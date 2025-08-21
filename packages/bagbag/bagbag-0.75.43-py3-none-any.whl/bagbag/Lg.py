import sys as __sys
from loguru import logger
import inspect
import os
import threading 
import multiprocessing
import re

pformat = (lambda a:lambda v,t="    ",n="\n",i=0:a(a,v,t,n,i))(lambda f,v,t,n,i:"{%s%s%s}"%(",".join(["%s%s%s: %s"%(n,t*(i+1),repr(k),f(f,v[k],t,n,i+1))for k in v]),n,(t*i)) if type(v)in[dict] else (type(v)in[list]and"[%s%s%s]"or"(%s%s%s)")%(",".join(["%s%s%s"%(n,t*(i+1),f(f,k,t,n,i+1))for k in v]),n,(t*i)) if type(v)in[list,tuple] else repr(v))
logformat = '<green>{time:MM-DD HH:mm:ss}</green> <level>{level:4.4}</level> {message}'

__config = {
    "handlers": [
        {
            "sink": __sys.stdout, 
            # "format": "{time:MM-DD HH:mm:ss} [{icon}] {message}",
            "format": logformat,
            "level": "TRACE",
        },
        # {"sink": "file.log", "serialize": True},
    ],
    # "extra": {"user": "someone"}
}
logger.configure(**__config)

def Trace(*message):
    messages = []
    jstr = " "
    # 如果第一个参数包含 %，则进行格式化处理
    if len(message) > 1 and isinstance(message[0], str) and '%' in message[0]:
        try:
            # 尝试格式化字符串
            formatted_msg = message[0] % tuple(pformat(msg) if isinstance(msg, (list, dict, set)) else msg for msg in message[1:])
            messages.append(formatted_msg)
        except TypeError as e:
            # 如果格式化失败，记录原始消息
            messages.append(str(message[0]))
            messages.extend(str(msg) for msg in message[1:])
    else:
        # 原有逻辑处理非格式化字符串
        for msg in message:
            if isinstance(msg, (int, float)):
                msg = str(msg)
            if isinstance(msg, (list, dict, set)):
                msg = pformat(msg)
                if msg.count("\n") != 0 and jstr == " ":
                    jstr = "\n"
            else:
                msg = str(msg)
            if str(msg).count("\n") != 0 and jstr == " ":
                jstr = "\n"
            messages.append(msg)
    
    p = inspect.stack()[1]

    logger.opt(ansi=True).trace(
        "<cyan>{pname}</cyan>:<cyan>{tname}</cyan>:<cyan>{filename}</cyan>:<cyan>{line}</cyan> <level>{message}</level>", 
        message=jstr.join(messages), 
        function=p.function.replace("<module>", "None"),
        line=p.lineno,
        filename=os.path.basename(p.filename),
        # tid=threading.get_native_id()
        # tid=threading.get_ident(),
        tname=re.sub("\([a-zA-Z0-9]+\)", "", threading.current_thread().name.replace("Thread-", "T").replace(" ", "").replace("MainThread", "MT")),
        pname=multiprocessing.current_process().name.replace("Process-", "P").replace("MainProcess", "MP"),
    )

def Debug(*message):
    messages = []
    jstr = " "
    # 如果第一个参数包含 %，则进行格式化处理
    if len(message) > 1 and isinstance(message[0], str) and '%' in message[0]:
        try:
            # 尝试格式化字符串
            formatted_msg = message[0] % tuple(pformat(msg) if isinstance(msg, (list, dict, set)) else msg for msg in message[1:])
            messages.append(formatted_msg)
        except TypeError as e:
            # 如果格式化失败，记录原始消息
            messages.append(str(message[0]))
            messages.extend(str(msg) for msg in message[1:])
    else:
        # 原有逻辑处理非格式化字符串
        for msg in message:
            if isinstance(msg, (int, float)):
                msg = str(msg)
            if isinstance(msg, (list, dict, set)):
                msg = pformat(msg)
                if msg.count("\n") != 0 and jstr == " ":
                    jstr = "\n"
            else:
                msg = str(msg)
            if str(msg).count("\n") != 0 and jstr == " ":
                jstr = "\n"
            messages.append(msg)
    
    p = inspect.stack()[1]
    
    logger.opt(ansi=True).debug(
        "<cyan>{pname}</cyan>:<cyan>{tname}</cyan>:<cyan>{filename}</cyan>:<cyan>{line}</cyan> <level>{message}</level>", 
        message=jstr.join(messages), 
        function=p.function.replace("<module>", "None"),
        line=p.lineno,
        filename=os.path.basename(p.filename),
        # tid=threading.get_native_id()
        # tid=threading.get_ident(),
        tname=re.sub("\([a-zA-Z0-9]+\)", "", threading.current_thread().name.replace("Thread-", "T").replace(" ", "").replace("MainThread", "MT")),
        pname=multiprocessing.current_process().name.replace("Process-", "P").replace("MainProcess", "MP"),
    )

def Info(*message):
    messages = []
    jstr = " "
    # 如果第一个参数包含 %，则进行格式化处理
    if len(message) > 1 and isinstance(message[0], str) and '%' in message[0]:
        try:
            # 尝试格式化字符串
            formatted_msg = message[0] % tuple(pformat(msg) if isinstance(msg, (list, dict, set)) else msg for msg in message[1:])
            messages.append(formatted_msg)
        except TypeError as e:
            # 如果格式化失败，记录原始消息
            messages.append(str(message[0]))
            messages.extend(str(msg) for msg in message[1:])
    else:
        # 原有逻辑处理非格式化字符串
        for msg in message:
            if isinstance(msg, (int, float)):
                msg = str(msg)
            if isinstance(msg, (list, dict, set)):
                msg = pformat(msg)
                if msg.count("\n") != 0 and jstr == " ":
                    jstr = "\n"
            else:
                msg = str(msg)
            if str(msg).count("\n") != 0 and jstr == " ":
                jstr = "\n"
            messages.append(msg)
    
    p = inspect.stack()[1]
    
    logger.opt(ansi=True).info(
        "<cyan>{pname}</cyan>:<cyan>{tname}</cyan>:<cyan>{filename}</cyan>:<cyan>{line}</cyan> <level>{message}</level>", 
        message=jstr.join(messages), 
        function=p.function.replace("<module>", "None"),
        line=p.lineno,
        filename=os.path.basename(p.filename),
        # tid=threading.get_native_id()
        # tid=threading.get_ident(),
        tname=re.sub("\([a-zA-Z0-9]+\)", "", threading.current_thread().name.replace("Thread-", "T").replace(" ", "").replace("MainThread", "MT")),
        pname=multiprocessing.current_process().name.replace("Process-", "P").replace("MainProcess", "MP"),
    )

def Warn(*message):
    messages = []
    jstr = " "
    # 如果第一个参数包含 %，则进行格式化处理
    if len(message) > 1 and isinstance(message[0], str) and '%' in message[0]:
        try:
            # 尝试格式化字符串
            formatted_msg = message[0] % tuple(pformat(msg) if isinstance(msg, (list, dict, set)) else msg for msg in message[1:])
            messages.append(formatted_msg)
        except TypeError as e:
            # 如果格式化失败，记录原始消息
            messages.append(str(message[0]))
            messages.extend(str(msg) for msg in message[1:])
    else:
        # 原有逻辑处理非格式化字符串
        for msg in message:
            if isinstance(msg, (int, float)):
                msg = str(msg)
            if isinstance(msg, (list, dict, set)):
                msg = pformat(msg)
                if msg.count("\n") != 0 and jstr == " ":
                    jstr = "\n"
            else:
                msg = str(msg)
            if str(msg).count("\n") != 0 and jstr == " ":
                jstr = "\n"
            messages.append(msg)
    
    p = inspect.stack()[1]
    
    logger.opt(ansi=True).warning(
        "<cyan>{pname}</cyan>:<cyan>{tname}</cyan>:<cyan>{filename}</cyan>:<cyan>{line}</cyan> <level>{message}</level>", 
        message=jstr.join(messages), 
        function=p.function.replace("<module>", "None"),
        line=p.lineno,
        filename=os.path.basename(p.filename),
        # tid=threading.get_native_id()
        # tid=threading.get_ident(),
        tname=re.sub("\([a-zA-Z0-9]+\)", "", threading.current_thread().name.replace("Thread-", "T").replace(" ", "").replace("MainThread", "MT")),
        pname=multiprocessing.current_process().name.replace("Process-", "P").replace("MainProcess", "MP"),
    )

def Error(*message, exc:bool=True):
    """
    It logs the error message with the file name, line number, thread name, and process name.
    
    :param exc: If True, the exception will be logged, defaults to False
    :type exc: bool (optional)
    """
    messages = []
    jstr = " "
    # 如果第一个参数包含 %，则进行格式化处理
    if len(message) > 1 and isinstance(message[0], str) and '%' in message[0]:
        try:
            # 尝试格式化字符串
            formatted_msg = message[0] % tuple(pformat(msg) if isinstance(msg, (list, dict, set)) else msg for msg in message[1:])
            messages.append(formatted_msg)
        except TypeError as e:
            # 如果格式化失败，记录原始消息
            messages.append(str(message[0]))
            messages.extend(str(msg) for msg in message[1:])
    else:
        # 原有逻辑处理非格式化字符串
        for msg in message:
            if isinstance(msg, (int, float)):
                msg = str(msg)
            if isinstance(msg, (list, dict, set)):
                msg = pformat(msg)
                if msg.count("\n") != 0 and jstr == " ":
                    jstr = "\n"
            else:
                msg = str(msg)
            if str(msg).count("\n") != 0 and jstr == " ":
                jstr = "\n"
            messages.append(msg)
    
    p = inspect.stack()[1]
    
    if exc:
        logger.opt(ansi=True).exception(
            "<cyan>{pname}</cyan>:<cyan>{tname}</cyan>:<cyan>{filename}</cyan>:<cyan>{line}</cyan> <level>{message}</level>", 
            message=jstr.join(messages), 
            function=p.function.replace("<module>", "None"),
            line=p.lineno,
            filename=os.path.basename(p.filename),
            # tid=threading.get_native_id()
            # tid=threading.get_ident(),
            tname=re.sub("\([a-zA-Z0-9]+\)", "", threading.current_thread().name.replace("Thread-", "T").replace(" ", "").replace("MainThread", "MT")),
            pname=multiprocessing.current_process().name.replace("Process-", "P").replace("MainProcess", "MP"),
        )
    else:
        logger.opt(ansi=True).error(
            "<cyan>{pname}</cyan>:<cyan>{tname}</cyan>:<cyan>{filename}</cyan>:<cyan>{line}</cyan> <level>{message}</level>", 
            message=jstr.join(messages), 
            function=p.function.replace("<module>", "None"),
            line=p.lineno,
            filename=os.path.basename(p.filename),
            # tid=threading.get_native_id()
            # tid=threading.get_ident(),
            tname=re.sub("\([a-zA-Z0-9]+\)", "", threading.current_thread().name.replace("Thread-", "T").replace(" ", "").replace("MainThread", "MT")),
            pname=multiprocessing.current_process().name.replace("Process-", "P").replace("MainProcess", "MP"),
        )

def SetLevel(level: str):
    """
    It sets the logging level of the logger to the level passed in
    
    :param level: The level of messages to log. canbe: trace,debug,info,warn,error
    :type level: str
    """
    for idx in range(len(__config['handlers'])):
        __config['handlers'][idx]['level'] = level.upper()

    logger.configure(**__config)

def SetStdout(enable:bool):
    if enable == False:
        handlers = []
        for idx in range(len(__config['handlers'])):
            if __config['handlers'][idx]['sink'] != __sys.stdout:
                handlers.append(__config['handlers'][idx])
        
        __config['handlers'] = handlers
    else:
        if __sys.stdout not in [i["sink"] for i in __config['handlers']]:
            handler = {
                "sink": __sys.stdout, 
                "format": logformat,
                "level": "TRACE",
            }
            __config['handlers'].append(handler)

    logger.configure(**__config)

def SetFile(path:str, size:int=100, during:int=7, color:bool=True, json:bool=False):
    """
    It sets the file handler for the logger.
    
    :param path: The path to the log file
    :type path: str
    :param size: The size of the file before it rotates, in MB
    :type size: int
    :param during: how long to keep the log file, in Hour
    :type during: int
    :param color: If True, the output will be colorized, defaults to True
    :type color: bool (optional)
    :param json: If True, the log records will be serialized to JSON, defaults to False
    :type json: bool (optional)
    """
    if '/' in path.strip("/") and not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path.strip('/')))

    if path not in [i["sink"] for i in __config['handlers']]:
        handler = {
            "sink": path,
            "rotation": str(size)+" MB", 
            "retention": str(during)+" hours", 
            "format": logformat,
            "level": __config['handlers'][0]['level'] if len(__config['handlers']) > 0 else "TRACE",
            "colorize": color,
            "serialize": json,
        }
        __config['handlers'].append(handler)
        logger.configure(**__config)

# import time 

# def ff():    
#     def f():
#         while True:
#             time.sleep(1)
#             Trace(time.time())

#     t = threading.Thread(target=f)
#     t.daemon = True 
#     t.start()

#     time.sleep(99999)

if __name__ == "__main__":
    # SetLevel("info")
    # SetFile("test.log", 1, 1, json=True)
    Trace(True)
    Trace("trace")
    Debug("debug")
    Info("info")
    Warn("warn")
    Warn(False)
    Error("error")
    Debug("text debug message", [ ['spam', 'eggs', 'lumberjack', 'knights', 'ni'], 'spam', 'eggs', 'lumberjack', 'knights', 'ni'])
    Trace("text debug message", [ ['spam', 'eggs', 'lumberjack', 'knights', 'ni'], 'spam', 'eggs', 'lumberjack', 'knights', 'ni'])
    Debug("first", "second", "third")
    Trace("初始化实例", 1)
    try:
        int("2.3")
    except:
        Error("转换错误:", True)

    
    # p = multiprocessing.Process(target=ff)
    # #p.daemon = True 
    # p.start()

    # time.sleep(99999)
