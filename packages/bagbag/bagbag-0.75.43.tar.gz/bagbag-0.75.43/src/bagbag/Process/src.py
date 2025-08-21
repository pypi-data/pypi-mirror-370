import multiprocessing 

## print("load process")

class ProcessObj():
    def __init__(self, processobj:multiprocessing.Process) -> None:
        self.processobj = processobj 
    
    def Join(self):
        self.processobj.join()

    def IsAlive(self):
        """查看进程是否在运行"""
        return self.processobj.is_alive()

    def Kill(self):
        """Kill进程（直接kill，暴力kill，要保证一定能kill成功）"""
        self.processobj.kill()
        self.processobj.join()  # 确保进程已终止

class ProcessObjs():
    def __init__(self, processobjs:list[multiprocessing.Process]) -> None:
        self.processobjs = processobjs
    
    def Join(self):
        [i.join() for i in self.processobjs]
    
    def isAnyAlive(self):
        """查看是否有任何一个进程在运行"""
        return any(p.is_alive() for p in self.processobjs)

    def KillAll(self):
        """杀死所有进程"""
        for p in self.processobjs:
            p.kill()
        for p in self.processobjs:
            p.join()  # 确保所有进程已终止
    
    def GetProcesses(self) -> list[ProcessObj]:
        return [ProcessObj(i) for i in self.processobjs]

def Process(func, *args, count:int=1, **kwargs) -> ProcessObj | ProcessObjs:
    """
    注意调用这个函数的时候要放到if __name__ == "__main__"里面, 否则会报错
    """
    if count == 1:
        t = multiprocessing.Process(target=func, args=args, kwargs=kwargs)
        t.daemon = True 
        t.start()

        return ProcessObj(t)
    elif count > 1:
        ts = []
        for _ in range(count):
            t = multiprocessing.Process(target=func, args=args, kwargs=kwargs)
            t.daemon = True 
            t.start()

            ts.append(t)

        return ProcessObjs(ts)
    else:
        raise Exception("count异常")

    return p 

# import time 
# 
# def p(s:str, ss:str):
#     while True:
#         time.sleep(1)
#         print(s, ss, time.time())

if __name__ == "__main__":
    pass 
