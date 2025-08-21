from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": [
        "Range",
        "Serialize",
        "Unserialize"
    ],
}

if TYPE_CHECKING:
    from .src import (
        Range,
        Serialize,
        Unserialize
    )
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


