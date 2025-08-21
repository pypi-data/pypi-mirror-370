import cachetools

#print("load " + '/'.join(__file__.split('/')[-2:]))

def LRU(size:int) -> cachetools.LRUCache:
    """
    The function returns an instance of a Least Recently Used (LRU) cache with a specified size using
    the cachetools library in Python.
    
    :param size: The parameter "size" is an integer that specifies the maximum number of items that can
    be stored in the LRU cache. When the cache reaches its maximum capacity, the least recently used
    item will be removed to make space for a new item
    :type size: int
    :return: The function `LRU` returns an instance of the `cachetools.LRUCache` class with the
    specified `size` parameter.
    """
    return cachetools.LRUCache(size)

def FIFO(size:int) -> cachetools.FIFOCache:
    """
    This function returns a FIFO cache object with a specified size using the cachetools library in
    Python.
    
    :param size: The parameter "size" is an integer that specifies the maximum number of items that can
    be stored in the FIFO cache
    :type size: int
    :return: an instance of the `cachetools.FIFOCache` class with the specified `size` parameter.
    """
    return cachetools.FIFOCache(size)

def LFU(size:int) -> cachetools.LFUCache:
    """
    The function returns an instance of a Least Frequently Used (LFU) cache with a specified size using
    the cachetools library in Python.
    
    :param size: The parameter "size" is an integer that specifies the maximum number of items that can
    be stored in the LFU cache. The LFU cache is a type of cache that stores items based on their
    frequency of use, with the least frequently used items being evicted first when the cache reaches
    its maximum
    :type size: int
    :return: The function `LFU` returns an instance of the `cachetools.LFUCache` class with the
    specified `size` parameter.
    """
    return cachetools.LFUCache(size)

def MRU(size:int) -> cachetools.MRUCache:
    """
    The function creates and returns a MRU cache object with a specified size using the cachetools
    library in Python.
    
    :param size: The parameter "size" is an integer that represents the maximum number of items that can
    be stored in the MRU cache
    :type size: int
    :return: The function `MRU` returns an instance of the `cachetools.MRUCache` class with the
    specified `size` parameter.
    """
    return cachetools.MRUCache(size)

def RR(size:int) -> cachetools.RRCache:
    """
    The function creates and returns a cache object with a specified size using the RRCache algorithm
    from the cachetools library in Python.
    
    :param size: The parameter "size" is an integer that specifies the maximum number of items that can
    be stored in the RRCache object. The RRCache is a cache implementation that uses a "recently read"
    eviction policy, which means that the least recently read items will be evicted from the cache
    :type size: int
    :return: The function `RR` returns an instance of the `cachetools.RRCache` class with the specified
    `size` parameter.
    """
    return cachetools.RRCache(size)

def TTL(size:int, ttl:int|float) -> cachetools.TTLCache:
    """
    The function creates and returns a TTLCache object with a specified size using the cachetools
    library.
    
    :param size: The parameter "size" is an integer that specifies the maximum number of items that can
    be stored in the cache. It is used to initialize a new instance of the TTLCache class from the
    cachetools module. This cache implementation automatically removes items that have not been accessed
    for a certain amount of time
    :type size: int
    :return: The function `TTL` is returning an instance of `cachetools.TTLCache` with the specified
    `size` parameter.
    """
    return cachetools.TTLCache(size, ttl)

if __name__ == "__main__":
    # from bagbag import Range, Funcs, Time, Lg
    cache = LRU(5000)

    dic = {}
    keys = []
    for _ in Range(5000):
        key = Funcs.UUID()
        cache[key] = Funcs.UUID()
        keys.append(key)
        dic[key] = None 

    start = Time.Now()

    for _ in Range(10000):
        # cache[Random.Choice(keys)] # 0.006376028060913086
        # if Funcs.UUID() in cache: #  0.038994789123535156
        # if Random.Choice(keys) in cache: # 0.004488945007324219
        # try:
        #     # cache[Random.Choice(keys)] # 0.006552934646606445
        #     cache[Funcs.UUID()] # 0.04251289367675781
        # except:
        #     pass 
        # cache.__contains__(Funcs.UUID()) # 0.03940105438232422
        Funcs.UUID() in dic

    end = Time.Now()

    Lg.Trace(end - start)