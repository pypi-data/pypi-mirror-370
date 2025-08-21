from __future__ import annotations

# 需要配合以下服务食用
# 
# version: '3'
# services:
#   matrix_bot:
#     image: darren2046/matrix-bot:0.0.12
#     container_name: matrix-bot
#     restart: always
#     #ports:
#     #   - "8888:8888" 
#     environment:
#       MATRIX_SERVER: "https://your.homeserver.com"
#       MATRIX_USER: account_username 
#       MATRIX_PASS: account_password
#       API_PASS: password_for_call_this_api_server # can be empty
#     dns:
#       - 8.8.8.8
#       - 4.4.4.4
#     volumes:
#       - /data/cr-volumes/matrix-bot/data:/data
# 备注:
# 版本0.0.1
#     arm64的可以调用http api发送消息, 也可以收消息(发送id给bot返回房间号)
#     amd64的可以调用http api发送消息, 但是不能收消息, 一脸蒙逼
#     

#print("load " + '/'.join(__file__.split('/')[-2:]))

from .. import Http
from .. import Base64
from .. import Json

import requests
import time

def retryOnNetworkError(func): # func是被包装的函数
    def ware(self, *args, **kwargs): # self是类的实例
        while True:
            try:
                res = func(self, *args, **kwargs)
                break
            except requests.exceptions.ReadTimeout as e:
                time.sleep(1)

        return res
    
    return ware

class MatrixBotMessage():
    def __init__(self, mb:MatrixBot, time:int, text:str, user:str, room:str) -> None:
        self.mb = mb 
        self.Time = time 
        self.Text = text 
        self.User = user 
        self.Room = room
    
    @retryOnNetworkError
    def Reply(self, message:str):
        resp = Http.PostForm(
            self.mb.apiserver + "/matrix-bot/send/text", 
            {
                "room": self.Room, 
                'text': message,
                'password': self.mb.password,
            })
        if resp.StatusCode != 200:
            raise Exception("发送消息错误:", resp.StatusCode)
    
    @retryOnNetworkError
    def ReplyImage(self, path:str):
        resp = Http.PostForm(
            self.mb.apiserver + "/matrix-bot/send/image", 
            {
                "room": self.Room, 
                'image': Base64.Encode(open(path, 'rb').read()),
                'password': self.mb.password,
            })
        if resp.StatusCode != 200:
            raise Exception("发送消息错误:", resp.StatusCode)
    
    def __repr__(self):
        return f"MatrixBotMessage(Time={self.Time} Room={self.Room} User={self.User} Text={self.Text})"
    
    def __str__(self):
        return f"MatrixBotMessage(Time={self.Time} Room={self.Room} User={self.User} Text={self.Text})"

class MatrixBot():
    def __init__(self, apiserver:str, password:str="") -> None:
        self.apiserver = apiserver.rstrip('/')
        self.password = password 
        self.room = None 

        if not self.apiserver.startswith("http://") and not self.apiserver.startswith("https://"):
            self.apiserver = "https://" + self.apiserver
    
    @retryOnNetworkError
    def SetRoom(self, room:str) -> MatrixBot:
        """
        如果room的id是 !abcdefghiljkmn:example.com, 那么room可以是abcdefghiljkmn, 默认取homeserver的域名
        
        :param room: The room you want to join
        :type room: str
        """
        self.room = room

        return self
    
    @retryOnNetworkError
    def Send(self, message:str, msgtype:str="text"):
        """
        > Send a message to the room. 
        
        The function takes two parameters: 
        
        - `message`: The message to be sent. 
        - `msgtype`: The type of the message. 
        
        The `msgtype` parameter can be one of the following: 
        
        - `text`: Plain text. 
        - `markdown`: Markdown text. 
        - `md`: Markdown text. 
        
        The function will raise an exception if the room is not set. 
        
        The function will raise an exception if the message cannot be sent.
        
        :param message: The message to be sent
        :type message: str
        :param msgtype: The type of message to be sent. Currently only supports text and markdown,
        defaults to text
        :type msgtype: str (optional)
        """
        if self.room == None:
            raise Exception("Need to set room first. ")
        
        if msgtype == "text":
            url = "/matrix-bot/send/text"
        else:
            url = "/matrix-bot/send/markdown"

        resp = Http.PostForm(
            self.apiserver + url, 
            {
                "room": self.room, 
                'text': message,
                'password': self.password,
            })
        if resp.StatusCode != 200:
            raise Exception("发送消息错误:", resp.StatusCode)
    
    @retryOnNetworkError
    def SendImage(self, path:str):
        if self.room == None:
            raise Exception("Need to set room first. ")

        resp = Http.PostForm(
            self.apiserver + "/matrix-bot/send/image", 
            {
                "room": self.room, 
                'image': Base64.Encode(open(path, 'rb').read()),
                'password': self.password,
            })
        if resp.StatusCode != 200:
            raise Exception("发送消息错误:", resp.StatusCode)
    
    @retryOnNetworkError
    def GetMessage(self, num:int=10, room:str=None) -> list[MatrixBotMessage]:
        """
        > Get the last 10 messages from the current room, will get messages from all rooms if the current room is not set. 
        > If the room is like !abcdefg:example.com and homeserver is example.com, then only need to set 'abcdefg' as room id. 
        > If the room is set to 'all', will get messages from all rooms.
        
        :param num: The number of messages to get, defaults to 10
        :type num: int (optional)
        :param room: The room to send the message to. If not specified, the default room is used
        :type room: str
        :return: A list of MatrixBotMessage objects.
        """
        if room == None:
            if self.room == None:
                room = 'all'
            else:
                room = self.room 

        res = Http.Get(self.apiserver + "/matrix-bot/get/message", {'password': self.password, 'num': str(num), "room": room}).Content
        # Lg.Trace(res)
        res = Json.Loads(res)
        resm = []
        for r in res:
            resm.append(MatrixBotMessage(self, r["time"], r["text"], r["user"], r["room"]))
        
        return resm

if __name__ == "__main__":
    mb = MatrixBot("https://example.com", 'password').SetRoom("xQIjxlkLqVdVKJaxwF")
    mb.Send("Hello World!")