
# from bagbag import Tools, String, Range, Funcs, Hash, Os, Lg
import typing 

#print("load " + '/'.join(__file__.split('/')[-2:]))

try:
    from .. import Tools
    from .. import String
    from ..Python import Range 
    from .. import Funcs 
    from .. import Hash 
    from .. import Os 
    from .. import Lg
except:
    import sys 
    sys.path.append("..")
    import Tools
    import String 
    from Python import Range 
    import Funcs 
    import Hash 
    import Os
    import Lg

class WebCrawlerResult:
    def __init__(self, URL:str="", PageSource:str="", Title:str=""):
        self.URL = URL 
        self.PageSource = PageSource
        self.Title = Title 
    
    def __repr__(self) -> str:
        pg = String(self.PageSource).Ommit(180).replace("\n", "\\n").replace("\t", "\\t")
        return f"WebCrawlerResult(URL={self.URL} Title={self.Title}) PageSource={pg}"
    
    def __str__(self) -> str:
        return self.__repr__()

class WebCrawler():
    def __init__(self):
        self.cachedbfname = Funcs.UUID()
        self.db = Tools.SQLite(self.cachedbfname)
        (
            self.db.Table("queue"). 
                AddColumn("url", "text"). 
                AddColumn("fetched", "int").
                AddColumn("md5", "string"). 
                AddIndex("fetched"). 
                AddIndex("md5")
        )
        self.tb = self.db.Table("queue")
    
    def getPageSource(self, se:Tools.Selenium.Chrome, url:str) -> list[str]:
        content = None 
        title = None 
        for _ in Range(3):
            try:
                se.Get(url)
                content = se.PageSource()
                title = se.Title()
                return title, content 
            except KeyboardInterrupt:
                # Lg.Trace("用户中断, 清理, 退出.")
                self.Close()
            except:
                pass 
        return title, content  
    
    def Run(self, url:str) -> typing.Iterable[WebCrawlerResult]:
        self.tb.Data({
            "url": url,
            "fetched": 0,
            "md5": Hash.Md5sum(url)
        }).Insert()

        with Tools.Selenium.Chrome(randomUA=False) as se:
            while self.tb.Where("fetched", "=", 0).Count() != 0:
                row = self.tb.Where("fetched", "=", 0).First()

                # Lg.Trace(row)
                nexturl = row['url']

                # Time.Sleep(5)
                # ipdb.set_trace()

                # Lg.Trace("采集URL:", nexturl)

                try:
                    u = Tools.URL(nexturl).Parse()
                except KeyboardInterrupt:
                    # Lg.Trace("用户中断, 清理, 退出.")
                    self.Close()
                except Exception as e:
                    # Lg.Trace(nexturl)
                    # Lg.Trace(traceback.print_exc())
                    continue

                schema = u.Schema
                host = u.Host
                port = u.Port
                path = Os.Path.Basedir(u.Path)

                # Lg.Trace("域名:", host)

                # Lg.Trace(host, "获取页面:", nexturl)
                title, content = self.getPageSource(se, nexturl)
                if not content:
                    # Lg.Trace(host, "页面获取失败")
                    continue 

                # Lg.Trace(host, "页面获取完成")

                yield WebCrawlerResult(
                    URL=nexturl,
                    PageSource=content,
                    Title=title,
                )

                self.tb.Where("id", "=", row['id']).Data({
                    "fetched": 1
                }).Update()

                for i in String(content).RegexFind("<a.+?href=\"(.*?)\".*?>(.+?)</a>", True):
                    # Lg.Trace("正则找到的结果:", i)
                    try:
                        curl = i[1].strip()
                        if "#" in curl:
                            curl = curl.split("#")[0]
                            # Lg.Trace("URL有#, 去掉之后:", curl)
                        
                        if curl.strip() == "":
                            continue

                        if '/../' in curl:
                            continue
                        
                        # Lg.Trace("找到链接:", curl)
                        if len(String(curl).RegexFind("(.+)://.+")) != 0:
                            # Lg.Trace("链接是完整链接")
                            if String(curl).RegexFind("(.+)://.+")[0][1] in ["http", "https"]:
                                if Tools.URL(curl).Parse().Host != host:
                                    # Lg.Trace("链接是站外链, 跳过")
                                    continue 
                                else:
                                    if self.tb.Where("md5", "=", Hash.Md5sum(curl)).Exists():
                                        # Lg.Trace("链接已爬过/在队列, 跳过")
                                        continue
                                    
                                    # Lg.Trace("放入队列:", curl)
                                    self.tb.Data({
                                        "url": curl,
                                        "fetched": 0,
                                        "md5": Hash.Md5sum(curl)
                                    }).Insert()
                            else:
                                # Lg.Trace("链接不是web的协议, 跳过")
                                pass
                        else:
                            if curl.startswith("#"):
                                # Lg.Trace("链接是tag, 跳过")
                                continue
                            
                            if curl.startswith("javascript:"):
                                # Lg.Trace("链接是javascript, 跳过")
                                continue
                            
                            if curl.startswith("mailto:"):
                                # Lg.Trace("链接是mailto, 跳过")
                                continue
                            
                            if (schema == "http" and port == "80") or (schema == "https" and port == "443"):
                                nnexturl = schema + "://" + host
                            else:
                                nnexturl = schema + "://" + host + ":" + str(port)
                            
                            if curl.startswith("/"):
                                # Lg.Trace("链接是绝对路径")
                                nnexturl += curl
                            else:
                                # Lg.Trace("链接是相对路径")
                                nnexturl += Os.Path.Join(path, curl)
 
                            if self.tb.Where("md5", "=", Hash.Md5sum(nnexturl)).Exists():
                                # Lg.Trace("链接已爬过/在队列, 跳过")
                                continue

                            # Lg.Trace("放入队列:", nnexturl)
                            self.tb.Data({
                                "url": nnexturl,
                                "fetched": 0,
                                "md5": Hash.Md5sum(nnexturl)
                            }).Insert()

                    except KeyboardInterrupt:
                        # Lg.Trace("用户中断, 清理, 退出.")
                        self.Close()
                    except Exception as e:
                        Lg.Error("解析链接\""+i[1]+"\"出错:", e)

                # Lg.Trace("解析页面完成")

    def Close(self):
        self.db.Close()
        Os.Unlink(self.cachedbfname) 

    def __enter__(self):
        return self 
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.Close()
        except:
            pass

if __name__ == "__main__":
    # Lg.SetFile("230412.web.crawler.log", color=False)
    with WebCrawler() as wc:
        for r in wc.Run('https://www.spaceblock.co.uk'):
            Lg.Info(r.URL, "=====>", r.Title)


