import os
import sys 
import re
import shutil
import os
from tqdm import tqdm
import typing
from .. import Lg

#print("load os")

Stdin = sys.stdin
Stdout = sys.stdout

def Touch(path:str):
    from pathlib import Path
    Path(path).touch()

def Chdir(path:str):
    os.chdir(path)

def Exit(num:int=0):
    sys.exit(num)

def System(cmd:str) -> int:
    import subprocess
    return subprocess.call(cmd, stderr=sys.stderr, stdout=sys.stdout, shell=True)

def Mkdir(*path:str):
    for p in path:
        os.makedirs(p, exist_ok=True)

def ListDir(path:str=".") -> list[str]:
    return os.listdir(path)

def ListFiles(path:str) -> list[str]:
    import glob
    return glob.glob(path)

Args = sys.argv 

def Getenv(varname:str, defaultValue:str=None) -> str | None:
    v = os.environ.get(varname)
    if not v:
        return defaultValue
    else:
        return v

def Getcwd() -> str:
    return os.getcwd()

def Unlink(path:str):
    import shutil
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)

def Move(src:str, dst:str, force:bool=True):
    import shutil
    if os.path.exists(dst):
        if not os.path.isdir(dst):
            if not force:
                raise Exception("目标已存在")
            else:
                os.unlink(dst)
        else:
            dst = os.path.join(dst, os.path.basename(src))

    ddir = os.path.dirname(dst)
    if ddir != "":
        if not os.path.exists(ddir):
            Mkdir(ddir)
    
    shutil.move(src, dst)

def Copy(src:str, dst:str, force:bool=False, show_progress:bool=True):
    """
    复制文件或目录。

    :param src: 源路径
    :param dst: 目标路径
    :param force: 是否覆盖目标文件或目录，默认为False
    :param show_progress: 是否显示进度条，默认为False
    """
    if os.path.exists(dst):
        if not os.path.isdir(dst):
            if not force:
                raise Exception("目标已存在")
            else:
                os.unlink(dst)
        else:
            dst = os.path.join(dst, os.path.basename(src))
    
    ddir = os.path.dirname(dst)
    if ddir != "":
        if not os.path.exists(ddir):
            Mkdir(ddir)

    # 如果源路径是文件
    if os.path.isfile(src):
        if show_progress:
            # 使用tqdm显示进度条
            with tqdm(total=os.path.getsize(src), unit='B', unit_scale=True, desc=f"Copying {src}") as pbar:
                def copy_with_progress(src, dst):
                    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                        while True:
                            buf = fsrc.read(1024)
                            if not buf:
                                break
                            fdst.write(buf)
                            pbar.update(len(buf))
                copy_with_progress(src, dst)
        else:
            shutil.copy2(src, dst)
    # 如果源路径是目录
    elif os.path.isdir(src):
        if show_progress:
            # 使用tqdm显示进度条
            for root, dirs, files in os.walk(src):
                for file in tqdm(files, desc=f"Copying {root}"):
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst, os.path.relpath(src_file, src))

                    if os.path.exists(dst_file) and force == False:
                        Lg.Trace("Exists:", dst_file)
                        continue 

                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    # shutil.copy2(src_file, dst_file)
                    with tqdm(total=os.path.getsize(src), unit='B', unit_scale=True, desc=f"Copying {src_file}") as pbar:
                        def copy_with_progress(src, dst):
                            with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                                while True:
                                    buf = fsrc.read(1024)
                                    if not buf:
                                        break
                                    fdst.write(buf)
                                    pbar.update(len(buf))
                        copy_with_progress(src_file, dst_file)
        else:
            shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        raise ValueError(f"源路径 {src} 既不是文件也不是目录。")

def GetLoginUserName() -> str:
    return os.getlogin()

def Walk(path:str, type:str=None) -> typing.Iterable[str]:
    """
    Walk through a directory and yield the names.
    
    :param path: The path to the directory you want to walk
    :type path: str
    :param type: The type of file you want to search for. "d" for directory and "f" for file, None(default) for all
    :type type: str
    """
    for root, dirs, files in os.walk(path, topdown=False):
        if type == None:
            for name in files:
                yield os.path.join(root, name)
            for name in dirs:
                yield os.path.join(root, name)
        elif type == "f":
            for name in files:
                yield os.path.join(root, name)
        elif type == "d":
            for name in dirs:
                yield os.path.join(root, name)

def GetUID() -> int:
    return os.getuid()

def GetCurrentThreadID() -> str:
    import threading
    import multiprocessing
    return multiprocessing.current_process().name.replace("Process-", "P").replace("MainProcess", "MP") + re.sub("\([a-zA-Z0-9]+\)", "", threading.current_thread().name.replace("Thread-", "T").replace(" ", "").replace("MainThread", "MT")) 

def GetIPByInterface(interface:str) -> str:
    import psutil
    import socket

    addrs = psutil.net_if_addrs()
    if interface in addrs:
        for addr in addrs[interface]:
            if addr.family == socket.AF_INET:  # 使用 socket.AF_INET
                return addr.address
            
    raise Exception("No IP address found for this interface")

if __name__ == "__main__":
    # Move("a", "b") # 移动当前目录的a到b
    # Move("b", "c/d/e") # 移动b到c/d/e, 会先递归创建目录c/d
    # Move("c/d/e", "d") # 移动c/d/e文件到d目录, 没有指定文件名就自动使用原来的文件名
    for i in Walk(".", type="d"):
        print(i)