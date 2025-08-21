from __future__ import annotations
import prometheus_client as pc

class PrometheusCounter():
    def __init__(self, name:str, help:str, registry:pc.CollectorRegistry=None) -> None:
        if registry != None:
            self.c = pc.Counter(name, help, registry=registry)
        else:
            self.c = pc.Counter(name, help)
        self.current = 0

        # import ipdb
        # ipdb.set_trace()
    
    def Add(self, num:int|float=1):
        self.c.inc(num)
    
    def Set(self, num:int|float=1):
        if num < self.current:
            raise Exception(f"Count类型只能设置更大类型的值, 当前值和想设置的值为: {self.current}, {num}")
        
        if num == self.current:
            return 

        self.c.inc(num - self.current)
        self.current = num

class PrometheusCounterVecLabeled():
    def __init__(self, labels:dict|list, pgv:PrometheusCounterVec):
        self.labels = labels 
        self.pgv = pgv
    
    def Set(self, num:int|float):
        self.pgv.Set(self.labels, num) 
        return self
    
    def Add(self, num:int|float=1):
        self.pgv.Add(self.labels, num)
        return self

class PrometheusCounterVec():
    def __init__(self, name:str, labels:list[str], help:str, registry:pc.CollectorRegistry=None) -> None:
        self.labels = labels 
        if registry != None:
            self.c = pc.Counter(name, help, labels, registry=registry)
        else:
            self.c = pc.Counter(name, help, labels)
        self.current = {}
    
    def Label(self, labels:dict|list) -> PrometheusCounterVecLabeled:
        return PrometheusCounterVecLabeled(labels, self)
    
    def Add(self, labels:dict|list, num:int|float=1):
        """
        It adds a new label to the metric.
        
        :param labels: a list of labels, or a dict of labels
        :type labels: dict|list
        :param num: The number to increment the counter by, defaults to 1
        :type num: int|float (optional)
        """
        if type(labels) == dict:
            lb = []
            for k in self.labels:
                if k in labels:
                    lb.append(labels[k])
                else:
                    lb.append("")
        elif type(labels) == list:
            if len(self.labels) == len(labels):
                lb = labels
            else:
                lb = labels[:len(self.labels)] + [""]*(len(self.labels) - len(labels))

        lbr = repr(lb)
        if lbr not in self.current:
            self.current[lbr] = 0

        self.current[lbr] = self.current[lbr] + num
        self.c.labels(*lb).inc(num)
    
    def Set(self, labels:dict|list, num:int|float=1):
        """
        It adds a new label to the metric.
        
        :param labels: a list of labels, or a dict of labels
        :type labels: dict|list
        :param num: 需要设置到counter的数字, 只能等于大于之前的数字, 否则抛异常
        :type num: int|float (optional)
        """
        if type(labels) == dict:
            lb = []
            for k in self.labels:
                if k in labels:
                    lb.append(labels[k])
                else:
                    lb.append("")
        elif type(labels) == list:
            if len(self.labels) == len(labels):
                lb = labels
            else:
                lb = labels[:len(self.labels)] + [""]*(len(self.labels) - len(labels))

        lbr = repr(lb)
        if lbr not in self.current:
            self.current[lbr] = 0
        
        if num < self.current[lbr]:
            raise Exception(f"Count类型只能设置更大类型的值, 当前值和想设置的值为: {self.current}, {num}")
        
        if num == self.current[lbr]:
            return 

        self.c.labels(*lb).inc(num - self.current[lbr])
        self.current[lbr] = num

class PrometheusGauge:
    def __init__(self, name:str, help:str, registry:pc.CollectorRegistry=None) -> None:
        if registry != None:
            self.g = pc.Gauge(name, help, registry=registry)
        else:
            self.g = pc.Gauge(name, help)
        
        self.current = 0
    
    def Set(self, num:int|float):
        self.current = num 
        self.g.set(num)
    
    def Add(self, num:int|float=1):
        self.current += num 
        self.g.set(self.current)

class PrometheusGaugeVecLabeled():
    def __init__(self, labels:dict|list, pgv:PrometheusGaugeVec):
        self.labels = labels 
        self.pgv = pgv
    
    def Set(self, num:int|float):
        self.pgv.Set(self.labels, num) 
        return self
    
    def Add(self, num:int|float=1):
        self.pgv.Add(self.labels, num)
        return self

class PrometheusGaugeVec():
    def __init__(self, name:str, labels:list[str], help:str, registry:pc.CollectorRegistry=None) -> None:
        self.labels = labels 
        if registry != None:
            self.g = pc.Gauge(name, help, labels, registry=registry)
        else:
            self.g = pc.Gauge(name, help, labels)
        
        self.currents = {}

    def Label(self, labels:dict|list) -> PrometheusGaugeVecLabeled:
        return PrometheusGaugeVecLabeled(labels, self)
    
    def getlabel(self, labels:dict|list) -> list:
        if type(labels) == dict:
            lb = []
            for k in self.labels:
                if k in labels:
                    lb.append(labels[k])
                else:
                    lb.append("")
        elif type(labels) == list:
            if len(self.labels) == len(labels):
                lb = labels
            else:
                lb = labels[:len(self.labels)] + [0]*(len(self.labels) - len(labels))
        
        return lb
    
    def Set(self, labels:dict|list, num:int|float):
        """
        It adds a number to the graph.
        
        :param labels: The labels of the histogram
        :type labels: dict|list
        :param num: The number of times the label is added, defaults to 1
        :type num: int|float (optional)
        """
        
        lb = self.getlabel(labels)
        if ''.join(lb) not in self.currents:
            self.currents[''.join(lb)] = 0 

        self.currents[''.join(lb)] = num
        self.g.labels(*lb).set(num)

    def Add(self, labels:dict|list, num:int|float=1):
        lb = self.getlabel(labels)
        if ''.join(lb) not in self.currents:
            self.currents[''.join(lb)] = 0 
        
        self.currents[''.join(lb)] += num
        self.Set(labels, self.currents[''.join(lb)])