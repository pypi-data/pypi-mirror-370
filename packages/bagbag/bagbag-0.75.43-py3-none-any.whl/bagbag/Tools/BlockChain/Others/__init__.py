from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "FearAndGreedIndex_src": ["FearAndGreedIndex"],
}

if TYPE_CHECKING:
    from .FearAndGreedIndex_src import FearAndGreedIndex
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )

