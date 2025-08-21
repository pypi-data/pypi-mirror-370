
from typing import Any


#print("load random")

def Int(min:int, max:int) -> int:
    import random 
    return random.randint(min, max)

def Choice(obj:list|str, count:int=1) -> Any | list[Any]:
    import random 
    if count <= 1:
        return random.choice(obj)
    else:
        return [random.choice(obj) for i in range(count)]

def String(length:int=8, charset:str="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") -> str:
    import random 
    res = []
    while len(res) < length:
        res.append(random.choice(charset))
    
    return "".join(res)

def Shuffle(li:list) -> list:
    import random 
    import copy
    l = copy.copy(li)
    random.shuffle(l)
    return l

if __name__ == "__main__":
    print(Choice("doijwoefwe"))
    print(String(5))
    print(Shuffle([1,2,3,4,5]))