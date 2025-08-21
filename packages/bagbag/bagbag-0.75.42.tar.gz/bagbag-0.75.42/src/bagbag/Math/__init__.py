from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": ["C10to62", "C62to10"],
}

if TYPE_CHECKING:
    from .src import (
        C10to62,
        C62to10,
    )
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


