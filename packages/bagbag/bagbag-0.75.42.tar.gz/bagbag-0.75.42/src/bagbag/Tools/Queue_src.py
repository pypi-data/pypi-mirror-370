# 需要配合以下服务器食用
#
# version: '3'
# services:
#   queue_server:
#     image: darren2046/queue-server:0.0.24
#     container_name: queue-server
#     restart: always
#     #ports:
#     #   - "8080:8080" 
#     environment:
#       # 支持3种backend
#       # REDIS_HOST: "192.168.1.5"
#       # REDIS_PORT: 
#       # REDIS_DB:
#       # REDIS_PASSWORD: 

#       MYSQL_HOST: "192.168.1.5"
#       # MYSQL_PORT:
#       # MYSQL_USER:
#       # MYSQL_PASSWORD: 
#       MYSQL_DATABASE: "queue"

#       # SQLITE_PATH: /data/queue.db

#     # volumes:
#     #   - /data/cr-volumes/queue-server/data:/data
    
#print("load " + '/'.join(__file__.split('/')[-2:]))

from .. import Http
from .. import Base64
from .. import Lg

import typing
import pickle

class queueQueueConfirm():
    def __init__(self, server:str, name:str, length:int=0, timeout:int=300) -> None:
        self.server = server 
        self.name = name 
        Http.PostForm(self.server + "/newQueueConfirm", {"qname": self.name, "length": length, "timeout": timeout})
    
    def Put(self, item:typing.Any, force:bool=False):
        while True:
            res = Http.PostForm(self.server + "/put", {"qname": self.name, "value": Base64.Encode(pickle.dumps(item, 2)), "force": str(force)})

            if res.StatusCode == 200:
                break 

    def Get(self) -> typing.Tuple[str, typing.Any]:
        while True:
            res = Http.Get(self.server + "/get", {"qname": self.name}, Timeout=900)
            # Lg.Trace(res)

            if res.StatusCode == 200:
                tid = res.Headers["Tid"]
                value = pickle.loads(Base64.Decode(res.Content))

                return tid, value 
    
    def Done(self, tid:str):
        Http.Get(self.server + "/done", {"qname": self.name, "tid": tid})
    
    def Size(self) -> int:
        res = Http.Get(self.server + "/size", {"qname": self.name})
        return int(res.Content)

class Queue():
    def __init__(self, server:str) -> None:
        self.server = server 
    
    def QueueConfirm(self, name:str, length:int=0, timeout:int=300) -> queueQueueConfirm:
        return queueQueueConfirm(self.server, name, length, timeout)

if __name__ == "__main__":
    qs = Queue("http://192.168.1.230:8080")
    qt = qs.QueueConfirm("test", 100, 10)
    Lg.Trace("put value")
    for i in range(200):
        Lg.Trace("put", i)
        qt.Put({1:i})
    for i in range(10):
        Lg.Trace("Get value")
        res = qt.Get()
        tid, value = res
        Lg.Trace(res)
        size = qt.Size()
        Lg.Trace(size)
        qt.Done(tid)