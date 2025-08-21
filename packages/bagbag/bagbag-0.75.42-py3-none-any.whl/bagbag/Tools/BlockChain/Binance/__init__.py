from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "OfficialAccountVertify": [
        "OfficialAccountVertify"
    ],
    "CoinsPrice_src": [
        "GetPrice"
    ]
}

if TYPE_CHECKING:
    from .CoinsPrice_src import GetPrice
    from .OfficialAccountVertify import OfficialAccountVertify
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


