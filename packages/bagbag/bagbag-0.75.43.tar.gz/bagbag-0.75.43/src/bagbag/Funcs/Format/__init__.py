from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": ["Size", "TimeDuration", "PrettyJson"],
}

if TYPE_CHECKING:
    from .src import (Size, TimeDuration, PrettyJson)
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


