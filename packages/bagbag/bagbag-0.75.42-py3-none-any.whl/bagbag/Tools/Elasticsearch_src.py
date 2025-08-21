import json 
import time 
import requests

from .. import Http, Lg, Json, String, Base64

# requests.exceptions.ReadTimeout

#print("load " + '/'.join(__file__.split('/')[-2:]))

def retryOnNetworkError(func): # func是被包装的函数
    def ware(self, *args, **kwargs): # self是类的实例
        while True:
            try:
                res = func(self, *args, **kwargs)
                break
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                time.sleep(3)

        return res
    
    return ware

class ElasticsearchCollection():
    def __init__(self, baseurl:str, indexname:str, headers:dict):
        self.baseurl = baseurl

        self.collectionurl = self.baseurl.strip("/") + "/" + indexname
        self.indexname = indexname

        self.headers = headers

    @retryOnNetworkError
    def Exists(self, id:int|str, Timeout:int=15) -> bool:
        url = self.collectionurl + "/_doc/" + str(id)
        r = Http.Head(url, timeout=Timeout, headers=self.headers)
        if r.StatusCode == 200:
            return True 
        elif r.StatusCode == 404:
            return False 
        else:
            raise Exception(r)
    
    @retryOnNetworkError
    def Get(self, id:int|str, Timeout:int=15) -> dict | None:
        url = self.collectionurl + "/_doc/" + str(id)
        r = Http.Get(url, timeout=Timeout, headers=self.headers)
        if r.StatusCode == 200:
            return Json.Loads(r.Content)['_source']
        elif r.StatusCode == 404:
            return None
        else:
            raise Exception(r)
    
    @retryOnNetworkError
    def Index(self, id:int|str, data:dict, refresh:bool=False, Timeout:int=15):
        url = self.collectionurl + "/_doc/" + str(id) + ("?refresh" if refresh else "")
        r = Http.PostJson(url, data, timeout=Timeout, headers=self.headers)
        if r.StatusCode != 201 and r.StatusCode != 200:
            raise Exception("插入到Elasticsearch出错: 状态码不是201或者200")
    
    @retryOnNetworkError
    def IndexBulk(self, data:dict, refresh:bool=False, Timeout:int=15):
        """
        批量index documents.
        data格式如下

        {
            [_id]: [doc],
            [_id]: [doc],
        }

        例如

        {
            '1': {'key': 'value1'},
            '2': {'key': 'value2'},
        }
        """
        url = self.baseurl + "/_bulk" + ("?refresh" if refresh else "")
        mdata = []
        for id in data:
            mdata.append(Json.Dumps({ "index" : { "_index" : self.indexname, "_id" : id } }, indent=None))
            mdata.append(Json.Dumps(data[id], indent=None))
        
        r = Http.PostRaw(url, '\n'.join(mdata), headers=self.headers)
        if r.StatusCode != 201 and r.StatusCode != 200:
            raise Exception("插入到Elasticsearch出错: 状态码不是201或者200")
    
    @retryOnNetworkError
    def Refresh(self, Timeout:int=15):
        Http.PostRaw(self.collectionurl+"/_refresh", "", timeout=Timeout, headers=self.headers)
    
    @retryOnNetworkError
    def Delete(self, id:int|str):
        r = Http.Delete(self.collectionurl + "/_doc/" + str(id), headers=self.headers)
        if r.StatusCode != 200:
            raise Exception("在elasticsearch删除id为\"" + str(id) + "\"的文档出错")
    
    @retryOnNetworkError
    def Search(self, key:str, value:str, page:int=1, pagesize:int=50, OrderByKey:str=None, OrderByOrder:str="ase", Highlight:str=None, mustIncludeAllPhrase:bool=True) -> dict:
        """
        It searches for a value in a key in Elasticsearch.
        
        :param key: the field to search in
        :type key: str
        :param value: The value to search for
        :type value: str
        :param page: The page number of the results you want to get, defaults to 1
        :type page: int (optional)
        :param pagesize: The number of results to return per page, defaults to 50
        :type pagesize: int (optional)
        :param OrderByKey: The key to sort by
        :type OrderByKey: str
        :param OrderByOrder: ase or desc, defaults to ase
        :type OrderByOrder: str (optional)
        :param Highlight: The field to highlight
        :type Highlight: str
        :param mustIncludeAllPhrase: If true, the search result must include all the words in the value,
        defaults to True
        :type mustIncludeAllPhrase: bool (optional)
        :return: A list of dictionaries.
        """
        if page * pagesize > 10000:
            raise Exception("偏移量不能超过10000: page * pagesize = " + str(page*pagesize))
        
        startfrom = (page - 1) * pagesize

        if mustIncludeAllPhrase:
            query = {
                "query": {
                    "match_phrase": {
                        key: {
                            "query": value,
                            "slop":  100,
                        },
                    },
                },
                "from": startfrom,
                "size": pagesize,
            }
        else:
            query = {
                "query": {
                    "match": {
                        key: value,
                    },
                },
                "from": startfrom,
                "size": pagesize,
            }
        
        if OrderByKey:
            query["sort"] = {
                OrderByKey: {
                    "order": OrderByOrder,
                }
            }
        
        if Highlight:
            query["highlight"] = {
                "fields": {
                    Highlight: {},
                },
            }

        # Lg.Debug(Json.Dumps(query))
        
        r = Http.PostJson(self.collectionurl+"/_search", query, headers=self.headers)
        if r.StatusCode != 200:
            raise Exception("在Elasticsearch中搜寻出错：" + r.Content)
        
        return json.loads(r.Content)

class Elasticsearch():
    def __init__(self, url:str, user:str=None, password:str=None):
        self.baseurl = url
        if not self.baseurl.startswith("http://") and not self.baseurl.startswith("https://"):
            self.baseurl = 'http://' + self.baseurl
        
        # Lg.Trace(String(self.baseurl).RegexFind(":[0-9]+$"))
        if len(String(self.baseurl).RegexFind(":[0-9]+$")) == 0:
            self.baseurl = self.baseurl + ":9200"
        
        self.headers = {}
        if user != None:
            self.headers['Authorization'] = 'Basic ' + Base64.Encode(user+":"+password)
    
    @retryOnNetworkError
    def Delete(self, IndexName:str):
        r = Http.Delete(self.baseurl.strip("/") + "/" + IndexName, headers=self.headers)
        if r.StatusCode != 200:
            raise Exception("删除索引\"" + IndexName + "\"失败")
    
    def Collection(self, IndexName:str):
        return ElasticsearchCollection(self.baseurl, IndexName, self.headers)

if __name__ == "__main__":
    es = Elasticsearch("192.168.1.186:9200")
    escth = es.Collection("telegram_history_content")

    sres = escth.Search("text", "bank account and routing number", 1, 50, "id", "desc")

    Lg.Debug(sres)