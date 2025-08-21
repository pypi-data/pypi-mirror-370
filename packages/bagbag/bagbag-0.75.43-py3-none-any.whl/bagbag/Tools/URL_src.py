from urllib.parse import urlparse, quote_plus, unquote

import requests
from urllib.parse import urlparse, urljoin

#print("load " + '/'.join(__file__.split('/')[-2:]))

class URLParseResult():
    def __init__(self, Schema:str, Host:str, Port:int, User:str, Pass:str, Path:str, Query:str, Fragment:str):
        self.Schema = Schema
        self.Host = Host    
        self.Port = Port    
        self.User = User    
        self.Pass = Pass    
        self.Path = Path    
        self.Query = Query   
        self.Fragment = Fragment
    
    def __repr__(self):
        return f"URLParseResult(Schema={self.Schema}, Host={self.Host}, Port={self.Port}, User={self.User}, Pass={self.Pass}, Path={self.Path}, Query={self.Query}, Fragment={self.Fragment})"

    def __str__(self):
        return f"URLParseResult(Schema={self.Schema}, Host={self.Host}, Port={self.Port}, User={self.User}, Pass={self.Pass}, Path={self.Path}, Query={self.Query}, Fragment={self.Fragment})"

class URL():
    def __init__(self, url:str):
        self.url = url 
    
    def Parse(self) -> URLParseResult:
        """
        It parses the URL and returns the URLParseResult object.
        :return: A URLParseResult object.
        """
        # 有时候是 example.com/abc?key=value, 这样没法解析, 所以加一个头才能解析
        if not self.url.startswith("http://") and not self.url.startswith("https://"):
            url = 'http://' + self.url 
        else:
            url = self.url 

        res = urlparse(url)

        # ipdb.set_trace()

        # 如果是自己加的协议头, 就不写到schema里面了
        if url == self.url:
            Schema = res.scheme
        else:
            Schema = None
        Path = res.path
        Query = res.query 
        Fragment = res.fragment

        if '@' not in res.netloc:
            User = None
            Pass = None
        else:
            u = res.netloc.split("@")[0]
            if ':' in u:
                User = u.split(":")[0]
                Pass = u.split(":")[1]
            elif len(u) != 0:
                User = u 
                Pass = None
            else:
                User = None 
                Pass = None
        # print(res)
        h = res.netloc 
        if '@' in res.netloc:
            h = res.netloc.split("@")[1]
        
        if ':' not in h:
            Host = h 
            if Schema == "http":
                Port = 80
            elif Schema == "https":
                Port = 443 
            else:
                Port = None
        else:
            Host = h.split(":")[0]
            Port = int(h.split(":")[1])
        
        return URLParseResult(Schema, Host, Port, User, Pass, Path, Query, Fragment)
    
    def Encode(self) -> str:
        return quote_plus(self.url)
    
    def Decode(self) -> str:
        return unquote(self.url)

    def GetRedirectChain(self) -> list[str]:
        """
        传入一个URL，返回所有301或302跳转的链接（包括最终的跳转目标）。如果传入的url不可访问则返回的list为空.

        参数:
        url (str): 初始URL。

        返回:
        list: 包含所有跳转链接的列表，按跳转顺序排列。
        """
        url = self.url

        redirect_chain = []
        session = requests.Session()
        while True:
            # print("trying:", url)
            try:
                response = session.get(url, allow_redirects=False, stream=True, timeout=15)
                response.close()  # 立即关闭连接，避免读取body
            except Exception as e:
                # print(f"Error fetching {url}: {e}")
                break

            # 获取完整的URI
            current_uri = urlparse(response.url)
            current_uri = f"{current_uri.scheme}://{current_uri.netloc}{current_uri.path}"
            # print('got:', current_uri)
            if current_uri not in redirect_chain:
                redirect_chain.append(current_uri)
            else:
                break

            if response.status_code in (301, 302):
                # 获取跳转目标URL
                location = response.headers.get('Location')
                if location:
                    # 确保跳转URL是绝对路径
                    url = urljoin(response.url, location)
                else:
                    break
            else:
                break

        return redirect_chain

if __name__ == "__main__":
    # u = URL("http://user:pass@docs.python.org:8897/3/library/urllib.parse.html?highlight=params&k=v#url-parsing")
    # print(u.Parse())

    # u = URL("example.com?title=правовая+защита")
    # print(u.Encode())

    # u = URL(u.Encode())
    # print(u.Decode())

    # u = URL("example.com/abc?key=value")
    # print(u.Parse())

    # u = URL("ss://YWVzLTI1Ni1jZmI6YW1hem9uc2tyMDU@54.95.169.40:443#%e6%97%a5%e6%9c%ac%3dtg%e9%a2%91%e9%81%93%3a%40bpjzx2%3d1")
    # print(u.Parse())

    print(URL('chrome-extension://aapbdbdomjkkjkaonfhkkikfgjllcleb/popup_css_compiled.css').Parse())