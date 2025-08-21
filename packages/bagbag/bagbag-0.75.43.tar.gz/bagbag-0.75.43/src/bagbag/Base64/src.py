import pybase64

# print("load base64")

def Encode(s:str|bytes) -> str:
    if type(s) == str:
        return pybase64.b64encode(bytes(s, "utf-8")).decode("utf-8")
    else:
        return pybase64.b64encode(s).decode("utf-8")

def Decode(s:str) -> str|bytes:
    res = pybase64.b64decode(s, validate=True)
    try:
        return res.decode("utf-8")
    except:
        return res 

if __name__ == "__main__":
    data = Encode(open("Lg.py").read())
    print(Decode(data))
    