import typing
from .. import Base64

## print("load python")

def Range(startOrEnd:int, end:int=None) -> typing.Iterator[str]:
    """
    If the second argument is provided, return a range from the first argument to the second argument,
    otherwise return a range from 0 to the first argument.
    If the second argument is smaller than the first argument, the range will be reverse.
    
    :param startOrEnd: The first number in the range. If end is not specified, this is the last number
    in the range
    :type startOrEnd: int
    :param end: The end of the range
    :type end: int
    :return: A range object
    """
    if end != None:
        if startOrEnd > end:
            return range(startOrEnd, end, -1)
        else:
            # print(startOrEnd, end, -1)
            return range(startOrEnd, end)
    else:
        return range(0, startOrEnd)

def Serialize(obj:typing.Any, safe:bool=True) -> str:
    if safe == True:
        import msgpack
        datab = b'm' + msgpack.packb(obj, use_bin_type=True)
    else:
        import pickle
        datab = b'p' + pickle.dumps(obj, protocol=2)

    return Base64.Encode(datab)

def Unserialize(data:str) -> typing.Any:
    data = Base64.Decode(data)
    if type(data) == str:
        data = data.encode()
        
    # print(repr(data))
    if data[0] == 109:
        import msgpack
        obj = msgpack.unpackb(data[1:], raw=False, strict_map_key=False)
    else:
        import pickle
        obj = pickle.loads(data[1:])

    return obj

if __name__ == "__main__":
    print([i for i in Range(10)])
    print([i for i in Range(20, 30)])
    print([i for i in Range(30, 25)])

