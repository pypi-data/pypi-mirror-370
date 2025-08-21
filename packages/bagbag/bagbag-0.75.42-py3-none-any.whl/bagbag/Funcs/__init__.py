from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "Wget_src": ["Wget"],
    "IP_src": ["Int2IP", "IP2Int", "GetPublicIP", "GetIPRangeByCIDR", "GetIPCountByCIDR"],
    "ResizeImage_src": ["ResizeImage", "ConvertImageFormate"],
    "Ping_src": ["Ping"],
    # "CutSentence_src": ["CutSentence"],
    "UUID_src": ["UUID", "UUID_Full"],
    # "Markdown_src": ["Markdown2Html", "Html2Markdown"],
    "FakeIdentity_src": ["FakeIdentity"],
    "VersionCompare_src": ["VersionCompare"],
    "Whois_src": ['DomainWhois', "IPWhois"],
    "ChromeExtension_src": ['ChromeExtensionDownload', 'ChromeExtensionInfomation'],
    "MarkCoordinatesOnMap_src": ['MarkCoordinatesOnMap'],
    "CountryNameConvert_src": ["CountryToAbbrev", "AbbrevToCountry"]
}

if TYPE_CHECKING:
    from .MarkCoordinatesOnMap_src import MarkCoordinatesOnMap
    from .Wget_src import Wget
    from .IP_src import Int2IP, IP2Int, GetPublicIP, GetIPRangeByCIDR, GetIPCountByCIDR
    from .ResizeImage_src import ResizeImage, ConvertImageFormate
    from .Ping_src import Ping
    # from .CutSentence_src import CutSentence
    from .UUID_src import UUID, UUID_Full
    # from .Markdown_src import Markdown2Html, Html2Markdown
    # from .FileType import FileType
    from .FakeIdentity_src import FakeIdentity
    from .VersionCompare_src import VersionCompare
    from .Whois_src import DomainWhois, IPWhois
    from .ChromeExtension_src import ChromeExtensionDownload, ChromeExtensionInfomation
    from .CountryNameConvert_src import CountryToAbbrev, AbbrevToCountry
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )

from . import Format


