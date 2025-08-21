# from .Opml import Opml, rssFeed
# from .Feed import Feed, rssPage

# class RSS:
#     Opml 
#     rssFeed
#     Feed 
#     rssPage

from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "Opml_src": [
        "Opml",
        "rssFeed"
    ], 
    "Feed_src": [
        "Feed",
        "rssPage"
    ], 
}

if TYPE_CHECKING:
    from .Opml_src import Opml, rssFeed
    from .Feed_src import Feed, rssPage
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


