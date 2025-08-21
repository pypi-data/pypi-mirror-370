from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": [
        "Int",
        "Choice", 
        "String",
        "Shuffle"
    ],
}

if TYPE_CHECKING:
    from .src import (
        Int,
        Choice,
        String,
        Shuffle
    )
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


