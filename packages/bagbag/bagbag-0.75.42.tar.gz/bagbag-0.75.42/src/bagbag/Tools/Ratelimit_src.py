
from .Lock_src import Lock
from .. import Time


#print("load " + '/'.join(__file__.split('/')[-2:]))

class RateLimit:
    def __init__(self, rate:str, sleep:bool=True):
        """
        sleep=True的时候会添加一个sleep, 可以把请求平均在时间段内. 在低速率的时候能限制准确. 高速率例如每秒50次以上, 实际速率会降低, 速率越高降低越多. 
        sleep=False的时候没有sleep, 会全在一开始扔出去, 然后block住, 等下一个周期, 在需要速率很高的时候可以这样, 例如发包的时候, 一秒限制2000个包这样.
        
        It takes a rate limit string in the form of "X/Y" where X is the number of requests and Y is the
        duration. 
        The duration can be specified in seconds (s), minutes (m), hours (h), or days (d). 
        
        The Take() method should be thread-safe.
        
        :param rate: The rate at which you want to limit the function calls
        :type rate: str
        :param sleep: If True, the rate limiter will sleep between requests. If False, it will not
        sleep, defaults to True
        :type sleep: bool (optional)
        """
        self.history = None
        self.rate = rate
        self.num, self.duration = self._parse_rate()
        self.history = []
        self.lock = Lock()
        self.sleeptime = float(self.duration) / float(self.num)
        self.sleep = sleep

    def _parse_rate(self):
        num, period = self.rate.split('/')
        num = int(num)
        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        return (num, duration)

    def Take(self) -> bool:
        if self.sleep:
            self.lock.Acquire()
            current_time = Time.Now()

            if not self.history:
                self.history.append(current_time)
                self.lock.Release()
                return 

            while len(self.history) > self.num:
                if self.history and self.history[-1] <= current_time - self.sleeptime:
                    self.history.pop()
                else:
                    Time.Sleep(self.sleeptime, bar=False)
    
            Time.Sleep(self.sleeptime, bar=False)
            self.history.insert(0, current_time)
            self.lock.Release()
            return True
        else:
            current_time = Time.Now()

            if not self.history:
                self.history.append(current_time)
                return True

            while True:
                #print("1")
                # 判断访问记录是否超过指定的时间限制, 如果超出限制, 移出list
                while self.history and self.history[-1] <= current_time - self.duration:
                    self.history.pop()

                #print(2)
                # 判断指定时间范围的访问记录数量是否超过最大次数
                if len(self.history) >= self.num:
                    #print(3)
                    Time.Sleep(self.duration - (current_time - self.history[-1]), bar=False)                
                else:
                    #print(4)
                    self.history.insert(0, current_time)
                    return True
                
                current_time = Time.Now()

if __name__ == "__main__":
    # Test speed
    # 
    def y(r):
        while True:
            r.Take(sleep=False)
            yield "1"

    import sys 
    t = RateLimit(sys.argv[1] + "/s") 
    
    from ProgressBar import ProgressBar
    pb = ProgressBar(y(t))
    for i in pb:
        pass

    # t = RateLimit("5/s") 
    # while True:
    #     t.Take(average=False)
    #     # t.Take(average=True)
    #     print("1", time.time())