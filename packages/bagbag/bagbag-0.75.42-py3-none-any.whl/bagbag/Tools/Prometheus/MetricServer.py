from __future__ import annotations

import prometheus_client as pc

try:
    from .metrics import * 
except:
    from metrics import * 

#print("load " + '/'.join(__file__.split('/')[-2:]))

# It creates a Prometheus server that listens on the specified port and IP address.
class MetricServer():
    def __init__(self, listen:str="0.0.0.0", port:int=9105):
        pc.start_http_server(port, listen)
    
    def NewCounter(self, name:str, help:str) -> PrometheusCounter:
        return PrometheusCounter(name, help)
    
    def NewCounterWithLabel(self, name:str, labels:list[str], help:str) -> PrometheusCounterVec:
        return PrometheusCounterVec(name, labels, help)
    
    def NewGauge(self, name:str, help:str) -> PrometheusGauge:
        return PrometheusGauge(name, help)
    
    def NewGaugeWithLabel(self, name:str, labels:list[str], help:str) -> PrometheusGaugeVec:
        return PrometheusGaugeVec(name, labels, help)

if __name__ == "__main__":
    import time
    import random

    p = MetricServer(port=8876)
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