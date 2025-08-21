# from .Elevated import Elevated
# from .Essential import Essential
# from .Elevated import twitterTweet as ElevatedTweet

from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "Elevated_src": [
        "Elevated",
        "ElevatedTweet",
        "ElevatedTwitterUser"
    ], 
    "Essential_src": [
        "Essential"
    ], 
    "Browser_src": [
        "Browser",
        "BrowserTwitterUser"
    ],
    "Utils": [
        "Utils"
    ],
    "Nitter_src": [
        "Nitter",
        "NitterTweet", 
        "NitterTwitterUser"
    ]
}

if TYPE_CHECKING:
    from .Elevated_src import (
        Elevated,
        ElevatedTweet,
        ElevatedTwitterUser,
    )
    from .Essential_src import Essential
    from .Browser_src import Browser, BrowserTwitterUser
    from .Nitter_src import Nitter, NitterTweet, NitterTwitterUser
    from . import Utils
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


