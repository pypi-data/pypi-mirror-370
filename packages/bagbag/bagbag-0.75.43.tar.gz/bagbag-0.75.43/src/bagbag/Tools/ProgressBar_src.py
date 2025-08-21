import tqdm

#print("load " + '/'.join(__file__.split('/')[-2:]))

class ProgressBar():
    def __init__(self, iterable_obj=None, total=None, title=None, leave=False, smoothing:float=0.3, initial:int=0):
        """
        The function initializes a progress bar object with various parameters.
        
        :param iterable_obj: The `iterable_obj` parameter is used to pass an iterable object, such as a
        list or a generator, to the `__init__` method. This object will be iterated over and progress
        will be displayed using the `tqdm` library
        :param total: The `total` parameter represents the total number of iterations that will be
        performed. It is used to calculate the progress percentage and estimate the remaining time. If
        the `total` parameter is not provided or is set to `None`, the progress bar will not display the
        progress percentage or estimate the remaining time
        :param title: The `title` parameter is used to set the description of the progress bar. It is a
        string that provides a brief summary or title for the progress being tracked
        :param leave: The `leave` parameter is used to determine whether the progress bar should remain
        visible after the iteration is complete. If `leave` is set to `True`, the progress bar will
        remain visible. If `leave` is set to `False`, the progress bar will be removed after the
        iteration is complete, defaults to False (optional)
        :param smoothing: Exponential moving average smoothing factor for speed estimates (ignored in GUI mode). 
        Ranges from 0 (average speed) to 1 (current/instantaneous speed) [default: 0.3].
        :type smoothing: float
        :param initial: The `initial` parameter is used to set the initial value of the progress bar. It
        determines the starting point of the progress bar. By default, it is set to 0, defaults to 0
        :type initial: int (optional)
        """
        self.iterable = iterable_obj
        self.tqdm = tqdm.tqdm(iterable_obj, dynamic_ncols=True, total=total, leave=leave, desc=title, smoothing=smoothing, initial=initial)
        self.total = total if total != None else 0
        self.current = 0

        self.itererr = None 
        try:
            iter(self.iterable)
        except TypeError as e:
            self.itererr = e

    def Add(self, num:int=1):
        self.current = self.current + num
        self.tqdm.update(num)
    
    def Set(self, num:int):
        if num < self.current:
            raise Exception("不能小于当前进度")

        if num == self.current:
            return

        step = num - self.current
        self.current = num
        self.tqdm.update(step)
    
    def Close(self):
        self.tqdm.close()
    
    def SetTotal(self, total:int):
        self.total = total
        self.tqdm.total = total 
        self.tqdm.refresh()
    
    def Total(self) -> int:
        return self.total 

    def Current(self) -> int:
        return self.current 
    
    def Remain(self) -> int:
        return self.total - self.current 

    def __iter__(self):
        if self.itererr != None:
            raise Exception("可迭代的参数没有传入, 需要传入, 例如Tools.ProgressBar(range(10)): " + str(self.itererr))

        for obj in self.iterable:
            # print("update")
            self.tqdm.update(1)
            yield obj 

        self.tqdm.close()
        return 

if __name__ == "__main__":
    import time
    for i in ProgressBar(range(10), title="test sleep"):
        time.sleep(0.3)
        #   print(i)
        
    p = ProgressBar(total=10, title="test sleep")
    for i in range(10):
        time.sleep(0.3)
        p.Add(1) 
    p.Close()