from __future__ import annotations

import requests

from ... import Http, Lg, Time, String, Tools, Range, Random

from bs4 import BeautifulSoup

import typing 

# resp = Http.Get("https://nitter.kavin.rocks/search?f=tweets&q=psychologist+a+paradox+&since=&until=&near=")

# File("tweet.html").Write(resp.Content)

# data = File("tweet.html").Read()

# x = Tools.XPath(data)

# item = x.Find("/html/body/div/div/div[2]/div[1]")

# 
# tweet 设置 用户 screenname
# tweet 返回用户obj -> 返回 cache 的 用户 obj , if 不存在则创建
# 
# 用户obj的属性更新, set info 之后 set 一份到 cache. 要带上是额外信息, 例如否解析完, 是否正在解析
# 用户obj的属性获取, get info 如果没有 在本obj 里面, 则 同步一次cache 的内容, 如果仍然没有, 则setinfo
# 
# 直接获取用户 obj -> 返回 cache 的 用户 obj , if 不存在则创建
# 
# ntucache['screenname'] = {'obj': user_object, 'updating': False, 'lastupdate': 0, "startupdate": 0}
# 
ntucache = Tools.Cache.LRU(2048)

class NitterTwitterUser():
    def __init__(self) -> None:
        self.ScreenName:str = None 

        self._favoriteCount:int = None 
        self._followersCount:int = None 
        self._statusesCount:int = None 
        self._friendsCount:int = None # 当前用户去follow别人的个数

        self._name:str = None 
        # self._id:int = None 
        self._location:str = None 
        self._registerTime:int = None 
        self._description:str = None 
        self._url:str = None
        self._verified:bool = None 
        # self._listedCount:int = None 
        
        self.raw_data:str = None

        self.twitter:Nitter = None 
        self.infoHasBeenSet = False # 是否已经set过info

    def setInfoByHtml(self, html:str):
        x = Tools.XPath(html)

        self._name:str = x.Find("//a[@class='profile-card-fullname']").Text()  
        # self._id:int = None 
        self._location:str = x.Find("//div[@class='profile-location']/span[2]").Text() if  x.Find("//div[@class='profile-location']/span[2]") else None
        self._registerTime:int = Time.Strptime(x.Find("//div[@class='profile-joindate']/span").Attribute("title"), "%I:%M %p - %d %b %Y")
        self._description:str = x.Find("//div[@class='profile-bio']").Text() if x.Find("//div[@class='profile-bio']") else None
        self._url:str = x.Find("//div[@class='profile-website']/span/a").Attribute("href") if x.Find("//div[@class='profile-website']/span/a") else None
        # ipdb.set_trace()
        
        self._verified:bool = True if x.Find("//span[@class='icon-ok verified-icon' and @title='Verified account']") != None else False 
        # self._listedCount:int = None 

        self._favoriteCount = int(x.Find("//li[@class='likes']/span[2]").Text().replace(",", ""))
        self._followersCount = int(x.Find("//li[@class='followers']/span[2]").Text().replace(",", ""))
        self._friendsCount = int(x.Find("//li[@class='following']/span[2]").Text().replace(",", ""))
        self._statusesCount = int(x.Find("//li[@class='posts']/span[2]").Text().replace(",", ""))

        # Lg.Trace({
        #     "name": self._name,
        #     "location": self._location,
        #     "registerTime": self._registerTime,
        #     "description": self._description,
        #     "url": self._url,
        #     "favoriteCount": self._favoriteCount,
        #     "followersCount": self._followersCount,
        #     "friendsCount": self._friendsCount,
        #     "statusesCount": self._statusesCount,
        # })
    
    def setInfo(self):
        Lg.Trace("当前ntucache的size:", len(ntucache))

        while ntucache[self.ScreenName]['updating'] and Time.Now() - ntucache[self.ScreenName]['startupdate'] < 300:
            Time.Sleep(0.3)

        ntucache[self.ScreenName]['updating'] = True 
        ntucache[self.ScreenName]['startupdate'] = Time.Now()

        url = self.twitter.server + "/" + self.ScreenName
        
        html = self.twitter.getHTML(url)
        self.raw_data = html

        self.setInfoByHtml(html)

        self.infoHasBeenSet = True

        ntucache[self.ScreenName] = {
            "obj": self, 
            "updating": False,
            "lastupdate": Time.Now(),
            'startupdate': 0
        }

    def getProperty(self, name:str) -> typing.Any:
        # 如果无数据且没解析
        if getattr(self, name) == None and not self.infoHasBeenSet:
            # 如果缓存也没有, 则解析
            if getattr(ntucache[self.ScreenName]['obj'], name) == None:
                self.setInfo()
            else:
                # 如果缓存有, 但是过期了, 则解析
                if Time.Now() - ntucache[self.ScreenName]['lastupdate'] > 86400:
                    self.setInfo()
                else:
                    # 否则用缓存更新自己
                    self = ntucache[self.ScreenName]['obj']
        else:
            # 如果有数据, 但是过期了, 则解析
            if Time.Now() - ntucache[self.ScreenName]['lastupdate'] > 86400:
                self.setInfo()
            else:
                # 否则用缓存更新自己
                self = ntucache[self.ScreenName]['obj']
        
        # 返回最新结果
        return getattr(self, name)
    
    @property
    def Name(self):
        return self.getProperty("_name")
    
    @property
    def Location(self):
        return self.getProperty("_location")
    
    @property
    def Verified(self):
        return self.getProperty("_verified")
    
    @property
    def RegisterTime(self):
        return self.getProperty("_registerTime")
    
    @property
    def Description(self):
        return self.getProperty("_description")
    
    @property
    def URL(self):
        return self.getProperty("_url")

    @property
    def FavoriteCount(self):
        return self.getProperty("_favoriteCount")
    
    @property
    def FollowersCount(self):
        return self.getProperty("_followersCount")
    
    @property
    def FriendsCount(self):
        return self.getProperty("_friendsCount")
    
    @property
    def StatusesCount(self):
        return self.getProperty("_statusesCount")
    
    def __repr__(self) -> str:
        return f"NitterTwitterUser(Name={self.Name} ScreenName={self.ScreenName} Location={self.Location} RegisterTime={self.RegisterTime} URL={self.URL} Description={self.Description} FollowersCount={self.FollowersCount} StatusesCount={self.StatusesCount} FavoriteCount={self.FavoriteCount} Verified={self.Verified})"

    def __str__(self) -> str:
        return self.__repr__()
    
    def getTimelineTweetsByHtmlByXPath(self, html:str) -> list[NitterTweet] | None:
        x = Tools.XPath(html)

        nts = []

        for idx in Range(1, 99):
            tlx = x.Find(f"//div[@class='timeline']/div[{idx}]")

            # Lg.Trace("idx:", idx)

            # ipdb.set_trace()

            # weburl = 'https://twitter.com/' + x.Find(tlx + "/a").Attribute("href")
            # if x.Find(tlx + "/div/div[1]/div[1]").Attribute("class") in ["pinned", "retweet-header"]:
            #     continue 

            if tlx.Find("//div[@class='retweet-header']") != None:
                Lg.Trace("跳过转推")
                continue 

            if tlx.Find("//div[@class='pinned']") != None:
                Lg.Trace("跳过pinned")
                continue 

            if tlx.Find(f"//a[@href='/{self.ScreenName}']") != None and tlx.Find(f"//a[@href='/{self.ScreenName}']").Text() == "Load newest":
                Lg.Trace("跳过Load newest")
                continue

            if tlx.Find("//div[@class='show-more']") != None:
                break 

            if tlx.Find(f"//h2[@class='timeline-end']") != None and tlx.Find(f"//h2[@class='timeline-end']").Text() == "No more items":
                Lg.Trace("没有更多元素")
                break

            # ipdb.set_trace()

            # if tlx.Find("//a[@class='tweet-link']") == None:
            #     ipdb.set_trace()

            nt = self.twitter.getTweetFromXPathSection(tlx)

            nts.append(nt)

            # ipdb.set_trace()

            # Lg.Trace({
            #     "tid": tid,
            #     "username": name,
            #     "screenname": self.ScreenName,
            #     "text": text,
            #     "time": time,
            #     "comment": comment, 
            #     "retweet": retweet,
            #     "quota": quota,
            #     "like": like
            # })
            # break 

        return nts

    def getTimelineTweetsByHtml(self, html:str) -> list[NitterTweet]:
        return self.getTimelineTweetsByHtmlByXPath(html) 
    
    def getTimelineNextPageLinke(self, html:str) -> str | None:
        x = Tools.XPath(html)

        if x.Find("//div[@class='show-more']/a") == None:
            return None 
        
        return self.twitter.server + "/" + self.ScreenName + x.Find("//div[@class='show-more']/a").Attribute('href')
    
    def Tweets(self) -> typing.Iterator[NitterTweet]:
        url = self.twitter.server + "/" + self.ScreenName

        pgcount = 1
        while True:
            Lg.Trace('pgcount:', pgcount)
            html = self.twitter.getHTML(url)

            if self.infoHasBeenSet == False:
                self.setInfoByHtml(html)

            for t in self.twitter.getTweetInHtml(html):
                yield t

            url = self.getTimelineNextPageLinke(html)

            if url == None:
                break 

            pgcount += 1

class NitterTweet():
    def __init__(self) -> None:
        self.ID:int = None
        # self.User:NitterTwitterUser = None 
        self.Time:int = None 
        self.Text:str = None 
        self.FavoriteCount:int = None 
        self.RetweetCount:int = None 
        self.CommentCount:int = None 
        self.URL:str = None 
        self.raw_data:str = None 
        
        # self.in_reply_to_tweet_id:int = None
        self.twitter:Nitter = None
        self._userScreenName:str = None  
    
    @property
    def User(self):
        return self.twitter._getUser(self._userScreenName)

    def __repr__(self) -> str:
        datetime = Time.Strftime(self.Time)
        return f"NitterTweet(ID={self.ID} Time={datetime}({self.Time}) Text={self.Text} User={self.User} FavoriteCount={self.FavoriteCount} RetweetCount={self.RetweetCount} CommentCount={self.CommentCount} URL={self.URL})"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def getRepliesTweetsByHtml(self, html:str) -> list[NitterTweet]:
        x = Tools.XPath(html)

        # rtx = x.Find("//div[@class='replies']")

        nts = []

        for idx in Range(1, 99):
            tlx = x.Find(f"//div[@class='replies']/div[{idx}]/div[1]")

            Lg.Trace("idx:", idx)

            # ipdb.set_trace()

            if tlx == None:
                break 

            # ipdb.set_trace()

            # if tlx.Find("//a[@class='tweet-link']") == None:
            #     ipdb.set_trace()

            nt = self.twitter.getTweetFromXPathSection(tlx)

            nts.append(nt)
        
        return nts

    def getRepliesNextPageLinkByHtml(self, html:str) -> str | None:
        x = Tools.XPath(html)

        if x.Find("//div[@class='show-more']/a") != None:
            smx = x.Find("//div[@class='show-more']/a").Attribute("href") 

            return f"{self.twitter.server}/{self.User.ScreenName}/status/{self.ID}{smx}"
        else:
            return None 
    
    def Replies(self) -> typing.Iterator[NitterTweet]:
        url = f"{self.twitter.server}/{self.User.ScreenName}/status/{self.ID}#m"

        while True:
            html = self.twitter.getHTML(url)

            for t in self.getRepliesTweetsByHtml(html):
                yield t 

            url = self.getRepliesNextPageLinkByHtml(html)

            Lg.Trace("Next URL:", url)

            if url == None:
                break 

class Nitter():
    def __init__(self, server:str=None, proxy:str=None, tor:bool=False) -> None:
        """
        proxy可以是http://或者https://以及socks5://
        如果是socks5且启用了tor需要做域名的远程解析 -> socks5h://
        """
        self.tor = tor 
        self.proxy = proxy

        self.servers = None

        if server != None:
            self.server = server.rstrip("/") 

            if not self.server.startswith("http://") and not self.server.startswith("https://"):
                self.server = 'http://' + self.server
        else:
            self.servers = self.getServers()
            self.selectServer(self.servers)

    def _getUser(self, screenName:str) -> NitterTwitterUser:
        if screenName in ntucache:
            return ntucache[screenName]["obj"]
        else:
            ntu = NitterTwitterUser()
            ntu.ScreenName = screenName 
            ntu.twitter = self

            ntucache[screenName] = {'obj': ntu, 'updating': False, 'lastupdate': 0, "startupdate": 0}

            return ntu
    
    def getServers(self) -> list[str]:
        servers = ['https://nitter.net']

        Lg.Trace("获取服务器列表...")
        try:
            url = 'https://raw.githubusercontent.com/wiki/zedeus/nitter/Instances.md'

            data = Http.Get(url).Content

            for i in String(data).RegexFind(r"\| *\[.+\]\((.+?)\).+?\| *:white_check_mark: *\| *:white_check_mark: *\|"):
                servers.append(i[1])
            
            Lg.Trace("获取到公网服务器列表个数:", len(servers) - 1)

            if self.tor == True:
                Lg.Trace("Tor已启用")
                for i in String(data).RegexFind(r"\| *<(http://.+?.onion)> *\| *:white_check_mark: *\|"):
                    servers.append(i[1])
                
                Lg.Trace("获取到tor网络的服务器列表个数:", len([i for i in filter(lambda x: 'onion' in x, servers)]))
        except Exception as e:
            Lg.Trace("获取服务器出错:", e)

        return servers

    def selectServer(self, servers:list[str]):
        servers = Random.Shuffle(servers)

        for server in servers:
            self.server = server.rstrip("/") 

            if not self.server.startswith("http://") and not self.server.startswith("https://"):
                self.server = 'http://' + self.server

            Lg.Trace("测试采集信息:", self.server)
            try:
                t = self.Search("SEC")
                Lg.Trace(next(t))

                Lg.Trace("使用服务器:", self.server)
                return 
            except Exception as e:
                # Lg.Error("出错了:", e)
                # import sys 
                # sys.exit()
                Lg.Trace("出错了:", e)
                Lg.Trace("测试下一个")
        
            # t = self.Search("SEC")
            # Lg.Trace(next(t))

            # Lg.Trace("使用服务器:", server)

        Lg.Trace("没有更多可以测试的服务器")
        
        raise Exception("没有合适的服务器") 

        

        
    
    def getTweetInHtml(self, html:str) -> list[NitterTweet] | None:
        x = Tools.XPath(html)

        nts = []

        for idx in Range(1, 99):
            tlx = x.Find(f"//div[@class='timeline']/div[{idx}]")

            # if tlx == None:
            #     break 

            if tlx.Find("//h2[@class='timeline-none']") != None:
                Lg.Trace("没有更多的推文")
                break 

            if tlx.Find("//div[@class='unavailable-box']") != None and tlx.Find("//div[@class='unavailable timeline-item']") != None:
                raise Exception("搜索不可用")

            # Lg.Trace("idx:", idx)

            # import ipdb
            # ipdb.set_trace()

            # weburl = 'https://twitter.com/' + x.Find(tlx + "/a").Attribute("href")
            # if x.Find(tlx + "/div/div[1]/div[1]").Attribute("class") in ["pinned", "retweet-header"]:
            #     continue 

            # if tlx.Find("//div[@class='retweet-header']") != None:
            #     Lg.Trace("跳过转推")
            #     continue 

            if tlx.Find("//div[@class='pinned']") != None:
                Lg.Trace("跳过pinned")
                continue 
            
            if hasattr(self, 'ScreenName'):
                if tlx.Find(f"//a[@href='/{self.ScreenName}']") != None and tlx.Find(f"//a[@href='/{self.ScreenName}']").Text() == "Load newest":
                    Lg.Trace("跳过Load newest")
                    continue
            
            if tlx.Find("//div[@class='timeline-item show-more']") and tlx.Find("//a").Text() == "Load newest":
                Lg.Trace("跳过Load newest")
                continue

            if tlx.Find("//div[@class='show-more']") != None:
                Lg.Trace("到达末尾")
                break 

            if tlx.Find(f"//h2[@class='timeline-end']") != None and tlx.Find(f"//h2[@class='timeline-end']").Text() == "No more items":
                Lg.Trace("没有更多元素")
                break

            # ipdb.set_trace()

            # if tlx.Find("//a[@class='tweet-link']") == None:
            #     ipdb.set_trace()

            nt = self.getTweetFromXPathSection(tlx)

            nts.append(nt)

            # ipdb.set_trace()

            # Lg.Trace({
            #     "tid": tid,
            #     "username": name,
            #     "screenname": self.ScreenName,
            #     "text": text,
            #     "time": time,
            #     "comment": comment, 
            #     "retweet": retweet,
            #     "quota": quota,
            #     "like": like
            # })
            # break 

        return nts
    
    def getSeachedNextPageLink(self, html:str) -> str | None:
        url = String(html).RegexFind('<div class="show-more"><a href="(.+?)">Load more</a></div>')
        if len(url) == 0:
            return None   

        return self.server + "/search" + String(url[0][1]).HTMLDecode()

    def getHTML(self, url:str) -> str:
        # headers = {
        #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        #     "Connection": "keep-alive",
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        #     "Sec-Fetch-Site": "none",
        #     "Sec-Fetch-Mode": "navigate",
        #     "Sec-Fetch-User": "?1",
        #     "Sec-Fetch-Dest": "document",
        #     "Accept-Encoding": "deflate",
        #     "Accept-Language": "en-CA,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-GB;q=0.6,en-US;q=0.5,ur;q=0.4",
        # }
        # resp = Http.Get(url, headers=headers)
        # import traceback
        # traceback.print_stack()

        while True:
            try:
                Lg.Trace('获取页面:', url)
                resp = Http.Get(url, proxy=self.proxy)
                if resp.StatusCode != 200:
                    raise Exception(f"HTTP状态码为{resp.StatusCode}: {url}")
                
                return resp.Content
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                Lg.Trace("出错了:", e)
                Lg.Trace("尝试另一个服务器")
                if self.servers != None:
                    self.selectServer(self.servers)

    def Search(self, key:str, sincetime:int|float=None, untiltime:int|float=None) -> typing.Iterator[NitterTweet]:
        """
        sincetime是起始的时间戳, 最早的推文, 最旧的
        untiletime是结束的时间戳, 最晚的推文, 最新的
        返回的时候是从新到旧的开始
        注意: 不采集retweets. 因为没办法获取到转推的用户的信息. 
        """

        key = key + " -filter:retweets"

        lastuntiltime = None 
        while True:
            url = self.server + "/search?f=tweet&q=" + String(key).URLEncode()

            if untiltime != None:
                ____uuuu = Time.Strftime(untiltime, "%Y-%m-%d")
                Lg.Trace(f"untiltime: {____uuuu}")
                url = url + f"&until={____uuuu}"
                lastuntiltime = untiltime   

            tcount = 0
            while True:
                # 有时候一个url要多get几次才会回复tweets
                for cidx in Range(5):
                    html = self.getHTML(url)

                    for t in self.getTweetInHtml(html):
                        if sincetime != None:
                            if t.Time < sincetime:
                                return 
                            
                        yield t 
                        tcount += 1

                        if untiltime == None:
                            untiltime = t.Time 
                        else:
                            if t.Time < untiltime:
                                untiltime = t.Time
                    
                    if tcount != 0:
                        break 
                    else:
                        Lg.Trace("Confirm:", cidx)
                        Time.Sleep(1)

                url = self.getSeachedNextPageLink(html)

                Lg.Trace("Next URL:", url)

                if url == None:
                    Lg.Trace("没有下一页")
                    break 
        
            Lg.Trace(f"tcount: {tcount}")
            Lg.Trace(f"untiltime: {untiltime}")
            Lg.Trace(f"lastuntiltime: {lastuntiltime}")
            if tcount == 0 and untiltime == lastuntiltime:
                break
    
    def User(self, screenName:str) -> NitterTwitterUser:
        if screenName in ntucache:
            ntu = ntucache[screenName]['obj']
        else:
            ntu = NitterTwitterUser()
            ntu.ScreenName = screenName
            ntu.twitter = self

            ntucache[screenName] = {
                "obj": ntu, 
                "updating": False,
                "lastupdate": 0,
                "startupdate": 0
            }

        return ntu
    
    def getTweetFromXPathSection(self, tlx:Tools.XPath) -> NitterTweet:
        tid = int(tlx.Find("//a[@class='tweet-link']").Attribute("href").split('#')[0].split('/')[-1])
        
        # text = String(tlx.Find("//div[@class='tweet-content media-body']").Html()).Html2Markdown()

        html = String(tlx.Find("//div[@class='tweet-content media-body']").Html()).HTMLDecode()
        soup = BeautifulSoup(html, 'html.parser')
        html = str(soup)
        for a in soup.find_all('a'):
            url = a.get("href")
            if url.startswith('/'):
                # Lg.Trace("----------")
                # Lg.Trace(1, html)
                # Lg.Trace(2, str(a))
                html = html.replace(str(a), String(a).RemoveHTMLTags())
        
        text = String(html).HTML2Markdown()
        
        # import ipdb
        # ipdb.set_trace()

        time = Time.Strptime(tlx.Find("//span[@class='tweet-date']/a").Attribute("title"), "%b %d, %Y · %I:%M %p UTC")
            
        comment = tlx.Find("//div[@class='tweet-stats']/span[1]").Text().strip().replace(',', '')
        comment = int(comment) if String(comment).IsDigit() else 0

        retweet = tlx.Find("//div[@class='tweet-stats']/span[2]").Text().strip().replace(',', '')
        retweet = int(retweet) if String(retweet).IsDigit() else 0

        quota = tlx.Find("//div[@class='tweet-stats']/span[3]").Text().strip().replace(',', '')
        quota = int(quota) if String(quota).IsDigit() else 0

        like = tlx.Find("//div[@class='tweet-stats']/span[4]").Text().strip().replace(",", "")
        like = int(like) if String(like).IsDigit() else 0

        # username = tlx.Find("//a[@class='fullname']").Text()
        screenname = tlx.Find("//a[@class='username']").Text()[1:]

        weburl = f"https://twitter.com/{screenname}/status/{tid}"
        # ipdb.set_trace()

        # Lg.Trace({
        #     "tid": tid,
        #     # "username": username,
        #     "screenname": screenname,
        #     "text": text,
        #     "time": time,
        #     "comment": comment, 
        #     "retweet": retweet,
        #     "quota": quota,
        #     "like": like
        # })

        nt = NitterTweet()
        nt.ID = tid
        nt.CommentCount = comment
        nt.FavoriteCount = like
        nt.RetweetCount = retweet
        nt.Text = text 
        nt.Time = time 
        nt.twitter = self
        nt.URL = weburl
        nt.raw_data = tlx.Html()
        nt._userScreenName = screenname

        return nt
    
    def getMainThreadInTweetPage(self, html:str) -> NitterTweet:
        x = Tools.XPath(html)

        tlx = x.Find("//div[@class='main-thread']") 

        return self.getTweetFromXPathSection(tlx)

    def Tweet(self, tid:int) -> NitterTweet:
        url = f"{self.server}/any_username/status/{tid}#m"

        html = self.getHTML(url)

        t = self.getMainThreadInTweetPage(html)
        t.ID = int(tid)

        return t

if __name__ == "__main__":
    # --- 联调所有
    n = Nitter()

    ntu = n.User("VenomApe_NFT")
    Lg.Trace(ntu)

    for t in ntu.Tweets():
        Lg.Info(Time.Strftime(t.Time), t.URL)

    for t in n.Search("psychologist a paradox"):
        Lg.Trace("psychologist a paradox", Time.Strftime(t.Time), t.URL)

    count = 0
    for t in n.Search("musk"):
        Lg.Trace("musk", Time.Strftime(t.Time), t.URL)
        count += 1

        if count > 20:
            break

    for t in n.Tweet("RDelaney", 1679898053631782924).Replies():
        Lg.Trace(t.ID)

    # --- 联调 tweet replies

    n = Nitter("nitter.kavin.rocks")

    for t in n.Tweet("RDelaney", 1679898053631782924).Replies():
        Lg.Trace(t.ID)

    # --- 测试 tweet replies

    html = File("tweet.detail.single.html").Read()
    n = Nitter("nitter.kavin.rocks")

    t = n.getMainThreadInTweetPage(html)
    t.ID = 1681734275589189634

    # replies = t.getRepliesTweetsByHtml(html)
    nextlink = t.getRepliesNextPageLinkByHtml(html)

    Lg.Trace(nextlink)

    # --- 测试获取单条 tweet 

    # 翻页的第一页
    html = Http.Get("https://nitter.kavin.rocks/cz_binance/status/1681734275589189634").Content
    File("tweet.detail.html").Write(html)

    # 翻页的第二页
    html = Http.Get("https://nitter.kavin.rocks/cz_binance/status/1681734275589189634?cursor=SQAAAPAMHBl2jIC9yaig3NYugICzpa-h3NYugoCxkaOoEgDxCMDSjbHJ3dYuhIC-raSi3NYuisDTjbiiLQDgsMWiotzWLiUCEhUEAAA#r").Content
    File("tweet.detail.1.html").Write(html)

    # 只有一页
    html = Http.Get("https://nitter.kavin.rocks/RDelaney/status/1679898053631782924#m").Content
    File("tweet.detail.single.html").Write(html)

    html = File("tweet.detail.html").Read()

    n = Nitter("nitter.kavin.rocks")
    # # t = n.getMainThreadInTweetPage(html)

    t = n.Tweet(1651414032925204480)

    Lg.Trace(t)

    # --- 测试获取服务器列表

    n = Nitter()
    servers = n.getServers()
    n.selectServer(servers)

    # --- 联调 timeline

    n = Nitter("nitter.kavin.rocks")
    n = Nitter('nitter.net')

    ntu = n.User("VenomApe_NFT")

    for t in ntu.Tweets():
        Lg.Info(Time.Strftime(t.Time), t.URL)

    # --- 调试 timeline 翻页链接

    n = Nitter("nitter.kavin.rocks")

    ntu = n.User("blahlaja")
    html = File("user.1.html").Read()

    link = ntu.getTimelineNextPageLinke(html)

    Lg.Trace(link)

    # ---- 调试 NitterTwitterUser - Timeline

    n = Nitter("nitter.kavin.rocks")

    ntu = n.User("blahlaja")
    html = File("user.2.html").Read()

    ntu.getTimelineTweetsByHtml(html)

    # ---- 联调 NitterTwitterUser, 从tweets里面 - info

    # 1

    n = Nitter("nitter.kavin.rocks")
    for t in n.Search("psychologist a paradox"):
        Lg.Trace(t.ID)

    Lg.Trace(t.User)

    # ---- 调试 NitterTwitterUser - info 

    n = Nitter("nitter.kavin.rocks")

    # Lg.Trace(ntu)
    ntu = n.User("blahlaja")

    # html = File("user.4.verified.html").Read()
    html = File("user.html").Read()

    # ntu = n.User("binsingha")
    # html = File("user.1.html").Read()

    ntu.setInfoByHtml(html)

    Lg.Trace(ntu)

    # ---- 调试 NitterTwitterUser - info

    # 活动频繁, 好多转推
    html = Http.Get("https://nitter.kavin.rocks/blahlaja").Content
    File("user.html").Write(html)

    # 活动频繁
    html = Http.Get("https://nitter.kavin.rocks/ShytoshiKusama").Content
    File("user.2.html").Write(html)

    # 没有推文
    html = Http.Get("https://nitter.kavin.rocks/binsingha").Content
    File("user.1.html").Write(html)

    html = File("user.1.html").Read()

    ntu = NitterTwitterUser()
    ntu.setInfoByHtml(html)

    # ---- 联调 Search 

    n = Nitter("nitter.kavin.rocks")

    for t in n.Search("psychologist a paradox"):
        Lg.Trace(t)

    # ---- 调试 Search  

    n = Nitter("nitter.kavin.rocks")
    
    html = File("search.retweet.html").Read()

    for i in n.getTweetInHtml(html):
        Lg.Trace(i)

    # 其他

    html = Http.Get("https://nitter.kavin.rocks/search?f=tweets&q=Si+on+prend+l%27argent+de+Musk%2C+Bezos+et+Arnault+et+qu%27on+le+redistribue+entre").Content
    html = Http.Get("https://nitter.kavin.rocks/blahlaja").Content
    html = Http.Get("https://nitter.kavin.rocks/cz_binance/status/1651414032925204480#m").Content
    File("tweet.url.in.text.html").Write(html)