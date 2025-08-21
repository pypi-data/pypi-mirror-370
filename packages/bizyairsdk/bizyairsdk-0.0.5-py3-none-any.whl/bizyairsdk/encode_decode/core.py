import base64
import functools
import inspect
import io
import json
import logging
import pickle
import zlib
from functools import singledispatch
from typing import Any, Callable, List, Optional, Union

import numpy as np
import safetensors
import safetensors.torch
import torch
from loguru import logger
from PIL import Image

TENSOR_MARKER = "TENSOR:"
SAFETENSORS_MARKER = "SAFETENSORS_MARKER:"
IMAGE_MARKER = "IMAGE:"
NUMPY_MARKER = "NUMPY:"
ONLY_PICKLE_MARKER = "ONLY_PICKLE:"
DTYPE_MAP = {
    "float16": torch.float16,
    "float32": torch.float32,
    "bfloat16": torch.bfloat16,
    "uint8": torch.uint8,
}

MAAS_IMAGE_MARKER = "data:image/"


def pil2tensor(image: Image) -> torch.Tensor:
    # https://docs.comfy.org/custom-nodes/backend/snippets#save-an-image-batch
    image = np.array(image).astype(np.float32) / 255.0
    image = torch.from_numpy(image).unsqueeze(0)
    return image


@singledispatch
def contains_tensor(obj) -> bool:
    raise NotImplementedError(f"Unsupported type: {type(obj)}")


@contains_tensor.register(int)
@contains_tensor.register(float)
@contains_tensor.register(str)
@contains_tensor.register(bool)
@contains_tensor.register(type(None))
def _(obj, **kwargs):
    return False


@contains_tensor.register(list)
def _(obj: list) -> bool:
    return any(contains_tensor(item) for item in obj)


@contains_tensor.register(tuple)
def _(obj: tuple) -> bool:
    return any(contains_tensor(item) for item in obj)


@contains_tensor.register(dict)
def _(obj: dict) -> bool:
    return any(contains_tensor(value) for value in obj.values())


@contains_tensor.register(str)
def _(obj: str) -> bool:
    return obj.startswith(TENSOR_MARKER) or obj.startswith(IMAGE_MARKER)


@contains_tensor.register(torch.Tensor)
def _(obj: torch.Tensor) -> bool:
    return True


@contains_tensor.register(np.ndarray)
def _(obj: np.ndarray) -> bool:
    return False


def is_image_tensor(tensor, **kwargs) -> bool:
    """https://docs.comfy.org/essentials/custom_node_datatypes#image

    Check if the given tensor is in the format of an IMAGE (shape [B, H, W, C] where C=3).

    `Args`:
        tensor (torch.Tensor): The tensor to check.

    `Returns`:
        bool: True if the tensor is in the IMAGE format, False otherwise.
    """
    try:
        if not isinstance(tensor, torch.Tensor):
            return False

        if len(tensor.shape) != 4:
            return False

        B, H, W, C = tensor.shape
        if C != 3:
            return False

        return True
    except Exception:
        return False


def _new_encode_comfy_image(images: torch.Tensor, image_format="WEBP", **kwargs) -> str:
    """https://docs.comfy.org/essentials/custom_node_snippets#save-an-image-batch
    Encode a batch of images to base64 strings.

    Args:
        images (torch.Tensor): A batch of images.
        image_format (str, optional): The format of the images. Defaults to "WEBP".

    Returns:
        str: A JSON string containing the base64-encoded images.
    """
    results = {}
    for batch_number, image in enumerate(images):
        i = 255.0 * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        base64ed_image = encode_image_to_base64(img, format=image_format)
        results[batch_number] = base64ed_image
    return json.dumps(results)


def _new_decode_comfy_image(
    img_datas: str, image_format="WEBP", **kwargs
) -> torch.tensor:
    """
    Decode a batch of base64-encoded images.

    Args:
        img_datas (str): A JSON string containing the base64-encoded images.
        image_format (str, optional): The format of the images. Defaults to "WEBP".

    Returns:
        torch.Tensor: A tensor containing the decoded images.
    """
    img_datas = json.loads(img_datas)

    decoded_imgs = []
    for img_data in img_datas.values():
        decoded_image = decode_base64_to_np(img_data, format=image_format)
        decoded_image = np.array(decoded_image).astype(np.float32) / 255.0
        decoded_imgs.append(torch.from_numpy(decoded_image)[None,])

    return torch.cat(decoded_imgs, dim=0)


def _legacy_encode_comfy_image(image: torch.Tensor, image_format="png") -> str:
    input_image = image.cpu().detach().numpy()
    i = 255.0 * input_image[0]
    input_image = np.clip(i, 0, 255).astype(np.uint8)
    base64ed_image = encode_image_to_base64(
        Image.fromarray(input_image), format=image_format
    )
    return base64ed_image


def _legacy_decode_comfy_image(
    img_data: Union[List, str], image_format="png"
) -> torch.tensor:
    if isinstance(img_data, List):
        decoded_imgs = [decode_comfy_image(x, old_version=True) for x in img_data]

        combined_imgs = torch.cat(decoded_imgs, dim=0)
        return combined_imgs

    out = decode_base64_to_np(img_data, format=image_format)
    out = np.array(out).astype(np.float32) / 255.0
    output = torch.from_numpy(out)[None,]
    return output


def encode_comfy_image(
    image: torch.Tensor,
    image_format="WEBP",
    old_version=False,
    lossless=False,
    **kwargs,
) -> str:
    if old_version:
        return _legacy_encode_comfy_image(image, image_format)
    return _new_encode_comfy_image(image, image_format, lossless=lossless, **kwargs)


def decode_comfy_image(
    img_data: Union[List, str], image_format="WEBP", old_version=False, **kwargs
) -> torch.tensor:
    if old_version:
        return _legacy_decode_comfy_image(img_data, image_format)
    return _new_decode_comfy_image(img_data, image_format)


def convert_image_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def encode_image_to_base64(
    image: Image.Image,
    format: str = "WEBP",
    quality: int = 100,
    lossless=False,
    **kwargs,
) -> str:
    image = convert_image_to_rgb(image)
    with io.BytesIO() as output:
        image.save(output, format=format, quality=quality, lossless=lossless)
        output.seek(0)
        img_bytes = output.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")


def decode_base64_to_np(img_data: str, format: str = "WEBP", **kwargs) -> np.ndarray:
    img_bytes = base64.b64decode(img_data)
    with io.BytesIO(img_bytes) as input_buffer:
        img = Image.open(input_buffer)  # TODO: format passed in?
        img = img.convert("RGB")
    return np.array(img)


def decode_base64_to_image(
    img_data: str, format: str = "WEBP", **kwargs
) -> Image.Image:
    return Image.fromarray(decode_base64_to_np(img_data, format))


def numpy_to_base64(tensor_np: np.array, compress=True, **kwargs) -> str:
    tensor_bytes = pickle.dumps(tensor_np)

    if compress:
        tensor_bytes = zlib.compress(tensor_bytes)

    tensor_b64 = base64.b64encode(tensor_bytes).decode("utf-8")
    return tensor_b64


def tensor_to_base64(tensor: torch.Tensor, compress=True, **kwargs) -> str:
    tensor_np = tensor.cpu().detach().numpy()
    tensor_b64 = numpy_to_base64(tensor_np, compress=compress, **kwargs)
    return tensor_b64


def serialize_tensor_to_safetensors(tensor: torch.Tensor, **kwargs) -> dict:
    # https://github.com/huggingface/diffusers/blob/20e4b6a628c7e433f5805de49afc28f991c185c0/src/diffusers/utils/remote_utils.py#L369
    """
    Returns:
        dict: {'data': containing binary data , 'metadata': metadata}
    """
    image = tensor
    metadata = {}
    data = safetensors.torch._tobytes(image, "tensor")
    metadata["shape"] = list(image.shape)
    metadata["dtype"] = str(image.dtype).split(".")[-1]
    return {"data": data, "metadata": metadata, "__type__": "torch.Tensor"}


def deserialize_safetensors_to_tensor(data_dict: dict) -> torch.Tensor:
    metadata = data_dict["metadata"]
    output_tensor: bytes = data_dict["data"]

    # _parse_dtype
    torch_dtype = DTYPE_MAP[metadata["dtype"]]
    shape = metadata["shape"]

    output_tensor = torch.frombuffer(
        bytearray(output_tensor), dtype=torch_dtype
    ).reshape(shape)
    return output_tensor


def base64_to_numpy(tensor_b64: str, **kwargs) -> np.ndarray:
    tensor_bytes = base64.b64decode(tensor_b64)
    compress = kwargs.pop("compress", True)
    if compress:
        tensor_bytes = zlib.decompress(tensor_bytes)

    tensor_np = pickle.loads(tensor_bytes)
    return tensor_np


def safetensors_decode(data: str, **kwargs) -> torch.Tensor:
    data_dict = json.loads(data)
    tensor_bytes = base64.b64decode(data_dict["data"])
    tensor_bytes = _decompress_decoded_bytes(tensor_bytes, **kwargs)
    data_dict["data"] = tensor_bytes
    out_tensor = deserialize_safetensors_to_tensor(data_dict)
    return out_tensor


def base64_to_tensor(tensor_b64: str, **kwargs) -> torch.Tensor:
    tensor_np = base64_to_numpy(tensor_b64, **kwargs)
    tensor = torch.from_numpy(tensor_np)
    return tensor


@singledispatch
def decode_data(input, **kwargs):
    return input


@decode_data.register(int)
@decode_data.register(float)
@decode_data.register(bool)
@decode_data.register(type(None))
@decode_data.register(bytes)
@decode_data.register(torch.Tensor)
def _(input, **kwargs):
    return input


@decode_data.register(type(None))
def _(input, **kwargs):
    return [None]


@decode_data.register(dict)
def _(input, **kwargs):
    if "__type__" in input:
        if input["__type__"] == "torch.Tensor":
            return deserialize_safetensors_to_tensor(input)

    return {k: decode_data(v, **kwargs) for k, v in input.items()}


@decode_data.register(list)
@decode_data.register(tuple)
def _(input, **kwargs):
    return [decode_data(x, **kwargs) for x in input]


def maas_convert_base64_to_image(base64_str: str) -> Optional[Image.Image]:
    """
    Convert a prefixed Base64 string to a PIL Image object

    Args:
        base64_str: Base64 string with data prefix, format should be like data:image/webp;base64,XXXX

    Returns:
        PIL.Image.Image object or None (when parsing fails)
    """
    # Split metadata and encoded data
    header, encoded_data = base64_str.split(",", 1)

    # Extract image format
    image_format = header.split(";")[0]
    if image_format.lower() not in ["webp", "jpeg", "png", "gif"]:
        raise ValueError(f"Unsupported image format: {image_format}")

    # Base64 decoding
    decoded_data = base64.b64decode(encoded_data)

    # Create in-memory file object
    buffer = io.BytesIO(decoded_data)

    # Open image and verify integrity
    img = Image.open(buffer)
    img.verify()  # Verify file integrity

    # Reset buffer pointer and reopen (verify closes the stream)
    buffer.seek(0)
    return Image.open(buffer)


@decode_data.register(str)
def _(input_str: str, **kwargs):
    HANDLER_CONFIG = {
        TENSOR_MARKER: {"handler": base64_to_tensor},
        IMAGE_MARKER: {"handler": decode_comfy_image},
        NUMPY_MARKER: {"handler": base64_to_numpy},
        ONLY_PICKLE_MARKER: {"handler": _decode_only_pickle},
        SAFETENSORS_MARKER: {"handler": safetensors_decode},
        MAAS_IMAGE_MARKER: {"handler": maas_convert_base64_to_image},
    }

    for marker, config in HANDLER_CONFIG.items():
        if input_str.startswith(marker):
            data = input_str[len(marker) :]
            return config["handler"](data, **kwargs)
    return input_str


def _decode_only_pickle(data, **kwargs):
    decoded_bytes = _decompress_decoded_bytes(base64.b64decode(data), **kwargs)
    restored_data = pickle.loads(decoded_bytes)
    return restored_data


def _compress_serialized_bytes(serialized_bytes: bytes, **kwargs) -> bytes:
    compress = kwargs.pop("compress", True)
    algo = kwargs.pop("algorithm", "zlib")
    if compress:
        serialized_bytes = zlib.compress(serialized_bytes)
    return serialized_bytes


def _decompress_decoded_bytes(decoded_bytes: bytes, **kwargs) -> bytes:
    compress = kwargs.pop("compress", True)
    if compress:
        decoded_bytes = zlib.decompress(decoded_bytes)
    return decoded_bytes


def _encode_fallback(data, **kwargs) -> str:
    serialized_bytes = pickle.dumps(data)
    serialized_bytes = _compress_serialized_bytes(serialized_bytes, **kwargs)
    base64_str = base64.b64encode(serialized_bytes).decode("utf-8")
    return ONLY_PICKLE_MARKER + base64_str


@singledispatch
def encode_data(data, **kwargs) -> str:
    """
    Args:
        data: Encoded data.
        output_tensor_type: base64 or binary
        compress: Whether to compress the data (default: True).
        algorithm: Compression algorithm to use. Options are 'zstd' or 'zlib'. (default: zlib).
    """
    logging.warning(f"Unsupported type: {type(data)} Willing only pickle")
    return _encode_fallback(data, **kwargs)


@encode_data.register(dict)
def _(output, **kwargs):
    return {k: encode_data(v, **kwargs) for k, v in output.items()}


@encode_data.register(list)
@encode_data.register(tuple)
def _(output, **kwargs):
    return [encode_data(x, **kwargs) for x in output]


def safetensors_encode(data: torch.Tensor, **kwargs) -> str:
    data_dict = serialize_tensor_to_safetensors(data)
    serialized_bytes = _compress_serialized_bytes(data_dict["data"], **kwargs)
    data_dict["data"] = base64.b64encode(serialized_bytes).decode("utf-8")
    return json.dumps(data_dict)


@encode_data.register(torch.Tensor)
def _(output, **kwargs):
    if kwargs.get("output_tensor_type", "base64") == "binary":
        return serialize_tensor_to_safetensors(output, **kwargs)

    if output.dtype == torch.bfloat16:
        return SAFETENSORS_MARKER + safetensors_encode(output, **kwargs)

    if is_image_tensor(output):
        # https://docs.comfy.org/essentials/custom_node_snippets#save-an-image-batch
        return IMAGE_MARKER + encode_comfy_image(output, image_format="WEBP", **kwargs)
    return TENSOR_MARKER + tensor_to_base64(output, **kwargs)


@encode_data.register(int)
@encode_data.register(float)
@encode_data.register(str)
@encode_data.register(bool)
@encode_data.register(type(None))
def _(output, **kwargs):
    return output


@encode_data.register(np.ndarray)
def _(output, **kwargs):
    return NUMPY_MARKER + numpy_to_base64(output, **kwargs)


def auto_decode_encode(
    output_tensor_type: str = "binary",
    enable_decode: bool = True,
    enable_encode: bool = True,
) -> Callable:
    """
    Decorator factory to automatically handle data decoding/encoding for task functions.
    """

    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        is_method = len(params) > 0 and params[0].name == "self"

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper function that handles the actual data transformation
            """
            _args = list(args)
            self_arg = None
            # Decode input arguments
            # Decode arguments if enabled
            if enable_decode:
                if is_method and len(_args) > 0:
                    self_arg, *rest_args = _args
                    decoded_args = [self_arg] + [decode_data(arg) for arg in rest_args]
                else:
                    decoded_args = [decode_data(arg) for arg in _args]

                decoded_kwargs = {k: decode_data(v) for k, v in kwargs.items()}
            else:
                decoded_args = _args.copy()
                decoded_kwargs = kwargs.copy()
            # Execute original function with decoded arguments
            print(
                f"{func} {decoded_args=} {decoded_kwargs=} {enable_decode=} {enable_encode=}"
            )
            result = func(*decoded_args, **decoded_kwargs)

            # Encode result if enabled
            if enable_encode:
                return encode_data(result, output_tensor_type=output_tensor_type)
            else:
                return result

        return wrapper

    return decorator
