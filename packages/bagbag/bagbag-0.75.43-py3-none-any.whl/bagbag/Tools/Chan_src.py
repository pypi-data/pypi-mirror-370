import queue 
from typing import Any, Generic, TypeVar, Iterator
import time

_T = TypeVar("_T")

class ChannelException(Exception):
    pass 

class ChannelClosed(ChannelException):
    pass 

class ChannelNoNewItem(ChannelException):
    pass 

#print("load " + '/'.join(__file__.split('/')[-2:]))

# > A `Chan` is a thread-safe queue with a `Size` method
class Chan(Generic[_T]):
    def __init__(self, size=1) -> None:
        self.q = queue.Queue(maxsize=size)
        self.closed = False 
    
    def Size(self) -> int:
        """
        This function returns the size of the queue
        :return: The size of the queue
        """
        return self.q.qsize()
    
    def Get(self, block:bool=True, timeout:int=None) -> _T:
        """
        The function Get() returns the next item from the queue
        
        :param block: If True, the Get() method will block until an item is available. If False, it will
        return immediately with an exception if no item is available, defaults to True
        :type block: bool (optional)
        :param timeout: If the queue is empty, block for up to timeout seconds
        :type timeout: int
        :return: The get method returns the next item in the queue.
        """
        if self.q.qsize() == 0 and self.closed:
            raise ChannelClosed("Channel已关闭")
        else:
            if timeout:
                for _ in range(0, int(timeout/0.1)):
                    try:
                        item = self.q.get(block=False)
                        return item 
                    except queue.Empty:
                        time.sleep(0.1) 
                raise ChannelNoNewItem("没有新项目")
            else:
                while True:
                    try:
                        item = self.q.get(block=False)
                        return item 
                    except queue.Empty:
                        time.sleep(0.1)
                        pass 
                    if self.q.qsize() == 0 and self.closed:
                        raise ChannelClosed("Channel已关闭")

    def Put(self, item:_T, block:bool=True, timeout:int=None):
        """
        Put(self, item:Any, block:bool=True, timeout:int=None):
        
        :param item: The item to be put into the queue
        :type item: Any
        :param block: If True, the Put() method will block until the queue has space available. If
        False, it will raise a queue.Full exception if the queue is full, defaults to True
        :type block: bool (optional)
        :param timeout: If the optional argument timeout is not given or is None, block if necessary
        until an item is available. If the timeout argument is a positive number, it blocks at most
        timeout seconds and raises the Full exception if no item was available within that time.
        Otherwise (block is false), put an item on
        :type timeout: int
        """
        self.q.put(item, block=block, timeout=timeout)
    
    def Close(self):
        self.closed = True

    def __iter__(self) -> Iterator[_T]:
        while True:
            try:
                yield self.Get()
            except ChannelClosed:
                return 

if __name__ == "__main__":
    # 声明Queue里面内容的类型
    q:Chan[str] = Chan(10)

    # for _ in q:
    #     print(_)

    q.Put("0")
    s = q.Get() # (variable) s: str
    print(s)

    q.Put("1")
    q.Put("2")
    q.Put("3")

    def p():
        for i in q:
            print(i)
        print("chan关闭, 退出for循环")

    try:
        q.Get(timeout=1)
        q.Get(timeout=1)
        q.Get(timeout=1)
        q.Get(timeout=1)
    except Exception as e:
        print(e)
    
    q.Put("4")
    q.Put("5")
    q.Put("6")
    
    import threading 
    threading.Thread(target=p).start()

    import time
    time.sleep(1)

    # for _ in q:
    #     print(_)

    q.Close()