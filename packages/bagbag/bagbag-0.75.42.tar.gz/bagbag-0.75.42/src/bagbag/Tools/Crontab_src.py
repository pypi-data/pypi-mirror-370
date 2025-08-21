from __future__ import annotations

import schedule
import time 

from ..Thread import Thread

#print("load " + '/'.join(__file__.split('/')[-2:]))

class Crontab():
    def __init__(self):
        Thread(self.run)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1) 

    def Every(self, interval: int = 1) -> Crontab:
        self.obj = schedule.every(interval) 
        self.everyInterval = interval
        return self
    
    def Second(self) -> Crontab:
        if self.everyInterval == 1:
            self.obj = self.obj.second
        elif self.everyInterval > 1:
            self.obj = self.obj.seconds

        return self 
    
    def Minute(self) -> Crontab:
        if self.everyInterval == 1:
            self.obj = self.obj.minute
        elif self.everyInterval > 1:
            self.obj = self.obj.minutes

        return self 
    
    def Hour(self) -> Crontab:
        if self.everyInterval == 1:
            self.obj = self.obj.hour
        elif self.everyInterval > 1:
            self.obj = self.obj.hours

        return self 
    
    def Day(self) -> Crontab:
        if self.everyInterval == 1:
            self.obj = self.obj.day
        elif self.everyInterval > 1:
            self.obj = self.obj.days

        return self 

    def Week(self) -> Crontab:
        if self.everyInterval == 1:
            self.obj = self.obj.week
        elif self.everyInterval > 1:
            self.obj = self.obj.weeks

        return self 
    
    def At(self, time: str) -> Crontab:
        self.obj = self.obj.at(time)
        return self

    def Do(self, job_func, *args, **kwargs):
        self.obj.do(job_func, *args, **kwargs)
    
    def Monday(self):
        self.obj = self.obj.monday 
        return self 
    
    def Tuesday(self):
        self.obj = self.obj.tuesday 
        return self 
    
    def Wednesday(self):
        self.obj = self.obj.wednesday 
        return self  

    def Thursday(self):
        self.obj = self.obj.thursday 
        return self 
    
    def Friday(self):
        self.obj = self.obj.friday 
        return self 
    
    def Saturday(self):
        self.obj = self.obj.saturday 
        return self 
    
    def Sunday(self):
        self.obj = self.obj.sunday 
        return self 

if __name__ == "__main__":
    def job():
        print("I'm working...")
    
    c = Crontab()

    c.Every(3).Second().Do(job)
    c.Every(3).Minute().Do(job)
    c.Every(3).Hour().Do(job)
    c.Every(3).Day().Do(job)
    c.Every(3).Week().Do(job)

    # Run job every minute at the 23rd second
    c.Every().Minute().At(":23").Do(job)

    # Run job every hour at the 42rd minute
    c.Every().Hour().At(":42").Do(job)

    # Run jobs every 5th hour, 20 minutes and 30 seconds in.
    # If current time is 02:00, first execution is at 06:20:30
    c.Every(5).Hour().At("20:30").Do(job)

    # Run job every day at specific HH:MM and next HH:MM:SS
    c.Every().Day().At("10:30").Do(job)
    c.Every().Day().At("10:30:42").Do(job)

    # Run job on a specific day of the week
    c.Every().Monday().Do(job)
    c.Every().Wednesday().At("13:15").Do(job)
    c.Every().Minute().At(":17").Do(job)

    while True:
        time.sleep(1)