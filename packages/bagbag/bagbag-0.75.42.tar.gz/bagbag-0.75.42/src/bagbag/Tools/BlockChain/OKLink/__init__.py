from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "API_src": [
        "API"
    ]
}

if TYPE_CHECKING:
    from .API_src import API
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


