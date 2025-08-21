import listparser
import requests

#print("load " + '/'.join(__file__.split('/')[-2:]))

class rssFeed():
    def __init__(self, title:str, url:str):
        self.Title = title 
        self.URL = url
    
    def __str__(self) -> str:
        return f"RSSFeed(Title={self.Title} URl={self.URL})"

    def __repr__(self) -> str:
        return self.__str__()

def Opml(opmlurl:str) -> list[rssFeed]:
    res = []
    for i in listparser.parse(requests.get(opmlurl).content)['feeds']:
        res.append(rssFeed(i["title"], i["url"]))
    
    return res

if __name__ == "__main__":
    for i in Opml("https://wechat2rss.xlab.app/opml/sec.opml"):
        print(i)