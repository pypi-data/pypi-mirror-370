from __future__ import annotations
import tweepy
import typing 
from . import Utils

#print("load " + '/'.join(__file__.split('/')[-2:]))

class ElevatedTwitterUser():
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
        self.ListedCount:int = None # The number of public lists that this user is a member of.
        self.FavoriteCount:int = None 
        self.FriendsCount:int = None # 当前用户去follow别人的个数
        self.raw_data:dict = None 

    # def Tweet(self, )
        
    def __repr__(self) -> str:
        return f"ElevatedTwitterUser(ID={self.ID} Name={self.Name} ScreenName={self.ScreenName} Location={self.Location} RegisterTime={self.RegisterTime} URL={self.URL} Description={self.Description} FollowersCount={self.FollowersCount} StatusesCount={self.StatusesCount} Verified={self.Verified} ListedCount={self.ListedCount} FavoriteCount={self.FavoriteCount})"

    def __str__(self) -> str:
        return f"ElevatedTwitterUser(ID={self.ID} Name={self.Name} ScreenName={self.ScreenName} Location={self.Location} RegisterTime={self.RegisterTime} URL={self.URL} Description={self.Description} FollowersCount={self.FollowersCount} StatusesCount={self.StatusesCount} Verified={self.Verified} ListedCount={self.ListedCount} FavoriteCount={self.FavoriteCount})"

class ElevatedTwitterUserMention():
    def __init__(self) -> None:
        self.ScreenName:str = None 
        self.Name:str = None 
        self.ID:int = None 
    
    def __repr__(self) -> str:
        return f"ElevatedTwitterUserMention(ID={self.ID} ScreenName={self.ScreenName} Name={self.Name})"
    
    def __str__(self) -> str:
        return self.__repr__()

class ElevatedTweet():
    def __init__(self) -> None:
        self.ID:int = None
        self.User:ElevatedTwitterUser = None 
        self.Time:int = None 
        self.Text:str = None 
        self.Language:str = None 
        self.FavoriteCount:int = None 
        self.RetweetCount:int = None 
        self.Mentions:list[ElevatedTwitterUserMention] = []
        self.Urls:list[str] = []
        self.Media:list[str] = []
        self.Tag:list[str] = []
        self.WebURL:str = None 

        self.raw_data:dict = None
        
        self.in_reply_to_tweet_id:int = None
        self.twitter:Elevated = None 

    def __repr__(self) -> str:
        return f"ElevatedTweet(ID={self.ID} Time={self.Time} Language={self.Language} Text={self.Text} User={self.User} FavoriteCount={self.FavoriteCount} RetweetCount={self.RetweetCount} Mentions={self.Mentions} Urls={self.Urls} Media={self.Media} Tag={self.Tag} WebURL={self.WebURL})"
    
    def __str__(self) -> str:
        return self.__repr__()

    def InReplyToTweet(self) -> ElevatedTweet | None:
        if self.in_reply_to_tweet_id == None:
            return None 
        
        return self.twitter.Tweet(self.in_reply_to_tweet_id)

    def Replies(self, checkcount:int=None) -> typing.Iterator[ElevatedTweet]:
        """
        通过采集回复当前发这个推文的用户的推文, 来筛选这个推文是否是回复当前这条推文的推文.
        checkcount是最大采集多少条"回复当前发这个推文的用户的推文", 不是会返回的推文条数.
        """
        # print(75, "to:" + self.User.ScreenName)
        count = 0
        for t in self.twitter.Search("to:" + self.User.ScreenName):
            # print(77, t)
            # print(t.in_reply_to_status_id, self.ID)
            # print(type(t.in_reply_to_status_id), type(self.ID))
            if t.in_reply_to_tweet_id == self.ID:
                yield t
            # print('')
            count += 1
            if checkcount != None and count > checkcount:
                return 

class Elevated():
    def __init__(self, consumer_key:str, consumer_secret:str) -> None:
        auth = tweepy.OAuth2AppHandler(consumer_key, consumer_secret)

        self.api = tweepy.API(auth, wait_on_rate_limit=True)
    
    def _wrapUser(self, user) -> ElevatedTwitterUser:
        u = ElevatedTwitterUser()
        u.ID = user.id
        u.Name = user.name
        u.ScreenName = user.screen_name
        u.Location = user.location
        u.Description = user.description
        if type(user.url) == str:
            if user.url.startswith("https://t.co/") or user.url.startswith("http://t.co/"):
                realurl = Utils.GetRealUrl(user.url)
                if realurl == None:
                    u.URL = user.url
                else:
                    u.URL = realurl
            else:
                u.URL = user.url
        u.RegisterTime = int(user.created_at.timestamp())
        u.FollowersCount = user.followers_count
        u.StatusesCount = user.statuses_count
        u.Verified = user.verified
        u.ListedCount = user.listed_count
        u.FavoriteCount = user.favourites_count
        u.FriendsCount = user.friends_count
        u.raw_data = user._json

        # import ipdb
        # ipdb.set_trace()

        return u
    
    def _wrapStatus(self, status) -> ElevatedTweet:
        # import ipdb
        # ipdb.set_trace()
        u = self._wrapUser(status.author)

        t = ElevatedTweet()
        t.twitter = self
        t.User = u 

        t.ID = status.id # https://twitter.com/saepudin1991/status/1613434061741260803
        t.Time = int(status.created_at.timestamp())
        t.FavoriteCount = status.favorite_count
        t.RetweetCount = status.retweet_count
        t.raw_data = status._json

        if hasattr(status, 'in_reply_to_status_id_str'):
            t.in_reply_to_tweet_id = status.in_reply_to_status_id

        if hasattr(status, 'retweeted_status'):
            # 由于如果是转推, 那么status.full_text会被截断到140个字符, 而完整的推文在status.retweeted_status.full_text
            # 所以拼接一下
            sidx = 0
            foundsidx = False 
            while True:
                if sidx > 140 or status.full_text[sidx:-1] == "":
                    break 

                if status.full_text[sidx:-1] in status.retweeted_status.full_text:
                    foundsidx = True 
                    break 

                sidx += 1
            if foundsidx:
                text = status.full_text[:sidx] + status.retweeted_status.full_text
            else:
                text = status.full_text
        # 如果不是转推
        else:
            text = status.full_text
        t.Text = text

        t.Language = status.lang

        if hasattr(status, 'entities'):
            if 'user_mentions' in status.entities and len(status.entities['user_mentions']) != 0:
                for u in status.entities['user_mentions']:
                    tuum = ElevatedTwitterUserMention()

                    tuum.ID = u['id']
                    tuum.Name = u['name']
                    tuum.ScreenName = u["screen_name"]

                    t.Mentions.append(tuum)

            if 'urls' in status.entities and len(status.entities['urls']) != 0:
                for u in status.entities['urls']:
                    t.Urls.append(u['expanded_url'])

            if 'media' in status.entities and len(status.entities['media']) != 0:
                for u in status.entities['media']:
                    t.Media.append(u['media_url'])

            if 'hashtags' in status.entities and len(status.entities['hashtags']) != 0:
                for u in status.entities['hashtags']:
                    t.Tag.append(u['text'])
        
        t.WebURL = f"https://twitter.com/{t.User.ScreenName}/status/{t.ID}"

        return t
    
    def Search(self, keyword:str, includeReTweets:bool=False, days:int=7, countPerRequest:int=40, sinceID:int=None) -> typing.Iterable[ElevatedTweet]:
        """
        It takes a keyword, and returns an iterator of tweets that contain that keyword. 
        tweet的ID是从大到小, 也就是数据的时间是从近到远
        
        :param keyword: The keyword to search for
        :type keyword: str
        :param days: How many days back to search, defaults to 7
        :type days: int (optional)
        :param countPerRequest: The number of tweets to return per request. The maximum is 100, defaults
        to 40
        :type countPerRequest: int (optional)
        :param sinceID: The ID of the tweet to start from. If you want to start from the beginning, set
        this to None
        :type sinceID: int
        """
        if includeReTweets == False:
            keyword = keyword + " -filter:retweets"
            
        for status in tweepy.Cursor(self.api.search_tweets, q=keyword, tweet_mode='extended', count=countPerRequest, since_id=sinceID).items():
            # import ipdb
            # ipdb.set_trace()
            yield self._wrapStatus(status)
    
    def Timeline(self, screenameOrID:str|int, countPerRequest:int=40, sinceID:int=None, includeReTweets:bool=False) -> typing.Iterable[ElevatedTweet]:
        """
        tweet from the timeline of the user with the given screen name
        tweet的ID是从大到小, 也就是数据的时间是从近到远
        如果有sinceID, 就返回比这个sinceID更新的tweets, 不包括这个tweet
        
        :param screename: The screen name of the user
        :type screename: str
        :param countPerRequest: The number of tweets to return per request. The maximum is 200, defaults
        to 40
        :type countPerRequest: int (optional)
        :param sinceID: If you want to get tweets since a certain ID, you can use this
        :type sinceID: int
        """
        if type(screenameOrID) == str:
            for status in tweepy.Cursor(self.api.user_timeline, screen_name=screenameOrID, tweet_mode='extended', count=countPerRequest, since_id=sinceID, include_rts=includeReTweets).items():
                yield self._wrapStatus(status)
        elif type(screenameOrID) == int:
            for status in tweepy.Cursor(self.api.user_timeline, user_id=screenameOrID, tweet_mode='extended', count=countPerRequest, since_id=sinceID, include_rts=includeReTweets).items():
                yield self._wrapStatus(status)
    
    def Followers(self, screename:str, countPerRequest:int=40) -> typing.Iterable[ElevatedTwitterUser]:
        for user in tweepy.Cursor(self.api.get_followers, screen_name=screename, count=countPerRequest).items():
            # import ipdb
            # ipdb.set_trace()
            yield self._wrapUser(user)
    
    def User(self, screenameOrID:str|int) -> ElevatedTwitterUser | None:
        """
        It takes a screen name or id and returns a ElevatedTwitterUser object
        
        :param screename: The screen name of the user for whom to return results for
        :type screename: str
        :return: A ElevatedTwitterUser object
        """
        try:
            if type(screenameOrID) == str:
                user = self.api.get_user(screen_name=screenameOrID)
            elif type(screenameOrID) == int:
                user = self.api.get_user(user_id=screenameOrID)
            else:
                return None 
        except tweepy.errors.Forbidden as e:
            if 'User has been suspended' in str(e):
                return None 
            else:
                raise e
        except tweepy.errors.NotFound:
            return None 
            
        # import ipdb
        # ipdb.set_trace()
        return self._wrapUser(user)

    def Tweet(self, tid:int) -> ElevatedTweet:
        return self._wrapStatus(self.api.get_status(tid, tweet_mode = "extended"))

if __name__ == "__main__":
    from bagbag import Lg, Json

    cfg = Json.Loads(open('twitter.ident').read())

    twitter = Elevated(cfg['consumer_key'], cfg['consumer_secret'])

    # print("user")
    u = twitter.User("asiwaju_wa")
    # print(u)
    
    # print("search")
    # for i in twitter.Search("coinsbee"):
    #     print(i)
    #     break 

    # idx = 0
    # print('timeline')
    # for i in twitter.Timeline(722784576):
    #     idx += 1
    #     print(i.ID, i.Time, i.Text)
    #     if idx == 10:
    #         break 
    
    # print("followers")
    # for i in twitter.Followers("asiwaju_wa"):
    #     print(i)
    #     break 

    # t = twitter.Tweet(1660223526509625349)
    # Lg.Trace(t)

    # ts = t.Replies()
    # Lg.Trace(ts)

    # import ipdb
    # ipdb.set_trace()