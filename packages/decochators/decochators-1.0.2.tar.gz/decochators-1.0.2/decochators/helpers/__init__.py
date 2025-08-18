import inspect
import importlib

__all__ = []

def _import_with_suffix(module_name: str, suffix: str):
    mod = importlib.import_module(f".{module_name}", package=__name__)
    for name, obj in inspect.getmembers(mod, inspect.isfunction):
        globals()[f"{name}_{suffix}"] = obj
        __all__.append(f"{name}_{suffix}")

_import_with_suffix("core_1d", "1d")
_import_with_suffix("core_3d", "3d")
