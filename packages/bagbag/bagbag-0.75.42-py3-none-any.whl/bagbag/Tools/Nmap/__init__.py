from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "service_probes": [
        "ServiceProbes",
    ]
}

if TYPE_CHECKING:
    from .service_probes import (
        ServiceProbes,
    )
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )

