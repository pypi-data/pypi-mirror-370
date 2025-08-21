from bagbag import * 

class FearAndGreedIndexResult():
    def __init__(self) -> None:
        self.Score:int = None 
        self.Status:str = None 
        self.NextUpdateRemainSeconds:int = None 
    
    def __repr__(self) -> str:
        # ipdb.set_trace()
        # Lg.Trace(self.__dir__())
        # Lg.Trace([i for i in filter(lambda attr: attr[0].isupper() and type(getattr(self, attr)) in [int, float, str], self.__dir__())])
        return f"{self.__class__.__name__}(%s)" % ' '.join([f"{attr}={getattr(self, attr)}" for attr in filter(lambda attr: attr[0].isupper() and type(getattr(self, attr)) in [int, float, str], self.__dir__())])

    def __str__(self) -> str:
        return self.__repr__()

def FearAndGreedIndex() -> FearAndGreedIndexResult:
    html = Http.Get("https://alternative.me/crypto/fear-and-greed-index/").Content
    x = Tools.XPath(html)

    status = str(x.Find("/html/body/div/main/section/div/div[3]/div[2]/div/div/div[1]/div[1]/div[2]").Text())
    score = int(x.Find("/html/body/div/main/section/div/div[3]/div[2]/div/div/div[1]/div[2]/div").Text())
    nextupdate = int(x.Find("//countdown").Attribute(":time").split(" ")[0])

    # Lg.Trace(type(value))

    fagir = FearAndGreedIndexResult()
    fagir.Score = score
    fagir.Status = status
    fagir.NextUpdateRemainSeconds = nextupdate

    return fagir

if __name__ == "__main__":
    f = FearAndGreedIndex()
    Lg.Trace(f)