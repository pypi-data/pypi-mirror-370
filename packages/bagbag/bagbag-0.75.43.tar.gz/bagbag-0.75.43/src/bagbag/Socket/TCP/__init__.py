from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": [
        "Connect", 
        "Listen",
        "PacketConnection",
        "StreamConnection"
    ],
}

if TYPE_CHECKING:
    from .src import (
        Listen,
        Connect,
        PacketConnection,
        StreamConnection
    )
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


