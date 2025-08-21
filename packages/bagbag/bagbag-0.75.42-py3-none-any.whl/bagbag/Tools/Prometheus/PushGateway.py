from __future__ import annotations

import prometheus_client as pc
import time
import socket

import threading

from ... import Base64 

from .metrics import * 
from ... import Http, Tools, Lg, Funcs

#print("load " + '/'.join(__file__.split('/')[-2:]))

class PushGateway():
    def __init__(self, address:str, job:str=None, basicAuthUser:str=None, basicAuthPass:str=None, pushinterval:int=15, instance:str=None, debug:bool=False):
        self.job = job if job != None else "default"
        self.instance = instance if instance != None else socket.gethostname()
        self.address = address 
        self.registry = pc.CollectorRegistry()
        self.pushinterval = pushinterval

        self.basicAuthUser = basicAuthUser
        self.basicAuthPass = basicAuthPass
        if self.basicAuthUser != None and self.basicAuthPass != None:
            self.headers = {
                "Authorization": "Basic " + Base64.Encode(self.basicAuthUser+":"+self.basicAuthPass)
            }
        else:
            self.headers = {}
        self.debug = debug

        # print("address:", address)

        if not self.address.startswith("http://") and not self.address.startswith("https://"):
            self.address = 'https://' + self.address 
        
        self.address = self.address + f"/metrics/job/{self.job}/instance/{self.instance}"

        if self.debug:
            Lg.Trace(self.address)
        
        t = threading.Thread(target=self.run)
        t.daemon = True 
        t.start()
    
    def run(self):
        # print(1)
        rl = Tools.RateLimit(str(int(3600/self.pushinterval)) + "/h")
        while True:
            rl.Take()
            data = pc.generate_latest(self.registry)
            if self.debug:
                Lg.Trace("Posting data:", data)
            # print(data)
            # print(self.address)
            if data != "":
                while True:
                    try:
                        Http.PutRaw(self.address, data, headers=self.headers, timeoutRetryTimes=9999)
                        break 
                    except Exception as e:
                        Lg.Warn(e)
                        time.sleep(1)
                        # print(e)
        
    def NewCounter(self, name:str, help:str) -> PrometheusCounter:
        return PrometheusCounter(name, help, self.registry)
    
    def NewCounterWithLabel(self, name:str, labels:list[str], help:str) -> PrometheusCounterVec:
        return PrometheusCounterVec(name, labels, help, self.registry)
    
    def NewGauge(self, name:str, help:str) -> PrometheusGauge:
        return PrometheusGauge(name, help, self.registry)
    
    def NewGaugeWithLabel(self, name:str, labels:list[str], help:str) -> PrometheusGaugeVec:
        return PrometheusGaugeVec(name, labels, help, self.registry)

if __name__ == "__main__":
    import time
    import random

    p = PushGateway("pushgateway.example.com", "test_job")
    c = p.NewCounterWithLabel(
        "test_counter", 
        ["label1", "label2"], # Two labels, will display with this order
        "test counter metric"
    )
    g = p.NewGaugeWithLabel(
        "test_gauge", 
        ["label1", "label2"], # Two labels, will display with this order
        "test gauge metric"
    )
    while True:
        c.Add({"label2": "value2", "label1": "value1"}) # Order is not matter
        c.Add(["l3", "l4"])
        c.Add(["l5"]) # Will be "l5" and ""
        c.Add(["l6", "l7", "l8"]) # Will be "l7" and "l8"
        g.Set(["l6", "l7", "l8"], random.randint(0, 100))
        time.sleep(1)