from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": [
        "Md5sum",
        "Md5sumFile",
        "Sha256sum",
        "Sha256sumFile",
        "Sha1sum",
        "Sha1sumFile",
    ],
}

if TYPE_CHECKING:
    from .src import (
        Md5sum,
        Md5sumFile,
        Sha256sum,
        Sha256sumFile,
        Sha1sum,
        Sha1sumFile,
    )
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


