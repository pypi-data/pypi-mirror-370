from .... import Http, File, Json, Time 
import typing 

class CryptocurrencyListingsResult():
    # https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest
    def __init__(self) -> None:
        # self.MarketCapStrict:float = None
        self.Name:str = None 
        """加密货币名称"""
        self.Symbol:str = None
        "加密货币符号"
        self.Slug:str = None 
        "Slug在数字货币领域通常指代一种简短、独特的标识符或别名。它用于标识特定的数字货币资产或项目，并在交易所、钱包应用程序和其他相关平台中使用。Slug 通常是由字母、数字和连字符组成的字符串，用于更方便地识别和引用特定的数字货币。不同的数字货币可能具有不同的 Slug，并且常用于URL、交易对和资产列表中。"
        self.DateAdded:str = None 
        """加密货币添加到系统的日期"""
        self.MarketCap:float = None 
        """根据我们的方法，市值"""
        self.Price:float = None 
        "各市场的最新平均交易价格"
        self.CirculatingSupply:float = None 
        "当前正在流通的加密货币的大致数量"
        self.TotalSupply:float = None 
        "目前存在的加密货币的大致总量（减去已被证实烧毁的加密货币）"
        self.MaxSupply:float = None 
        "我们对货币生命周期内最大硬币数量的最佳近似值"
        self.NumMarketPairs:float = None
        "交易每种货币的所有交易所的市场对数量"
        # self.MarketCapByTotalSupplyStrict:float = None 
        # "按总供应量计算的市值"
        self.Volume24h:float = None 
        "24 小时滚动调整后的交易量"
        # self.Volume7d:float = None 
        # "7天 滚动调整后的交易量"
        # self.Volume30d:float = None 
        # "滚动的 30 天调整后交易量"
        self.PercentChange1h:float = None 
        "每种货币的 1 小时交易价格百分比变化"
        self.PercentChange24h:float = None 
        "每种货币的 24 小时交易价格百分比变化"
        self.PercentChange7d:float = None  
        "每种货币的 7 天交易价格百分比变化"
        self.MarketCap:float = None 
        "总市值"
        self.LastUpdated:int = None 
        "信息的最后更新时间时间戳"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(%s)" % ' '.join([f"{attr}={getattr(self, attr)}" for attr in filter(lambda attr: attr[0].isupper() and type(getattr(self, attr)) in [int, float, str], self.__dir__())])

    def __str__(self) -> str:
        return self.__repr__()
    
class API():
    def __init__(self, key:str) -> None:
        self.server = "https://pro-api.coinmarketcap.com"
        self.key = key
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.key,
        }
    
    def CryptocurrencyListings(self, limit:int=190) -> typing.Iterator[CryptocurrencyListingsResult]:
        """
        The function `CryptocurrencyListings` retrieves the latest cryptocurrency listings from a server
        and returns an iterator of the results.
            注意:
                Cache / Update frequency: Every 60 seconds.
                1 call credit per 200 cryptocurrencies returned
        
        :param limit: The `limit` parameter is an optional parameter that specifies the maximum number
        of cryptocurrency listings to retrieve. By default, it is set to 200, but you can change it to
        any positive integer value to limit the number of listings returned, defaults to 200
        :type limit: int (optional)
        :return: an iterator of CryptocurrencyListingsResult objects.
        """
        url = self.server + '/v1/cryptocurrency/listings/latest'

        resp = Http.Get(url, headers=self.headers, Params={"limit": limit})

        if resp.StatusCode != 200:
            # 200 Successful
            # 400 Bad Request
            # 401 Unauthorized
            # 403 Forbidden
            # 429 Too Many Requests
            # 500 Internal Server Error
            raise Exception("获取CryptocurrencyListings出错, HTTP状态码:", resp.StatusCode)

        content = Json.Loads(resp.Content)

        if content['status']['error_code'] != 0:
            raise Exception("获取CryptocurrencyListings出错, 状态码:", content['status']['error_code'])

        return self._parseCryptocurrencyListingsContent(content)

        # File("cryptocurrency.listings").Write(resp.Content)

    def _parseCryptocurrencyListingsContent(self, content:dict) -> typing.Iterator[CryptocurrencyListingsResult]:
        for data in content['data']:
            clr = CryptocurrencyListingsResult()

            m = data['quote']['USD']
            
            clr.MarketCap = m['market_cap']
            clr.Name = data['name']
            clr.Symbol = data['symbol']
            # date_added：加密货币添加到系统的日期。
            clr.DateAdded = data['date_added']
            # price：各市场的最新平均交易价格。
            clr.Price = m['price']
            # circulating_supply：当前正在流通的加密货币的大致数量。
            clr.CirculatingSupply = data['circulating_supply']
            # total_supply：目前存在的加密货币的大致总量（减去已被证实烧毁的加密货币）。
            clr.TotalSupply = data['total_supply']
            # max_supply：我们对货币生命周期内最大硬币数量的最佳近似值。
            clr.MaxSupply = data['max_supply']
            # num_market_pairs：交易每种货币的所有交易所的市场对数量。
            clr.NumMarketPairs = data['num_market_pairs']
            # market_cap_by_total_supply_strict：按总供应量计算的市值。
            # volume_24h：24 小时滚动调整后的交易量。
            clr.Volume24h = m['volume_24h']
            # volume_7d: 24 小时滚动调整后的交易量。
            # volume_30d：滚动的 24 小时调整后交易量。
            # percent_change_1h： 每种货币的 1 小时交易价格百分比变化。
            clr.PercentChange1h = m['percent_change_1h']
            # percent_change_24h: 每种货币的 24 小时交易价格百分比变化。
            clr.PercentChange24h = m['percent_change_24h']
            # percent_change_7d： 每种货币的 7 天交易价格百分比变化。
            clr.PercentChange7d = m['percent_change_7d']
            clr.LastUpdated = Time.Strptime(data['last_updated'])
            clr.Slug = data['slug']

            yield clr