from .. import Http
from .. import Json
from .. import Time
from .. import Lg
from ..Tools import Cache
import typing 

class FlashPoint():
    def __init__(self, apikey:str) -> None:
        self.apikey = apikey 
    
    def Search(self, basetypes:list[str]|str, keyword:str=None, pagesize:int=100, page:int=0, fromTime:str|int="2024-05-15T22:09:39Z", toTime:str="now", order:str="desc") -> dict:
        """
        这个Python函数使用指定参数执行搜索，并以JSON格式返回结果。

        • 参数 basetypes：Search 方法中的 basetypes 参数用于指定搜索的基础类型。它可以是单个字符串或字符串列表。如果是列表，方法会用’AND’连接列表元素以形成搜索查询。
        • 类型：basetypes：list[str]|str
        • 参数 keyword：Search 方法中的 keyword 参数用于指定要在搜索查询中查找的搜索词。它是一个代表您想在指定的基础类型内搜索的关键词或短语的字符串。如果提供，搜索结果将根据此进行过滤。
        • 类型：keyword：str
        • 参数 pagesize：Search 方法中的 pagesize 参数指定每页搜索结果返回的数量。它决定搜索结果每页显示多少项，默认为100。
        • 类型：pagesize：int（可选）
        • 参数 page：Search 方法中的 page 参数用于指定要获取哪一页的结果。它是一个整数，表示页面编号，从0开始表示第一页。通常每页包含pagesize数量的结果，默认为0。
        • 类型：page：int（可选）
        • 参数 fromTime：Search 方法中的 fromTime 参数指定搜索查询的开始时间。它可以以字符串格式（例如：“2024-05-15T22:09:39Z”）或作为表示Unix时间戳的整数提供，默认为2024-05-15T22:09:39Z。
        • 类型：fromTime：str|int（可选）
        • 参数 toTime：toTime 是一个参数，它指定搜索查询的结束时间。在这段代码片段中，默认设置为”now”，这意味着搜索将包括到当前时间为止的结果，默认为now。
        • 类型：toTime：str（可选）
        • 参数 order：Search 方法中的 order 参数指定搜索结果的排序顺序。它可以有两个可能的值：“asc”表示升序，或”desc”表示根据sort_date字段的降序，默认为desc。
        • 类型：order：str（可选）
        • 返回值：Search 方法返回一个包含搜索结果的字典。如果HTTP响应状态码为200，则将响应的JSON内容加载并作为字典返回。如果状态码不是200，则抛出异常，消息表示搜索未返回200状态码。
        """
        url = "https://fp.tools/api/v4/all/search"

        if type(basetypes) == list:
            basetypes = ' AND '.join(basetypes)

        keyword = f" + ({keyword})" if keyword != None else ""

        if type(fromTime) in [int, float]:
            fromTime = Time.Strftime(fromTime, "%Y-%m-%dT%H:%M:%SZ", utc=True)

        data = {"size": pagesize,
                            "query": f"+basetypes:({basetypes}) {keyword} + sort_date:[{fromTime} TO {toTime}]",
                            "from": pagesize * page , "track_total_hits": 10000,
                            "traditional_query": True,
                            "sort": [f"sort_date:{order}"]}

        headers = {
            'Authorization': f'Bearer {self.apikey}'
        }

        # Lg.Trace(data)

        resp = Http.PostJson(url, data, headers=headers, timeout=300)
        if resp.StatusCode == 200:
            return Json.Loads(resp.Content)
        else:
            raise Exception(f"搜索返回状态码不是200: {resp.StatusCode}")
    
    def FetchDataUntilNow(self, basetypes:list[str]|str, fromTime:str|int="2024-05-15T22:09:39Z", batchsize:int=200) -> typing.Iterable[dict]:
        """
        这个函数根据指定的基础类型和起始时间，持续获取数据直到当前时间。

        :param basetypes: `FetchDataUntilNow`方法中的`basetypes`参数可以是字符串列表或单个字符串，用于过滤并指定您想要获取的数据类型。
        :type basetypes: list[str]|str
        :param fromTime: `FetchDataUntilNow`方法中的`fromTime`参数指定了应从哪个时间开始获取数据。如果调用方法时未提供值，则默认设置为"2024-05-15T22:09:39Z"。此参数默认为2024-05-15T22:09:39Z。
        :type fromTime: str|int (可选)
        """
        sleepwaittime = 1
        cache = Cache.FIFO(batchsize * 2)
        while True:
            try:
                res = self.Search(basetypes, pagesize=batchsize, fromTime=fromTime, order="asc")
            except Exception as e:
                Lg.Warn("Error:", e)
                Time.Sleep(sleepwaittime)
                sleepwaittime = sleepwaittime * 2
                continue 
            
            sleepwaittime = 1

            if res['hits']['total']['value'] == 0 and res['hits']['total']['relation'] == 'eq':
                break 
        
            if res['hits']['total']['value'] == 1 and res['hits']['total']['relation'] == 'eq':
                doc = res['hits']['hits'][0]
                _id = doc['_id']
                src = doc["_source"]
                
                if _id in cache:
                    break 

            for doc in res['hits']['hits']:
                _id = doc['_id']
                src = doc['_source']
                fromTime = src['sort_date']
                
                if _id not in cache:
                    yield src
                    cache[_id] = None 

if __name__ == "__main__":
    fp = FlashPoint(apikey)

    for doc in fp.FetchDataUntilNow("chat", Time.Now() - 120): # 时间会被转成UTC
        # Lg.Trace(doc)
        # break

        message = doc['body']['text/plain'] if 'body' in doc else "[EMPTY MESSAGE]"
        time = doc['sort_date']
        Lg.Trace(time, message)

# Search返回的dict大概类似这样
# 
# {
#     "hits": {
#         "hits": [
#             {
#                 "_id": "123",
#                 "_source": {
#                     "key": "value"
#                 },
#                 "_type": "_doc",
#                 "sort": [
#                     1715810981000
#                 ]
#             }
#         ],
#         "max_score": null,
#         "total": {
#             "relation": "eq",
#             "value": 8353
#         }
#     },
#     "timed_out": false,
#     "took": 117
# }