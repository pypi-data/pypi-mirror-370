import tweepy
import typing 

tweetFields = ['author_id', 'created_at', 'geo', 'id', 'lang', 'text']

#print("load " + '/'.join(__file__.split('/')[-2:]))

class EssentialTweet():
    def __init__(self) -> None:
        self.ID:int = None
        self.Time:int = None 
        self.Text:str = None 
        self.Language:str = None 
    
    def __repr__(self) -> str:
        return f"EssentialTweet(ID={self.ID} Time={self.Time} Language={self.Language} Text={self.Text})"
    
    def __str__(self) -> str:
        return f"EssentialTweet(ID={self.ID} Time={self.Time} Language={self.Language} Text={self.Text})"

class Essential():
    def __init__(self, bearerToken:str) -> None:
        self.api = tweepy.Client(bearer_token=bearerToken, wait_on_rate_limit=True)

    def _wrapStatus(self, status) -> EssentialTweet:
        t = EssentialTweet()

        t.ID = status.id 
        t.Time = int(status.created_at.timestamp())

        t.Text = status.text

        t.Language = status.lang

        return t
    
    def Search(self, keyword:str, sinceID:int=None, tweetPerRequest:int=10) -> typing.Iterable[EssentialTweet]:
        tweets = tweepy.Paginator(self.api.search_recent_tweets, query=keyword, since_id=sinceID, tweet_fields=tweetFields, max_results=tweetPerRequest).flatten()
        for status in tweets:
            yield self._wrapStatus(status)
    
    def Timeline(self, screename:str, sinceID:int=None, tweetPerRequest:int=10) -> typing.Iterable[EssentialTweet]:
        u = self.api.get_user(username=screename)
        if len(u.errors) != 0:
            raise Exception("User not exists: " + screename)

        tweets = tweepy.Paginator(self.api.get_users_tweets, id=u.data.id, since_id=sinceID, tweet_fields=tweetFields, max_results=tweetPerRequest).flatten()
        for status in tweets:
            yield self._wrapStatus(status)

if __name__ == "__main__":
    t = Essential(twitterBearerToken)

    t.Timeline("EtherChecker")

    count = 0
    for tt in t.Timeline("EtherChecker"):
        print(tt)
        count += 1
        if count > 30:
            break 