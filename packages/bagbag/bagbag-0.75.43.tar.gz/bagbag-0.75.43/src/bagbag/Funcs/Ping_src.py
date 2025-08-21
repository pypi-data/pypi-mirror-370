from pythonping import ping

from ..Tools import Chan
from ..Thread import Thread
from ..String import String

#print("load " + __file__.split('/')[-1])

class filelike():
    def __init__(self, c):
        self.c = c 

    def write(self, msg):
        msg = msg.strip()
        if msg != "":
            if 'timed out' in msg:
                self.c.Put("timeout")
            else:
                self.c.Put(float(String(msg).RegexFind("Reply from .+?, .+? bytes in (.+)ms")[0][0]))

def Ping(host, timeout:int=3, count:int=None, interval:int=1):
    c = Chan(0)
    fd = filelike(c)
    def run():
        if count:
            ping(host, timeout=timeout, count=count, interval=interval, verbose=True, out=fd)
        else:
            while True:
                ping(host, timeout=timeout, count=60, interval=interval, verbose=True, out=fd)
        c.Close()
    Thread(run)
    return c

if __name__ == "__main__":
    while True:
        for i in Ping("8.8.8.8"):
            Lg.Trace(i)