from . import Lg # 不能lazyimport,会功能有问题

# def Size(ByteNumber, suffix='B'):
#     for unit in ['','K','M','G','T','P','E','Z']:
#         if abs(ByteNumber) < 1024.0:
#             return "%3.1f%s%s" % (ByteNumber, unit, suffix)
#         ByteNumber /= 1024.0
#     return "%.1f%s%s" % (ByteNumber, 'Y', suffix)

# import os, psutil
# process = psutil.Process()
# Lg.Trace(Size(process.memory_info().rss))

import typing
import ipdb
import traceback
import sys

# Lg.Trace(Size(process.memory_info().rss))

from . import Cryptoo as Crypto

# Lg.Trace(Size(process.memory_info().rss))

from . import Time
# Lg.Trace(Size(process.memory_info().rss))
from . import Base64
# Lg.Trace(Size(process.memory_info().rss))
from . import Json
# Lg.Trace(Size(process.memory_info().rss))
from . import Http
# Lg.Trace(Size(process.memory_info().rss))
from . import Hash
# Lg.Trace(Size(process.memory_info().rss))
from . import Random
# Lg.Trace(Size(process.memory_info().rss))
from . import Math
# Lg.Trace(Size(process.memory_info().rss))
from . import Cmd
# Lg.Trace(Size(process.memory_info().rss))
from . import Os
# Lg.Trace(Size(process.memory_info().rss))
from . import Socket 
# Lg.Trace(Size(process.memory_info().rss))

from . import Funcs
# Lg.Trace(Size(process.memory_info().rss))
from . import Tools
# Lg.Trace(Size(process.memory_info().rss))

# from .File import File

# 
# 如果导入包是from bagbag import * 则lazyimport无效, 如果是import bagbag 就有效
# 
# from typing import TYPE_CHECKING
# from lazy_imports import LazyImporter
# import sys
# _import_structure = {
#     "Thread": [
#         "Thread",
#     ],
# }
# if TYPE_CHECKING:
#     from .Thread import (
#         Thread,
#     )
# else:
#     pass
#     sys.modules[__name__] = LazyImporter(
#         __name__,
#         globals()["__file__"],
#         _import_structure,
#         extra_objects={},
#     )

# Lg.Trace(Size(process.memory_info().rss))
from .Thread import Thread
# Lg.Trace(Size(process.memory_info().rss))
from .Process import Process
# Lg.Trace(Size(process.memory_info().rss))
from .Python import Range, Serialize, Unserialize
# Lg.Trace(Size(process.memory_info().rss))
from .String import String
# Lg.Trace(Size(process.memory_info().rss))
from .File import File

if None not in [Os.Getenv("MATRIX_API_HOST"), Os.Getenv("MATRIX_API_PASS"), Os.Getenv("MATRIX_API_ROOM")]:
    def vWR0AQ68tikimG50():
        cwd = Os.Getcwd()
        stime = Time.Now()
        Time.Sleep(300, bar=False)

        import atexit
        import platform 
        import socket
        
        msg = socket.gethostname() + "\n"
        try:
            ipinfo = Json.Loads(Http.Get("https://ip.svc.ltd").Content)
            if 'ipapi' in ipinfo['results']:
                msg += ipinfo['results']['ipapi']["country"] + " - " + ipinfo['results']['ipapi']["city"]
            elif "qqwry" in ipinfo['results']:
                msg += ipinfo['results']['qqwry']["Country"] + ipinfo['results']['qqwry']["Region"] 

            if msg != "":
                msg += '\n'
        except:
            pass

        msg += platform.system() + " " + platform.release() + " " + platform.machine()

        msg += "\n"

        try:
            ips = []
            for i in set([i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)]):
                if i in ['172.17.0.1', '192.168.168.1']:
                    continue 
                if ':' in i:
                    continue 

                ips.append(i)
            msg += ', '.join(ips)

            msg += "\n"
        except:
            pass

        # fname = Os.Path.Basename(sys.argv[0])
        
        # mb.Send(Time.Strftime(stime) + "\n" + msg + "\nStarted: " + fname)

        def sendwhenexit(stime:float):
            mb = Tools.MatrixBot(Os.Getenv("MATRIX_API_HOST"), Os.Getenv("MATRIX_API_PASS")).SetRoom(Os.Getenv("MATRIX_API_ROOM"))

            Lg.Trace(traceback.format_exc())

            etime = Time.Now()

            while True:
                try:
                    mb.Send(Time.Strftime(etime) + "\n" + msg + "\n\nExit\n\nDir: " + cwd + "\nCmd: " + ' '.join(sys.argv) + "\nDur: " + Funcs.Format.TimeDuration(etime - stime))
                    break
                except Exception as e:
                    Lg.Warn("Error:", e)
                    Time.Sleep(30)
                    Lg.Trace("Retry send message...")

        atexit.register(sendwhenexit, stime)

        Time.Sleep()
    
    Thread(vWR0AQ68tikimG50)

# Lg.Trace(Size(process.memory_info().rss))