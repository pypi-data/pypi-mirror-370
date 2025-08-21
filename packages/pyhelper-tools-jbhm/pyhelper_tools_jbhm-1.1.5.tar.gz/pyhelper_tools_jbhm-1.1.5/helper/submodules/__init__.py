import os
import importlib
import inspect
from typing import Set, Dict, Any

_submodules_dir = os.path.dirname(__file__)

_EXCLUDED_FUNCTIONS = {}


def _is_exportable(name: str, obj: Any) -> bool:
    return (
        callable(obj)
        and not name.startswith("_")
        and name not in _EXCLUDED_FUNCTIONS
        and inspect.getmodule(obj) is not None
    )


_exported_functions: Dict[str, Any] = {}

for filename in os.listdir(_submodules_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        try:
            module = importlib.import_module(f".{module_name}", package=__package__)

            for name, obj in vars(module).items():
                if _is_exportable(name, obj):
                    _exported_functions[name] = obj

        except ImportError as e:
            print(f"Warning: Could not import module {module_name}: {str(e)}")
            continue

globals().update(_exported_functions)

__all__ = sorted(_exported_functions.keys())