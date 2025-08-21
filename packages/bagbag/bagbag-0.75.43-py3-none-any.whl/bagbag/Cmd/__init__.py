from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": [
        "TailOutput",
        "GetStatusOutput",
        "GetOutput",
        "Exist",
        "ContinuousSubprocess",
        "Where",
    ],
}

if TYPE_CHECKING:
    from .src import (
        TailOutput,
        GetStatusOutput,
        GetOutput,
        Exist,
        Where,
        ContinuousSubprocess,
    )
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


