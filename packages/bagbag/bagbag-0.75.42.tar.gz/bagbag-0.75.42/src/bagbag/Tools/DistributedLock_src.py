from __future__ import annotations

# 配合如下server使用
# 
# version: '3'
# services:
#   lock_server:
#     image: darren2046/lock-server:lastest
#     container_name: lock-server
#     restart: always
#     #ports:
#     #   - "8888:8888" 
#     environment:
#       PASSWORD: password
#       DEBUG: "False"


#print("load " + '/'.join(__file__.split('/')[-2:]))

from .. import Time
from .. import Http
from ..Thread import Thread
from .. import Lg

class distributedLockLock():
    def __init__(self, lockserver:DistributedLock, lockname:str, timeout:int) -> None:
        self.lockserver = lockserver
        self.lockname = lockname 
        self.timeout = timeout
        self.islocked = False
        self.lockident:str = None

    def touch(self):
        errcount = 0
        while True:
            if self.timeout / 2 < 10:
                Time.Sleep(10, bar=False)
            elif self.timeout / 3 < 10:
                Time.Sleep(10, bar=False)
            elif self.timeout / 3 < 1:
                Time.Sleep(1)
            else:
                Time.Sleep(self.timeout / 3, bar=False)
            
            resp = Http.PostJson(self.lockserver.server + "/lock/touch", {
                "password": self.lockserver.password,
                "lockident": self.lockident,
                "lockname": self.lockname,
            }, timeout=5, timeoutRetryTimes=999999999)
            if resp.StatusCode != 200:
                errcount += 1
                if errcount >= 3:
                    raise Exception(str(resp.StatusCode) + ": " + resp.Content)

            if self.islocked == False:
                break
    
    def Acquire(self, block:bool=True, refresh:bool=False) -> bool:
        """
        It tries to acquire a lock.
        
        :param block: If the lock is already acquired, whether to wait for it to be released, defaults
        to True
        :type block: bool (optional)
        :param refresh: If set to True, the lock will be refreshed to make sure it will not timeout and acquire by others, defaults to False
        :type refresh: bool (optional)
        :return: A boolean value.
        """
        while True:
            while True:
                try:
                    resp = Http.PostJson(self.lockserver.server + "/lock/acquire", {
                        "password": self.lockserver.password,
                        "timeout": self.timeout,
                        "lockname": self.lockname,
                    }, timeout=5, timeoutRetryTimes=999999999)
                    break 
                except Exception as e:
                    Time.Sleep(1)
                    Lg.Warn("获取锁失败:", e)

            if resp.StatusCode == 200:
                self.lockident = resp.Content
                self.islocked = True
                if refresh == True:
                    Thread(self.touch)

                return True 
            elif resp.StatusCode == 202:
                if block == False:
                    return False 
                else:
                    Time.Sleep(self.lockserver.checkInterval)
            else:
                raise Exception(str(resp.StatusCode) + ": " + resp.Content)

    def Release(self):
        while True:
            try:
                resp = Http.PostJson(self.lockserver.server + "/lock/release", {
                    "password": self.lockserver.password,
                    "lockident": self.lockident,
                    "lockname": self.lockname,
                }, timeout=5, timeoutRetryTimes=999999999)
                break
            except Exception as e:
                Time.Sleep(1)
                Lg.Warn("释放锁失败:", e)

        if resp.StatusCode != 200:
            raise Exception(str(resp.StatusCode) + ": " + resp.Content)
        self.islocked = False

class DistributedLock():
    def __init__(self, server:str, password:str, checkInterval:int=5) -> None:
        """
        This function initializes the class with the server address, password, and check interval
        
        :param server: The URL of the server you want to connect to
        :type server: str
        :param password: The password to connect to server
        :type password: str
        :param checkInterval: How often to check for lock, defaults to 5
        :type checkInterval: int (optional)
        """
        self.server = server 
        self.password = password 
        self.checkInterval = checkInterval

        if not self.server.startswith("http://") and not self.server.startswith("https://"):
            self.server = "https://" + self.server
    
    def Lock(self, lockname:str, timeout:int=300) -> distributedLockLock:
        return distributedLockLock(self, lockname, timeout)

if __name__ == "__main__":
    lockserver = DistributedLock("http://localhost:8888", "abc")
    lock = lockserver.Lock("test_lock", timeout=30)
    count = 0
    # Lg.Trace('acquire')
    # lock.Acquire()

    def run():
        Lg.Trace("Started.")
        global count
        while True:
            lock.Acquire()
            print(count)
            count += 1
            lock.Release()
            if count > 30:
                break 
    
    Thread(run)
    Thread(run)
    
    Time.Sleep(35)