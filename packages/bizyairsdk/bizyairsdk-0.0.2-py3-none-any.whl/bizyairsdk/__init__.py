import importlib
import pkgutil
import sys

__all__ = []
pkg = sys.modules[__name__]

for m in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
    mod = importlib.import_module(m.name)
    if hasattr(mod, "__all__"):
        for name in mod.__all__:
            setattr(pkg, name, getattr(mod, name))
        __all__.extend(mod.__all__)
