import threading 

## print("load Thread")

class ThreadObj():
    def __init__(self, threadobj:threading.Thread) -> None:
        self.threadobj = threadobj 
    
    def Join(self):
        self.threadobj.join()

class ThreadObjs():
    def __init__(self, threadobjs:list[threading.Thread]) -> None:
        self.threadobjs = threadobjs
    
    def Join(self):
        [i.join() for i in self.threadobjs]

def Thread(func, *args, count:int=1, **kwargs) -> ThreadObjs | ThreadObj:
    if count == 1:
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.daemon = True 
        t.start()

        return ThreadObj(t)
    elif count > 1:
        ts = []
        for _ in range(count):
            t = threading.Thread(target=func, args=args, kwargs=kwargs)
            t.daemon = True 
            t.start()

            ts.append(t)

        return ThreadObjs(ts)
    else:
        raise Exception("count异常")

if __name__ == "__main__":
    import time 

    def p(s:str, ss:str):
        while True:
            time.sleep(1)
            print(s, ss, time.time())

    t = Thread(p, "oo", "kk")

    while True:
        time.sleep(1)



