from __future__ import annotations

import telebot # https://github.com/eternnoir/pyTelegramBotAPI

try:
    from .Ratelimit_src import RateLimit
    from .Lock_src import Lock 
    from .DistributedLock_src import DistributedLock
    from .. import Lg
except:
    from Ratelimit_src import RateLimit
    from Lock_src import Lock
    from DistributedLock_src import DistributedLock
    import sys
    sys.path.append("..")
    import Lg

import time

#print("load " + '/'.join(__file__.split('/')[-2:]))

class TelegramBotOfficial():
    def __init__(self, token:str, ratelimit:str="20/m", lock:Lock|DistributedLock=None):
        """
        :param token: The token of your bot
        :type token: str
        :param ratelimit: The ratelimit for the bot. This is a string in the format of "x/y" where x is
        the number of messages and y is the time period. For example, "20/m" means 20 messages per
        minute, defaults to 20/m. There is no limit if set to None.
        :type ratelimit: str (optional)
        """
        self.token = token 
        self.tb = telebot.TeleBot(self.token)
        self.tags:list[str] = []
        if ratelimit != None:
            self.rl = RateLimit(ratelimit)
        else:
            self.rl = None 
        self.lock = lock
    
    def retryOnError(func): # func是被包装的函数
        def ware(self, *args, **kwargs): # self是类的实例
            errc = 0
            while True:
                try:
                    res = func(self, *args, **kwargs)
                    break
                except Exception as e:
                    Lg.Trace(str(e))
                    time.sleep(3)
                    errc += 1
                    if errc > 10:
                        raise e

            return res
    
        return ware

    def getLock(func): # func是被包装的函数
        def ware(self, *args, **kwargs): # self是类的实例
            if self.lock != None:
                self.lock.Acquire()

            res = func(self, *args, **kwargs)

            if self.lock != None:
                self.lock.Release()
            
            return res

        return ware
    
    def rateLimit(func): # func是被包装的函数
        def ware(self, *args, **kwargs): # self是类的实例
            if self.rl != None:
                self.rl.Take()

            res = func(self, *args, **kwargs)
            
            return res

        return ware

    @retryOnError
    def GetMe(self) -> telebot.types.User:
        return self.tb.get_me()
    
    def SetChatID(self, chatid:int) -> TelegramBot:
        self.chatid = chatid
        return self
    
    @retryOnError
    @getLock
    @rateLimit
    def SendFile(self, path:str):
        self.tb.send_document(self.chatid, open(path, 'rb')) 

    @retryOnError
    @getLock
    @rateLimit
    def SendImage(self, path:str):
        self.tb.send_photo(self.chatid, open(path, 'rb'))

    @retryOnError
    @getLock
    @rateLimit
    def SendVideo(self, path:str):
        self.tb.send_video(self.chatid, open(path, 'rb')) 

    @retryOnError
    @getLock
    @rateLimit
    def SendAudio(self, path:str):
        self.tb.send_audio(self.chatid, open(path, 'rb')) 

    @retryOnError
    @getLock
    @rateLimit
    def SendLocation(self, latitude:float, longitude:float):
        self.tb.send_location(self.chatid, latitude, longitude)
    
    @retryOnError
    @getLock
    @rateLimit
    def SetTags(self, *tags:str) -> TelegramBotOfficial:
        self.tags = tags
        return self 

    @retryOnError
    @getLock
    @rateLimit
    def SendMsg(self, msg:str, mode:str="text", webPreview:bool=True, *tags:str):
        """
        It sends a message to the chatid of the bot. 

        :param msg: The message to be sent
        :type msg: str
        :param mode: text, markdown, html, defaults to text
        :type mode: str (optional)
        :param webPreview: if True, the link will be shown as a link, if False, the link will be shown
        as a text, defaults to True
        :type webPreview: bool (optional)
        :param : `msg` - the message to be sent
        :type : str
        """
        if len(tags) != 0:
            tag = '\n\n' + ' '.join(['#' + t for t in tags])
        else:
            if len(self.tags) != 0:
                tag = '\n\n' + ' '.join(['#' + t for t in self.tags])
            else:
                tag = ""
        
        if mode == "text":
            mode = None 
        
        dwp = not webPreview
        
        if len(msg) <= 4096 - len(tag):
            self.tb.send_message(self.chatid, msg.strip() + tag, parse_mode=mode, disable_web_page_preview=dwp) 
        else:
            for m in telebot.util.smart_split(msg, 4096 - len(tag)):
                self.tb.send_message(self.chatid, m.strip() + tag, parse_mode=mode, disable_web_page_preview=dwp) 
                if self.rl != None:
                    self.rl.Take()
                    
if __name__ == "__main__":
    token, chatid = open("TelegramBot.ident").read().strip().split("\n")
    t = TelegramBotOfficial(token).SetChatID(int(chatid))
    # t.SendMsg(open("Telegram.py").read(), "tag1", "tag2")
    t.SendMsg("test")
    # t.SendFile("URL.py")