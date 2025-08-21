from .... import Http, Json, Time, Tools, String

#print("load " + '/'.join(__file__.split('/')[-2:]))

# https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md

class CoinsPairPrice():
    def __init__(self, pair:str, price:float, time:float) -> None:
        self.Pair:str = pair 
        self.Price:float = price  
        self.Time:float = time
    
    def __repr__(self) -> str:
        return f"CoinsPairPrice(Pair={self.Pair} Price={self.Price} Time={self.Time})"

    def __str__(self) -> str:
        return self.__repr__()

servertime = None
rl = Tools.RateLimit("1/s")

def ServerTime() -> float:
    global servertime 
    if servertime == None:
        servertime = Json.Loads(Http.Get("https://api.binance.com/api/v3/time").Content)['serverTime'] / 1000
    timegap = Time.Now() - servertime

    return Time.Now() - timegap

def GetPrice(pair:str|list="BTCUSDT") -> CoinsPairPrice | list[CoinsPairPrice]:
    """
    The function `GetPrice` retrieves the current price of a specified cryptocurrency pair or a list of
    pairs from the Binance API.
    
    :param pair: For example: BTCUSDT. The trading pair(s) for which you want to retrieve the current price(s). 
    It can be a string for a single pair or a list of strings for multiple pairs. If no pair is specified, the
    function will return the prices for all available trading pairs
    :type pair: str|list
    :return: The function `GetPrice` returns either a `CoinsPairPrice` object or a list of
    `CoinsPairPrice` objects depending on the input parameter `pair`. If `pair` is a string, a single
    `CoinsPairPrice` object is returned. If `pair` is a list, a list of `CoinsPairPrice` objects is
    returned. If `pair` is `None`,
    """
    rl.Take()
    
    url = "https://api.binance.com/api/v3/ticker/price"
    if pair != None:
        if type(pair) == str:
            url = url + "?symbol=" + pair
        elif type(pair) == list:
            url = url + "?symbols=" + String(Json.Dumps(pair).replace(" ", "")).URLEncode()  
        else:
            raise Exception("不合适的pair类型")
    
    resp = Http.Get(url)
    if resp.StatusCode != 200:
        raise Exception(f"状态码不为200: {resp.StatusCode}. 详见: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md")
    
    st = ServerTime()

    content = Json.Loads(resp.Content)

    if pair != None and type(pair) == str:
        return CoinsPairPrice(content['symbol'], content['price'], st)

    resp = []
    for p in content:
        resp.append(CoinsPairPrice(p['symbol'], p['price'], st))

    return resp
