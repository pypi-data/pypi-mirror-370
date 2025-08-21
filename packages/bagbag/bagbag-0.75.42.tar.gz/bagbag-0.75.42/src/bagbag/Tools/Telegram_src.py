from __future__ import annotations

from re import I
from attr import has
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import telethon
from telethon import utils
from telethon import types
import time
import typing
import ipdb
from typing import List, Iterator
from telethon.tl.types import  InputMessagesFilterGif
from telethon.tl.types import  InputMessagesFilterDocument
from telethon.tl.types import  InputMessagesFilterMusic
from telethon.tl.types import  InputMessagesFilterPhotoVideo
from telethon.tl.types import  InputMessagesFilterUrl
from telethon.tl.types import  InputMessagesFilterVoice
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.types import ChannelParticipantCreator
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.channels import GetParticipantsRequest
import tqdm

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from telethon.tl.types import DocumentAttributeVideo

from .. import Os
from .Database import SQLite
from .. import Time
from .. import Lg
from ..String import String
from ..File import File
from .Ratelimit_src import RateLimit
from .. import Funcs

#print("load " + '/'.join(__file__.split('/')[-2:]))

class TelegramGeo():
    def __init__(self):
        self.Long = None
        self.Lat = None 
        self.AccessHash = None

    def __repr__(self):
        return f"TelegramGeo(Long={self.Long}, Lat={self.Lat}, AccessHash={self.AccessHash})"
        
    def __str__(self):
        return f"TelegramGeo(Long={self.Long}, Lat={self.Lat}, AccessHash={self.AccessHash})"

class TelegramPhoto():
    def __init__(self):
        self.ID = None
        self.AccessHash = 0
        self.message = None 
    
    def Save(self, fpath:str=None) -> str:
        if fpath == None:
            fpath = "photo.jpg"
        elif Os.Path.IsDir(fpath):
            fpath = Os.Path.Join(fpath, "photo.jpg")

        fpath = Os.Path.Uniquify(fpath)

        self.message.download_media(file=fpath)

        return fpath
    
    def __repr__(self):
        return f"TelegramPhoto(ID={self.ID}, AccessHash={self.AccessHash})"
        
    def __str__(self):
        return f"TelegramPhoto(ID={self.ID}, AccessHash={self.AccessHash})"
        
# File and Audio
class TelegramFile():
    def __init__(self):
        self.message:telethon.tl.patched.Message = None 
        self.Name:str = ""
        self.Size:int = 0
        self.ID:int = None 
        self.AccessHash:int = 0
        self.MimeType:str = None 
        # mimetype = video
        self.VideoDuration:int = None 
        self.VideoWidth:int = None 
        self.VideoHeight:int = None 
    
    def callback(self, current, total):
        self.pbar.update(current-self.prev_curr)
        self.prev_curr = current
    
    def Save(self, fpath:str=None) -> str:
        if self.Name.strip() == "":
            name = Funcs.UUID() + ".mp4"
        else:
            name = self.Name + ".mp4"

        if fpath == None:
            fpath = name
        elif Os.Path.IsDir(fpath):
            fpath = Os.Path.Join(fpath, name)

        fpath = Os.Path.Uniquify(fpath)

        self.prev_curr = 0
        self.pbar = tqdm.tqdm(total=self.Size, unit='B', unit_scale=True)
        self.message.download_media(file=fpath, progress_callback=self.callback)
        self.pbar.close()

        return fpath
    
    def __repr__(self):
        return f"TelegramFile(Name={self.Name}, Size={self.Size}, ID={self.ID}, AccessHash={self.AccessHash})"
        
    def __str__(self):
        return f"TelegramFile(Name={self.Name}, Size={self.Size}, ID={self.ID}, AccessHash={self.AccessHash})"

class TelegramButton():
    def __init__(self, btn:telethon.tl.custom.messagebutton.MessageButton) -> None:
        self.btn = btn 

    def Text(self) -> str:
        return self.btn.text
    
    def Click(self):
        self.btn.click()

    def __repr__(self):
        return f"TelegramButton(Text={self.btn.text} Data={self.btn.data} Url={self.btn.url} Inline_query={self.btn.inline_query})"
        
    def __str__(self):
        return self.__repr__()

class TelegramMessage():
    def __init__(self, client:TelegramClient):
        self.client = client
        self.tg:Telegram = None 
        self.peer:TelegramPeer = None 
        self.message:telethon.tl.patched.Message = None
        self.PeerType:str = None 
        self.Chat = TelegramPeer(client=self.client)
        self.ID:int = None 
        self.Time:int = None 
        self.Action:str = None 
        self.File:TelegramFile = None
        self.Photo:TelegramPhoto = None
        self.Geo:TelegramGeo = None
        self.Message:str = None
        self.User:TelegramPeer = None
        self.Buttons:List[List[TelegramButton]] = None
        self.MessageRaw:str = None 
        self.GroupedID:int = None # 如果是同一条消息的多个图片, 会有相同的GroupedID
        self.ReplyToMessageID:int = None 
    
    def ForwardTo(self, Username:str|TelegramPeer, HideSenderName:bool=True):
        if type(Username) == str:
            if HideSenderName:
                p = self.tg.PeerByUsername(Username)
                p.SendMessage(self.message)
            else:
                self.message.forward_to(Username)
        else:
            if HideSenderName:
                Username.SendMessage(self.message)
            else:
                self.message.forward_to(Username)

    def Refresh(self) -> TelegramMessage:
        return self.peer.Message(self.ID) 

    def ClickButton(self, buttonText:str) -> bool:
        """
        If the button exists, click it and return True, otherwise return False
        
        :param buttonText: The text of the button you want to click
        :type buttonText: str
        :return: A boolean value.
        """
        if self.Buttons != None:
            for row in self.Buttons:
                for btn in row:
                    if btn.Text() == buttonText:
                        btn.Click()
                        return True 

        return False 
    
    def Delete(self):
        self.message.delete()

    def ReplyMessage(self, message:str):
        return self.peer.client.send_message(self.peer.entity, message, reply_to=self.ID)
    
    def callback(self, current, total):
        self.pbar.update(current-self.prev_curr)
        self.prev_curr = current

    def ReplyVideo(self, path:str):
        metadata = extractMetadata(createParser(path))

        self.prev_curr = 0
        self.pbar = tqdm.tqdm(total=File(path).Size(), unit='B', unit_scale=True)
        
        resp = self.peer.client.send_file(self.peer.entity, file=open(path, 'rb'), attributes=[
                                  DocumentAttributeVideo(
                                      (0, metadata.get('duration').seconds)[metadata.has('duration')],
                                      (0, metadata.get('width'))[metadata.has('width')],
                                      (0, metadata.get('height'))[metadata.has('height')]
                                  )], progress_callback=self.callback, reply_to=self.ID)
        
        self.pbar.close()

        return resp
    
    def ReplyImage(self, path:str|list):
        return self.peer.client.send_file(self.peer.entity, path, reply_to=self.ID)
    
    def __repr__(self):
        return f"TelegramMessage(PeerType={self.PeerType}, Chat={self.Chat}, ID={self.ID}, Time={self.Time}, Action={self.Action}, File={self.File}, Photo={self.Photo}, Message={self.MessageRaw}, User={self.User}, Button={self.Buttons})"
        
    def __str__(self):
        return f"TelegramMessage(PeerType={self.PeerType}, Chat={self.Chat}, ID={self.ID}, Time={self.Time}, Action={self.Action}, File={self.File}, Photo={self.Photo}, Message={self.MessageRaw}, User={self.User}, Button={self.Buttons})"
        
class TelegramPeer():
    def __init__(self, Type:str=None, Name:str=None, Username:str=None, ID:int=None, AccessHash:int=None, PhoneNumber:int=None, LangCode:str=None, client:TelegramClient=None):
        """
        :param Type: The type of the entity. Can be either "user" or "channel" (group)
        :type Type: str
        :param Name: The name of the user or channel
        :type Name: str
        :param Username: The username of the user or channel
        :type Username: str
        :param ID: The ID of the user or chat
        :type ID: int
        :param AccessHash: This is a unique identifier for a user or group. It is used to identify a user
        or group in a secure way
        :type AccessHash: int
        :param PhoneNumber: The phone number of the user
        :type PhoneNumber: int
        :param LangCode: The language code of the user
        :type LangCode: str
        """
        self.Type = Type # channel, group, user
        self.Name = Name # 名字, First Name + Last Name 或者 Title 
        self.Username = Username 
        self.ID = ID
        self.AccessHash = AccessHash
        self.PhoneNumber = PhoneNumber 
        self.LangCode = LangCode 
        self.Resolved = False # 是否已解析. 只设置一个ID, 解析之后就补上其它的字段.
        self.client = client # telethon.sync.TelegramClient
        self.entity = None 
        self.tg:Telegram = None
        # 如果是从Group里面Get的Admin, 如果是owner, 会被设置后面这个值
        self.GroupOwner:bool = None 
        self.GroupAdmin:bool = None 

        self.admins:list[TelegramPeer] = None
        self.getmemberratelimit = RateLimit('60/m')

    def __getAdmin(self):
        self.admins = []
        try:
            # Lg.Trace()
            for user in self.tg.client.iter_participants(self.entity, filter=ChannelParticipantsAdmins):
                # Lg.Trace()
                # ipdb.set_trace()
                tp = self.tg.wrapPeer(user)

                tp.GroupAdmin = True

                # 检查管理员是否为 owner
                if isinstance(user.participant, ChannelParticipantCreator):
                    # Lg.Trace()
                    tp.GroupOwner = True
                else:
                    tp.GroupOwner = False
                # Lg.Trace()
                self.admins.append(tp)
        except telethon.errors.rpcerrorlist.ChatAdminRequiredError:
            Lg.Warn("can not get administrators")
            pass 
    
    def GetAdmin(self) -> list[TelegramPeer]:
        if self.Type != "group":
            return []
        
        if self.admins == None:
            self.__getAdmin()

        return self.admins
    
    def _members_first_20(self) -> typing.Iterable[TelegramPeer]:
        # Lg.Trace()
        for user in self.tg.client.iter_participants(self.entity):
            # Lg.Trace()
            # ipdb.set_trace()
            tp = self.tg.wrapPeer(user)

            yield tp
    
    def _members_by_search(self) -> typing.Iterable[TelegramPeer]:
        queryKey = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

        for key in queryKey:
            # Lg.Trace("Key:", key)
            offset = 0
            limit = 100
            while True:
                self.getmemberratelimit.Take()
                # Lg.Trace(f"offset {offset}, limit {limit}")
                participants = self.client(GetParticipantsRequest(
                    self.entity, ChannelParticipantsSearch(key), offset, limit,
                    hash=0
                ))
                if not participants.users:
                    break
                for user in participants.users:
                    tp = self.tg.wrapPeer(user)
                    yield tp

                offset += len(participants.users)

    def _members_by_history(self, limit:int=5000) -> typing.Iterable[TelegramPeer]:
        count = 0
        for message in self.MessagesAll():
            yield message.User

            count += 1
            if count >= limit:
                break
    
    def Members(self) -> typing.Iterable[TelegramPeer]:
        peerid = {}

        if self.admins == None:
            self.__getAdmin()

        for u in self.admins:
            if u.ID in peerid:
                continue 
                
            peerid[u.ID] = None 
            yield u 

        for u in self._members_first_20():
            if u.ID in peerid:
                continue 

            peerid[u.ID] = None 

            # Lg.Trace("_members_first_20:", len(peerid))
            yield u 
        
        for u in self._members_by_search():
            if u.ID in peerid:
                continue 

            peerid[u.ID] = None 

            # Lg.Trace("_members_by_search:", len(peerid))
            yield u 

        for u in self._members_by_history():
            if u == None:
                continue 
            
            if u.ID in peerid:
                continue 

            peerid[u.ID] = None 

            # Lg.Trace("_members_by_history:", len(peerid))
            yield u 
        
    def GetOwner(self) -> TelegramPeer | None:
        if self.Type != "group":
            return None 
        
        if self.admins == None:
            self.__getAdmin()
        
        for tp in self.admins:
            if tp.GroupOwner:
                return tp
        
    def Message(self, id:str) -> TelegramMessage:
        message = self.client.get_messages(self.entity, ids=id)
        return self.__wrapMsg(message)
    
    def __wrapMsg(self, message:telethon.tl.patched.Message) -> TelegramMessage:
        # import ipdb
        # ipdb.set_trace()
        msg = TelegramMessage(self.client)
        msg.peer = self
        msg.message:telethon.tl.patched.Message = message
        msg.tg = self.tg
        msg.PeerType = self.Type 
        msg.Chat = self 
        msg.ID = message.id 
        msg.Time = int(message.date.timestamp())
        msg.GroupedID = message.grouped_id
        msg.ReplyToMessageID = message.reply_to_msg_id
        if message.action:
            msg.Action = message.action.to_dict()["_"]
        if message.media:
            if message.document:
                msg.File = TelegramFile()
                msg.File.message = message
                msg.File.ID = message.document.id 
                msg.File.AccessHash = message.document.access_hash
                msg.File.Size = message.document.size 
                msg.File.MimeType = message.document.mime_type
                # Media为MessageMediaWebPage的时候没有document
                # 其实就是message的预览, 不用录细节
                if hasattr(message.media, "document"):
                    for attr in message.media.document.attributes:
                        if attr.to_dict()['_'] == "DocumentAttributeFilename":
                            msg.File.Name = attr.to_dict()['file_name']
                        if attr.to_dict()['_'] == "DocumentAttributeVideo":
                            msg.File.VideoDuration = attr.to_dict()['duration']
                            msg.File.VideoWidth = attr.to_dict()['w']
                            msg.File.VideoHeight = attr.to_dict()['h']
            elif message.photo:
                msg.Photo = TelegramPhoto()
                msg.Photo.message = message
                msg.Photo.ID = message.photo.id
                msg.Photo.AccessHash = message.photo.access_hash
            elif message.geo:
                msg.Geo = TelegramGeo()
                msg.Geo.AccessHash = message.geo.access_hash
                msg.Geo.Lat = message.geo.lat
                msg.Geo.Long = message.geo.long
            # else: 
            #     import ipdb 
            #     ipdb.set_trace()
            #     print(message)
        if message.message:
            msg.Message = message.message
        if message.text:
            msg.MessageRaw = message.text
        if message.reply_to_msg_id != None:
            msg.ReplyToMessageID = message.reply_to_msg_id
        if message.from_id:
            # ipdb.set_trace()
            # print(message.from_id.to_dict())
            if message.from_id.to_dict()['_'] == "PeerUser":
                t = "bot" if message.sender.bot else "user"
                msg.User = TelegramPeer(Type=t, ID=message.from_id.user_id, client=self.client)
                msg.User.AccessHash = message.sender.access_hash
                msg.User.Name = ' '.join([i for i in filter(lambda x: x != None, [message.sender.first_name, message.sender.last_name])])
                msg.User.Username = message.sender.username
                msg.User.PhoneNumber = message.sender.phone
                msg.User.LangCode = message.sender.lang_code
                msg.User.Resolved = True
            elif message.from_id.to_dict()['_'] == "PeerChannel":
                msg.User = TelegramPeer(Type="channel", ID=message.from_id.channel_id, client=self.client)
                if hasattr(message.sender, 'title'):
                    msg.User.Name = message.sender.title
                if hasattr(message.sender, 'access_hash'):
                    msg.User.AccessHash = message.sender.access_hash
                if hasattr(message.sender, 'username'):
                    msg.User.Username = message.sender.username
                msg.User.Resolved = True
        
        '''
        if entity.bot == True:
            tp.Type = "bot"
        else:
            tp.Type = "user"

        if entity.broadcast == True:
            tp.Type = "channel"
        elif entity.megagroup == True:
            tp.Type = "group"
        '''
        # ipdb.set_trace()

        if message.buttons != None:
            buttons = []
            for row in message.buttons:
                btns = []
                for btn in row:
                    btns.append(TelegramButton(btn))
                buttons.append(btns)
            
            msg.Buttons = buttons

        return msg
    
    def Messages(self, limit:int=100, offset:int=0, filter:str=None) -> list[TelegramMessage]:
        """
        只指定limit的时候就从会话的底部往上翻. 消息从新到旧返回, 新的msg id更大.
        如果有指定offset就是从id为这个offset往上翻. 不包含这offset的id的消息.
        所以如果要遍历所有消息, 就先不指定offset, 提取100条. 然后把offset设置为这一批的消息的最后一条消息的offset再抓取, 循环往复.
        
        :param limit: The maximum number of messages to be returned, defaults to 100
        :type limit: int (optional)
        :param offset: The offset of the first message to be returned, defaults to 0
        :type offset: int (optional)
        :param filter: 需要过滤出来的消息类型, 可选 gif, file, music, media, link, voice, 参考telegram的客户端关于群组或者频道的详情
        :return: A list of TelegramMessage objects
        """
        filterm = {
            "gif": InputMessagesFilterGif,
            "file": InputMessagesFilterDocument,
            "music": InputMessagesFilterMusic,
            "media": InputMessagesFilterPhotoVideo,
            "link": InputMessagesFilterUrl,
            "voice": InputMessagesFilterVoice,
            None: None, 
        }
        res = []
        getmessage = self.client.get_messages(self.entity, limit=limit, offset_id=offset, filter=filterm[filter])
        for message in getmessage:
            msg = self.__wrapMsg(message)
            res.append(msg)
        return res
    
    def Resolve(self) -> TelegramPeer:
        """
        Resolve Peer, get information by peer id. 
        """
        if self.ID:
            self.entity = self.client.get_entity(self.ID)
            # import ipdb
            # ipdb.set_trace()
            if type(self.entity) == telethon.tl.types.Channel:
                if self.entity.broadcast == True:
                    self.Type = "channel"
                elif self.entity.megagroup == True:
                    self.Type = "group"
                self.Name = self.entity.title
            elif type(self.entity) == telethon.tl.types.User:
                if self.entity.bot == True:
                    self.Type = "bot"
                else:
                    self.Type = "user"
                self.Name = " ".join([i for i in filter(lambda x: x != None, [self.entity.first_name, self.entity.last_name])])
                self.PhoneNumber = self.entity.phone
                self.LangCode = self.entity.lang_code

            self.AccessHash = self.entity.access_hash
            self.Username = self.entity.username 
            self.ID = self.entity.id
        
        return self

    def __repr__(self):
        if self.Type == "user":
            return f"TelegramPeer(Type={self.Type}, Name={self.Name}, Username={self.Username}, ID={self.ID}, AccessHash={self.AccessHash}, PhoneNumber={self.PhoneNumber}, GroupOwner={self.GroupOwner})"
        else:
            return f"TelegramPeer(Type={self.Type}, Name={self.Name}, Username={self.Username}, ID={self.ID}, AccessHash={self.AccessHash})"

    def __str__(self):
        return self.__repr__()
    
    def SendMessage(self, message:str, replyToMessageID:int=None):
        if not self.entity:
            self.Resolve()

        return self.client.send_message(self.entity, message, reply_to=replyToMessageID)
    
    def callback(self, current, total):
        self.pbar.update(current-self.prev_curr)
        self.prev_curr = current

    def SendVideo(self, path:str, replyToMessageID:int=None):
        if not self.entity:
            self.Resolve()
        
        metadata = extractMetadata(createParser(path))

        self.prev_curr = 0
        self.pbar = tqdm.tqdm(total=File(path).Size(), unit='B', unit_scale=True)
        
        resp = self.client.send_file(self.entity, reply_to=replyToMessageID, file=open(path, 'rb'), attributes=[
                                  DocumentAttributeVideo(
                                      (0, metadata.get('duration').seconds)[metadata.has('duration')],
                                      (0, metadata.get('width'))[metadata.has('width')],
                                      (0, metadata.get('height'))[metadata.has('height')]
                                  )], progress_callback=self.callback)
        
        self.pbar.close()

        return resp
    
    def SendImage(self, path:str|list, replyToMessageID:int=None):
        if not self.entity:
            self.Resolve()
        
        return self.client.send_file(self.entity, path, reply_to=replyToMessageID)
        
    def MessagesAll(self, filter:str=None) -> Iterator[TelegramMessage]:
        """
        :param filter: 需要过滤出来的消息类型, 可选 gif, file, music, media, link, voice, 参考telegram的客户端关于群组或者频道的详情
        :return: A list of TelegramMessage objects
        """

        rl = RateLimit("60/m")
        msgs = self.Messages(filter=filter)
        while len(msgs) != 0:
            for msg in msgs:
                yield msg 

            rl.Take()
            msgs = self.Messages(offset=msgs[-1].ID, filter=filter)

        return 

# It's a wrapper for the `telethon` library that allows you to use it in a more Pythonic way
class Telegram():
    def __init__(self, appid:str, apphash:str, sessionfile:str, phone:str=None):
        self.client = TelegramClient(sessionfile, appid, apphash, device_model="Samsung S22 Ultra", system_version="Android 10.0.0", app_version="4.0.2") 
        # self.client = TelegramClient(StringSession(sessionString), appid, apphash)
        if phone:
            self.client.start(phone=phone)
        else:
            self.client.start()

        # me = self.client.get_me()
        # print(me.stringify())
        self.sessionfile = sessionfile + ".session"
        self.peersResolved = {}

    def SessionString(self) -> str:
        """
        It takes the session object from the client object and saves it to a string
        :return: The session string is being returned.
        """
        return self.client.session.save()
    
    def retryOnFloodWaitError(func): # func是被包装的函数
        def ware(self, *args, **kwargs): # self是类的实例
            while True:
                try:
                    res = func(self, *args, **kwargs)
                    return res
                except telethon.errors.rpcerrorlist.FloodWaitError as e:
                    sleepsec = int(String(e.args[0]).RegexFind("A wait of (.+?) seconds is required")[0][1]) + 1
                    Lg.Warn(f"捕获FloodWaitError错误, 休眠{sleepsec}秒")
                    Time.Sleep(sleepsec)

        return ware
    
    def wrapPeer(self, entity) -> TelegramPeer:
        # Lg.Trace()
        tp = TelegramPeer()
        tp.client = self.client
        if type(entity) == telethon.tl.types.Channel:
            if entity.broadcast == True:
                tp.Type = "channel"
            elif entity.megagroup == True:
                tp.Type = "group"
            tp.Name = entity.title
        elif type(entity) == telethon.tl.types.User:
            if entity.bot == True:
                tp.Type = "bot"
            else:
                tp.Type = "user"
            tp.Name = " ".join(filter(lambda x: x != None, [entity.first_name, entity.last_name]))
        elif type(entity) == telethon.tl.types.Chat:
            tp.Type = "chat"
            tp.Name = entity.title

        if hasattr(entity, "access_hash"):
            tp.AccessHash = entity.access_hash
        if hasattr(entity, "username"):
            tp.Username = entity.username 
        tp.ID = entity.id
        tp.entity = entity
        tp.tg = self

        return tp
    
    @retryOnFloodWaitError
    def PeerByUsername(self, username:str) -> TelegramPeer | None:
        """
        根据Username解析一个Peer, 有速率限制
        
        :param username: The username of the user/channel you want to send the message to
        :type username: str
        """
        # Lg.Trace("开始解析username:", username )
        if username in self.peersResolved:
            # Lg.Trace("存在缓存, 直接返回")
            return self.peersResolved[username]
        else:
            try:
                # Lg.Trace("第一次解析尝试")
                obj = self.client.get_entity(username)
            except (ValueError, TypeError) as e:
                # Lg.Trace("报错了:", e)
                if str(e).startswith("No user has") and str(e).endswith("as username"):
                    return None 
                if str(e).startswith("Could not find the input entity for "):
                    return None 

                time.sleep(1)
                try:
                    # Lg.Trace("第二次解析尝试")
                    obj = self.client.get_entity(username)
                except ValueError as e:
                    # Lg.Trace("报错了:", e)
                    if str(e).startswith("No user has") and str(e).endswith("as username"):
                        return None 
                    if str(e).startswith("Could not find the input entity for "):
                        return None 
                    if str(e).startswith("Cannot find any entity corresponding to"):
                        return None 

            except telethon.errors.rpcerrorlist.UsernameInvalidError as e:
                Lg.Trace("报错了, 用户名不存在:", e)
                return None 
            except telethon.errors.rpcerrorlist.UsernameNotOccupiedError as e:
                Lg.Trace("报错了, 用户名不存在:", e)
                return None 
            except telethon.errors.rpcerrorlist.ChannelInvalidError as e:
                Lg.Trace("报错了, 用户名不存在:", e)    
                return None 
            except telethon.errors.rpcerrorlist.ChannelPrivateError as e:
                Lg.Trace("报错了, 用户名不存在:", e)
                return None 

            tp = self.wrapPeer(obj)

            self.client.session.save()

            self.peersResolved[username] = tp

            return tp
    
    def PeerByIDAndHash(self, ID:int, AccessHash:int, Type:str="channel") -> TelegramPeer | None:
        """
        根据ID和Hash返回一个Peer, 没有速率限制. 
        不同的帐号解析同一个Username会得到不一样的AccessHash, 所以:
        之前帐号解析出来的Hash需要之前的帐号使用, 否则就会报错: Could not find the input entity for
        
        :param ID: The ID of the user or group
        :type ID: int
        :param Hash: The hash value of the peer, which can be obtained by calling the GetPeerHash method
        of the TelegramPeer object
        :type Hash: int
        :param Type: The type of the peer, which can be "channel", "group", or "user", defaults to
        channel
        :type Type: str (optional)
        :return: TelegramPeer
        """
        if Type in ["channel", "group"]:
            tp = types.PeerChannel(ID)
        elif Type in ["user", 'bot']:
            tp = types.PeerUser(ID)
        else:
            raise Exception(f"未知的类型:{Type}")

        peerid = utils.get_peer_id(tp)

        # Lg.Trace("第一次在PeerByIDAndHash里面解析")
        # ipdb.set_trace()

        peer = self.PeerByUsername(peerid) 

        if peer == None:
            Lg.Trace("PeerByIDAndHash里面解析第一次结果为None")
            self.client.session.save() # save all data to sqlite database session file to avoide database lock
            db = SQLite(self.sessionfile)
            try:
                (db.Table("entities").
                    Data({
                        "id": peerid, 
                        "hash": AccessHash,
                    }).Insert())
            except:
                db.Close() 
                return None  

            db.Close()

            peer = self.PeerByUsername(peerid) 
            if peer == None:
                time.sleep(1)
                peer = self.PeerByUsername(peerid) 

            return peer
        # else:
        return peer
    
    def GetMe(self) -> TelegramPeer:
        me = self.client.get_me()
        return self.PeerByIDAndHash(ID=me.id, AccessHash=me.access_hash, Type="user").Resolve()
    
    def Dialogs(self) -> list[TelegramPeer]:
        res = []
        for d in self.client.get_dialogs():
            res.append(self.wrapPeer(d.entity))
        
        return res

if __name__ == "__main__":
    import json 
    ident = json.loads(open("Telegram.ident").read())
    app_id = ident["appid"]
    app_hash = ident["apphash"]
    
    tg = Telegram(app_id, app_hash, "telegram-session", "123")

    print(tg.GetMe())

    peer = tg.PeerByUsername(ident["username"])
    # peer = tg.PeerByIDAndHash(1234567678, -345)
    print(peer)

    # import ipdb
    # ipdb.set_trace()

    for i in peer.Messages():
        if i.User:
            i.User.Resolve()
        print(i)



