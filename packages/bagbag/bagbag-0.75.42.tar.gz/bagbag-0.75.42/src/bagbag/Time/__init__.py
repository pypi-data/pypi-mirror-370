from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": [
        "FormatDuration",
        "Sleep",
        "Strftime",
        "Strptime",
        "Now",
        "DailyTimeBetween",
        "NowString"
    ],
}

if TYPE_CHECKING:
    from .src import (
        FormatDuration,
        Sleep,
        Strftime,
        Strptime,
        Now,
        DailyTimeBetween,
        NowString
    )
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


