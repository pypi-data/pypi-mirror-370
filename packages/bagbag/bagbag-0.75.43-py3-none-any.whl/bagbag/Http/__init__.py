from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": [
        "Head",
        "Get",
        "PostRaw",
        "PostJson",
        "PostForm",
        "Delete",
        "PutForm",
        "PutRaw",
        "PutJson",
        "useragents",
        "Response",
    ],
}

if TYPE_CHECKING:
    from .src import (
        Head,
        Get,
        PostRaw,
        PostJson,
        PostForm,
        Delete,
        PutForm,
        PutRaw,
        PutJson,
        useragents,
        Response,
    )
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


