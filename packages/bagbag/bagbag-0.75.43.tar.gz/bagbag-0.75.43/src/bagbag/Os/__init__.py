
from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": [
        "Exit", 
        "System",
        "Mkdir",
        "ListDir",
        "ListFiles",
        "Getenv",
        "Getcwd",
        "Unlink",
        "Move",
        "Copy",
        "GetLoginUserName",
        "Walk",
        "GetUID",
        "Args",
        "GetCurrentThreadID",
        "Chdir",
        "Touch",
        "Stdin",
        "Stdout",
        "GetIPByInterface",
    ],
    "Path": ["Path"]
}

if TYPE_CHECKING:
    from .src import (
        Exit,
        System,
        Mkdir,
        ListDir,
        ListFiles,
        Getenv,
        Getcwd,
        Unlink,
        Move,
        Copy,
        GetLoginUserName,
        Walk,
        GetUID,
        Args,
        GetCurrentThreadID,
        Chdir,
        Touch,
        Stdin,
        Stdout,
        GetIPByInterface,
    )
    from . import Path
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


