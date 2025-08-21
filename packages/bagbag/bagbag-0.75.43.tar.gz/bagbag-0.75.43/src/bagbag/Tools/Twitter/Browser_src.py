from ... import Time, Tools, Json, Lg, String

from . import Utils

import typing 
import ipdb

class BrowserTweet():
    def __init__(self) -> None:
        self.User:str = None # Screen Name 
        self.Time:int = None 
        self.Text:int = None 
        self.URL:str = None 
    
    def __str__(self) -> str:
        time = Time.Strftime(self.Time)
        return f"BrowserTweet(User={self.User} Time={time} Text={self.Text})"

    def __repr__(self) -> str:
        return self.__str__()

class BrowserTwitterUser():
    def __init__(self) -> None:
        # https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/user
        self.ID:int = None 
        self.Name:str = None 
        self.ScreenName:str = None 
        self.Location:str = None 
        self.RegisterTime:int = None 
        self.Description:str = None 
        self.URL:str = None
        self.FollowersCount:int = None 
        self.StatusesCount:int = None 
        self.Verified:bool = None 
        self.ListedCount:int = None 
        self.FavoriteCount:int = None 
        self.FriendsCount:int = None # 当前用户去follow别人的个数
        self.raw_data:dict = None 

    def __repr__(self) -> str:
        return f"BrowserTwitterUser(ID={self.ID} Name={self.Name} ScreenName={self.ScreenName} Location={self.Location} RegisterTime={self.RegisterTime} URL={self.URL} Description={self.Description} FollowersCount={self.FollowersCount} StatusesCount={self.StatusesCount} Verified={self.Verified} ListedCount={self.ListedCount} FavoriteCount={self.FavoriteCount})"

    def __str__(self) -> str:
        return f"BrowserTwitterUser(ID={self.ID} Name={self.Name} ScreenName={self.ScreenName} Location={self.Location} RegisterTime={self.RegisterTime} URL={self.URL} Description={self.Description} FollowersCount={self.FollowersCount} StatusesCount={self.StatusesCount} Verified={self.Verified} ListedCount={self.ListedCount} FavoriteCount={self.FavoriteCount})"

class Browser():
    def __init__(self, cookie:str=None, proxy:str=None) -> None:
        self.cookie = cookie
        self.proxy = proxy 
        self.requestStorage = "memory"
        self.maxRequests = 500
        self.se = Tools.Selenium.ChromeWire(
            randomUA=False, 
            requestStorage=self.requestStorage, 
            maxRequests=self.maxRequests, 
            httpProxy=self.proxy
        )

    def twitterSearchResultParser(self, j:dict) -> list[dict]:
        if 'globalObjects' not in j:
            return []
        
        if 'tweets' not in j['globalObjects'] or 'users' not in j['globalObjects']:
            return []

        tweets = j['globalObjects']['tweets']
        users = j['globalObjects']['users']

        res = []
        for tidx in tweets:
            tweet = tweets[tidx]

            # 采集数据
            time = tweet['created_at']
            text = tweet['full_text']

            uid = tweet['user_id_str']

            user = None 
            for uidx in users:
                if uid == users[uidx]['id_str']:
                    user = users[uidx]['screen_name']
                    break 
    
            # 处理数据
            time = Time.Strptime(time)

            # 存储
            res.append({
                "user": user,
                "time": time,
                "text": text,
                "url": f"https://twitter.com/{user}/status/{tidx}"
            })
        
        return res 

    def fetchTweet(self) -> list[dict]:
        resp = []
        for flow in self.se.Flows():
            # if not Tools.URL(flow.Request.URL).Parse().Host in ['api.twitter.com']:
            #     continue  
            # if not Tools.URL(flow.Request.URL).Parse().Path.endswith("adaptive.json"):
            #     continue 

            path = Tools.URL(flow.Request.URL).Parse().Path

            # if path in ['/i/api/2/guide.json']:
            #     continue

            if path != "/i/api/2/search/adaptive.json":
                continue

            try:
                content = Json.Loads(flow.Response.Body)
            except Exception as e:
                # Lg.Trace("错误载入json:", flow.Request.URL)
                # ipdb.set_trace()
                continue
            
            # Lg.Trace("载入json成功:", flow.Request.URL)
            for i in self.twitterSearchResultParser(content) :
                resp.append(i)
                Lg.Trace(f"有推文的url: {path} \n {i}")
        
        return resp 

    def Search(self, query:str, since:int=None, until:int=None, stype:str="top") -> typing.Iterator[BrowserTweet]:
        """
        This function searches for tweets on Twitter based on a query, time range, and search type, and
        returns an iterator of the resulting tweets.
        在stype为top的时候可能返回重复的推文
        
        :param query: The search query to be used for searching tweets
        :type query: str
        :param since: The "since" parameter is not used in the code provided. It is not clear what it is
        intended to represent without further context
        :type since: int
        :param until: The "until" parameter is used to specify the latest date (in Unix timestamp
        format) for the tweets to be searched. Only tweets posted before this date will be included in
        the search results
        :type until: int
        :param stype: The type of search results to be returned. 可以是top或者live
        :type stype: str (optional)
        """

        if since != None and type(since) not in [int, float]:
            raise Exception("since需要为数字")
        
        if until != None and type(until) not in [int, float]:
            raise Exception("until需要为数字")

        baseurl = 'https://twitter.com/search?q=%s&src=recent_search_click&f=' + stype

        if until != None:
            lastestTime = until 
        else:
            lastestTime = Time.Now()

        if self.cookie == None:
            raise Exception("搜索需要使用cookie")

        try:
            self.se.SetCookie(self.cookie)
        except:
            self.se.Get("https://twitter.com")
            self.se.SetCookie(self.cookie)

        while True:
            utildate = Time.Strftime(lastestTime, "%Y-%m-%d")
            q = query + f" until:{utildate}"

            Lg.Info("Search:", q)
            u = baseurl % String(q).URLEncode()

            Lg.Trace("URL:", u)
            self.se.Get(u)

            Time.Sleep(5, bar=True, title="等待页面加载")

            empty = 0
            tweetscount = 0
            while True:
                tweets = self.fetchTweet()

                if len(tweets) == 0:
                    if f'No results for "{q}"'.lower() in self.se.PageSource().lower():
                        Lg.Trace("无搜索结果")
                        return 
                    
                    empty += 1
                    Lg.Trace("empty result")
                    if empty > 5:
                        Lg.Trace("break")
                        break 
                else:
                    empty = 0

                for i in tweets:
                    bt = BrowserTweet()
                    bt.User = i['user']
                    bt.Time = i['time']
                    bt.Text = i['text']
                    bt.URL = i['url']

                    Lg.Trace(bt)
                    
                    lastestTime = bt.Time
                    try:
                        if since != None and bt.Time < since:
                            Lg.Trace("到达since指定的日期:", Time.Strftime(since))
                            return 
                    except Exception as e:
                        Lg.Trace("since:", since)
                        Lg.Trace("bt.Time:", bt.Time)
                        Lg.Warn(e)
                    
                    tweetscount += 1
                    yield bt

                Lg.Trace("Scrool down")
                self.se.ScrollDown(6000)
                Time.Sleep(2)
                self.se.ScrollDown(6000)
                Time.Sleep(2)

            if tweetscount == 0:
                return 
    
    def _getUserInformationFlow(self, timeout:int=10) -> Tools.Selenium.SeleniumFlow | None:
        starttime = Time.Now()
        
        resflow = None 
        while True:
            for flow in self.se.Flows():
                if len(String(flow.Request.URL).RegexFind('https://twitter.com/i/api/graphql/.+?/UserByScreenName')) == 0:
                    continue 

                resflow = flow 
            
            if resflow != None:
                return resflow
            
            if Time.Now() - starttime > timeout:
                return None 

            Time.Sleep(0.1)

    def _user(self, screen_name:str, timeout:int=20) -> BrowserTwitterUser | None: 
        self.se.ClearIdent()

        while True:
            try:
                self.se.Get("https://twitter.com/" + screen_name) 
                break 
            except:
                Lg.Error("Get页面出错, 重试...")
                Time.Sleep(1)
                self.se.Close()
                self.se = Tools.Selenium.ChromeWire(
                    randomUA=False, 
                    requestStorage=self.requestStorage, 
                    maxRequests=self.maxRequests, 
                    httpProxy=self.proxy
                )

        Lg.Trace()

        starttime = Time.Now()
        while True:
            for flow in self.se.Flows():
                # Lg.Trace(flow.ID)
                try:
                    if len(String(flow.Request.URL).RegexFind('https://twitter.com/i/api/graphql/.+?/UserByScreenName')) == 0:
                        continue 
                    
                    Lg.Trace("找到URL:", flow.Request.URL)
                    j = Json.Loads(flow.Response.Body)
                    # 用户不存在
                    if len(j['data']) == 0:
                        Lg.Trace()
                        return None 
                    
                    r = j['data']['user']['result']
                    # 用户被停用
                    if '__typename' in r:
                        Lg.Trace()
                        if r['__typename'] == 'UserUnavailable':
                            Lg.Trace()
                            return None 

                    Lg.Trace()
                    u = r['legacy']

                    btu = BrowserTwitterUser()

                    btu.RegisterTime = Time.Strptime(u['created_at'])
                    btu.Description = u['description']
                    btu.FollowersCount = u['followers_count']
                    # data['friends_count'] = u['friends_count']
                    btu.FriendsCount = u['friends_count']
                    btu.StatusesCount = u['statuses_count']
                    btu.Verified = u['verified']
                    # if 'verified_type' in u:
                    #     data['verified_type'] = u['verified_type']
                    btu.Name = u['name']
                    btu.ScreenName = u['screen_name']
                    btu.Location = u['location']
                    btu.FavoriteCount = u['favourites_count']
                    btu.ListedCount = u['listed_count']

                    if 'profile_banner_url' in u:
                        Lg.Trace()
                        reres = String(u['profile_banner_url']).RegexFind('https://pbs.twimg.com/profile_banners/([0-9]+)/[0-9]+')
                        if len(reres) != 0:
                            Lg.Trace()
                            btu.ID = int(reres[0][1])
                    
                    if 'url' in u:
                        Lg.Trace()
                        if type(u['url']) == str:
                            Lg.Trace()
                            if u['url'].startswith("https://t.co/") or u['url'].startswith("http://t.co/"):
                                realurl = Utils.GetRealUrl(u['url'])
                                if realurl == None:
                                    btu.URL = u['url']
                                else:
                                    btu.URL = realurl
                            else:
                                btu.URL = u['url']
                        # btu.URL = u['url']

                    # Lg.Trace(u)

                    btu.raw_data = u

                    Lg.Trace()
                    # import ipdb
                    # ipdb.set_trace()

                    return btu
                except Exception as e:
                    Lg.Error()
                    # import ipdb
                    # ipdb.set_trace()
                    pass
            
            if Time.Now() - starttime > timeout:
                Lg.Trace("time out")
                # ipdb.set_trace()
                return "timeout" 

            Time.Sleep(0.1)
    
    def User(self, screen_name:str, timeout:int=20) -> BrowserTwitterUser | None: 
        if screen_name == None or screen_name == "":
            return None 
        
        for _ in range(5):
            Lg.Trace(f"尝试第{_}次")
            user = self._user(screen_name, timeout)
            if user == "timeout":
                self.se.Close()
                self.se = Tools.Selenium.ChromeWire(
                    randomUA=False, 
                    requestStorage=self.requestStorage, 
                    maxRequests=self.maxRequests, 
                    httpProxy=self.proxy
                )
            else:
                return user
                
    def Close(self):
        self.se.Close()

    def __enter__(self):
        return self 
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.Close()
        except:
            pass

if __name__ == "__main__":
    # b = Browser(twittercookie)
    # key = "RainUnlocks"
    # # key = "coinsbee"
    # for t in b.Search(key, Time.Now() - 86400 * 10):
    #     Lg.Trace(t)

    with Tools.Twitter.Browser() as tb:
        u = tb.User("RodrigoRochaCI")

        Lg.Trace(u)
