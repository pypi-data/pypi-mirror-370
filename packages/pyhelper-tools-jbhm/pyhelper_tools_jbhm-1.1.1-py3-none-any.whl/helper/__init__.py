from .core import *
from .submodules import *

__version__ ="1.1.1" 
__name__ = "pyhelper-tools-jbhm"

import inspect
from typing import Callable


def _get_all_functions():
    functions = {}

    from . import core

    for name, obj in inspect.getmembers(core):
        if inspect.isfunction(obj) and obj.__module__.startswith("helper.core"):
            functions[name] = obj

    from . import submodules

    for name, obj in inspect.getmembers(submodules):
        if inspect.isfunction(obj) and obj.__module__.startswith("helper.submodules"):
            functions[name] = obj

    return functions


ALL_FUNCTIONS = _get_all_functions()

_exported_names = set()

from .core import __all__ as core_all

_exported_names.update(core_all)

from .submodules import __all__ as submodules_all

_exported_names.update(submodules_all)

_other_exports = {
    "sys",
    "ast",
    "pd",
    "Path",
    "json",
    "csv",
    "ET",
    "sns",
    "mpl",
    "tk",
    "messagebox",
    "ScrolledText",
    "np",
    "plt",
    "re",
    "inspect",
    "asyncio",
    "time",
    "os",
    "filedialog",
}

_other_exports = _other_exports - _exported_names
_exported_names.update(_other_exports)

__all__ = sorted(_exported_names)