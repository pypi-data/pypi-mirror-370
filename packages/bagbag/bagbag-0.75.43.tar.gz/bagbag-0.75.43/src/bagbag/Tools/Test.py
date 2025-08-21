
cache = []

class Test():
    def __init__(self, obj) -> None:
        cache.append(obj)
    
    def Get(self) -> list:
        return cache