from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "Tron": ["Tron"],
    "Binance": ["Binance"],
    "CoinMarketCap": ['CoinMarketCap'], 
    "OKLink": ['OKLink'],
    "Others": ["Others"]
}

if TYPE_CHECKING:
    from . import Tron
    from . import Binance
    from . import CoinMarketCap
    from . import Others
    from . import OKLink
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )

