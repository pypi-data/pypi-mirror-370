from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "Ratelimit_src": ["RateLimit"],
    "Redis_src": ["Redis", "RedisQueue", "RedisQueueConfirm", "redisKey", "redisNamespaced"],
    "ProgressBar_src": ["ProgressBar"],
    "Telegram_src": ["Telegram", "TelegramPeer", "TelegramMessage"],
    "Lock_src": ["Lock"],
    "Database": [
        "SQLite",
        "MySQL",
        "mySQLSQLiteKeyValueTable",
        "mySQLSQLiteTable",
        "mySQLSQLiteQueue",
        "mySQLSQLiteConfirmQueue"
    ],
    "URL_src": ["URL"],
    "Chan_src": ["Chan", "ChannelNoNewItem"],
    "WebServer_src": ["WebServer"],
    "TelegramBotOfficial_src": ["TelegramBotOfficial"],
    "TelegramBot_src": ["TelegramBot"],
    "Argparser_src": ["Argparser"],
    "Elasticsearch_src": ["Elasticsearch"],
    "Crontab_src": ["Crontab"],
    "WaitGroup_src": ["WaitGroup"],
    # from . import Xlsx
    "Xlsx": ["Xlsx"],
    "XPath_src": ["XPath"],
    # from . import Translater
    "Translater": ["Translater"],
    "SSH_src": ["SSH"],
    "Github_src": ["Github"],
    "Kafka_src": ["Kafka", "kafkaProducer", "kafkaConsumer", "kafkaQueue"],
    "Queue_src": ["Queue"],
    # from . import RSS
    "RSS": ["RSS"],
    "MatrixBot_src": ["MatrixBot"],
    "Nslookup_src": ["Nslookup"],
    # from . import Twitter
    "Twitter": ["Twitter"],
    "DistributedLock_src": ["DistributedLock"],
    # from . import BlockChain
    "BlockChain": ["BlockChain"], 
    "JavaScript": ["JavaScript"],
    # from . import ComputerVision
    "ComputerVision": ["ComputerVision"],
    "WebCrawler_src": ["WebCrawler"],
    "OCR_src": ["OCR"],
    # "File_src": ["File"],
    # "Selenium": ["Selenium", "SeleniumFlow", "SeleniumElement"],
    "Selenium": ["Selenium", "SeleniumElement"],
    "CSV": ["CSV"],
    "OpenAI": ["OpenAI"],
    "Prometheus": ['Prometheus'],
    "Cache": ["Cache"],
    "TextClassifier": ["TextClassifier"],
    "SMTP_src": ['SMTP'],
    "FlashPoint_src": ['FlashPoint'],
    "Nmap": ["Nmap"],
    "Draw": ['Draw'],
    "VNC_src": ['VNC'],
    "Mitmproxy_src": ["Mitmproxy"],
    "ZIP_src": ["ZIP"],
    "Mongodb_src": ["MongoDB"],
}

if TYPE_CHECKING:
    from .Mongodb_src import MongoDB
    from .ZIP_src import ZIP
    from . import Nmap
    # from ..File_src import File
    from .FlashPoint_src import FlashPoint
    from .SMTP_src import SMTP
    from .Redis_src import Redis, RedisQueue, RedisQueueConfirm, redisKey, redisNamespaced
    from .Database import SQLite, MySQL, mySQLSQLiteKeyValueTable, mySQLSQLiteTable,mySQLSQLiteQueue, mySQLSQLiteConfirmQueue
    from .ProgressBar_src import ProgressBar
    from .Telegram_src import Telegram, TelegramPeer, TelegramMessage
    from . import Cache
    from . import CSV
    from . import OpenAI
    from . import Selenium
    from . import TextClassifier
    from .Lock_src import Lock
    from . import Prometheus
    from .URL_src import URL
    from .Ratelimit_src import RateLimit
    from .Chan_src import Chan, ChannelNoNewItem
    from .WebServer_src import WebServer
    from .TelegramBotOfficial_src import TelegramBotOfficial
    from .TelegramBot_src import TelegramBot
    from .Argparser_src import Argparser
    from .Elasticsearch_src import Elasticsearch
    from .Crontab_src import Crontab
    from .WaitGroup_src import WaitGroup
    from . import Xlsx
    from .XPath_src import XPath
    from . import Translater
    from .SSH_src import SSH
    # from .TelegramAsync import TelegramAsync
    from .Github_src import Github
    from .Kafka_src import Kafka, kafkaProducer, kafkaConsumer, kafkaQueue
    from .Queue_src import Queue
    from . import RSS
    from .MatrixBot_src import MatrixBot
    from .Nslookup_src import Nslookup
    from . import Twitter
    from .DistributedLock_src import DistributedLock
    # from .Test import Test
    from . import BlockChain
    from .JavaScript_src import JavaScript
    from .ComputerVision import ComputerVision
    from .WebCrawler_src import WebCrawler
    from .OCR_src import OCR
    from . import Draw
    from .VNC_src import VNC
    from .Mitmproxy_src import Mitmproxy
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


