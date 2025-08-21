from __future__ import annotations

import socket

from ...Tools import Chan
from ...Thread import Thread
from ... import Lg

import io
import typing 
import msgpack
# import pickle
import ssl

import socks 

# print("tcp load")

class StreamClosedError(Exception):
    pass

class TCPPeerAddress():
    def __init__(self, host:str, port:int):
        self.Host = host 
        self.Port = port 
    
    def __str__(self) -> str:
        return f"TCPPeerAddress(Host={self.Host}, Port={self.Port})"
    
    def __repr__(self) -> str:
        return self.__str__()

class PacketConnection():
    def __init__(self, sc:StreamConnection) -> None:
        self.sc = sc 

    def PeerAddress(self) -> TCPPeerAddress:
        return TCPPeerAddress(self.sc.Host, self.sc.Port)

    def Close(self):
        self.sc.Close()

    def Send(self, data:dict|list|str|int|bytes):
        # datab = pickle.dumps(data, protocol=2)
        datab = msgpack.packb(data, use_bin_type=True)
        length = len(datab)
        lengthb = length.to_bytes(8, "big")
        self.sc.SendBytes(lengthb + datab)

    def Recv(self) -> dict|list|str|int|bytes:
        length = int.from_bytes(self.sc.RecvBytes(8), "big")
        datab = self.sc.RecvBytes(length)
        # print(len(datab))
        # return pickle.loads(datab)
        return msgpack.unpackb(datab, raw=False)
    
    def __str__(self):
        return f"PacketConnection(Host={self.sc.Host} Port={self.sc.Port})"
    
    def __repr__(self):
        return f"PacketConnection(Host={self.sc.Host} Port={self.sc.Port})"
    
    def __iter__(self) -> typing.Iterator[dict|list|str|int|bytes]:
        while True:
            try:
                yield self.Recv()
            except:
                return 
        
class StreamConnection():
    def __init__(self, ss:socket, host:str, port:int):
        self.ss = ss
        self.Host = host
        self.Port = port 
        self.buffer = io.BytesIO()
    
    def PacketConnection(self) -> PacketConnection:
        return PacketConnection(self)
    
    def PeerAddress(self) -> TCPPeerAddress:
        return TCPPeerAddress(self.Host, self.Port)
    
    def Send(self, data:str):
        self.SendBytes(data.encode('utf-8'))

    def SendBytes(self, data:bytes):
        try:
            self.ss.sendall(data) 
        except BrokenPipeError:
            raise StreamClosedError("发送数据出错")
        
    def SendLine(self, data:str):
        self.SendBytes((data + "\n").encode('utf-8') )

    def Recv(self, length:int) -> str:
        return self.RecvBytes(length).decode('utf-8')

    def RecvBytes(self, length:int=None) -> bytes:
        if length != None:
            buff = b''
            while len(buff) < length:
                # print("92")
                buf = self.ss.recv(length)
                # Lg.Trace(buf)
                # print(len(buf))
                if buf:
                    buff += buf
                else:
                    if buff == "":
                        raise StreamClosedError("接收数据出错")
                    else:
                        break
            return buff
        else:
            buf = self.ss.recv(8192)
            if buf:
                return buf 
            else:
                if buf == "":
                    raise StreamClosedError("接收数据出错")
                else:
                    return buf
                
    def RecvLine(self, encoding:str='utf-8') -> str:
        """
        从TCP连接中按行读取数据，返回一行数据，包括最后的换行符。

        :param encoding: 字符编码，如果为None则返回bytes，否则返回解码后的字符串
        :return: 读取到的一行数据，包括换行符
        """
        while True:
            # 尝试从缓冲区中读取一行数据
            self.buffer.seek(0)
            data = self.buffer.read()
            if b'\n' in data:
                line, remaining = data.split(b'\n', 1)
                self.buffer = io.BytesIO(remaining)
                if encoding is not None:
                    return line.decode(encoding) + '\n'
                else:
                    return line + b'\n'
            
            # 如果缓冲区中没有换行符，从连接中读取更多数据
            new_data = self.ss.recv(4096)
            if not new_data:
                # 如果连接关闭，返回缓冲区中的所有数据
                if data:
                    if encoding is not None:
                        return data.decode(encoding)
                    else:
                        return data
                else:
                    return b"" if encoding is None else ""
            
            # 将新数据追加到缓冲区
            self.buffer.write(new_data)

    def Close(self):
        self.ss.close()
    
    def __str__(self):
        return f"StreamConnection(Host={self.Host} Port={self.Port})"
    
    def __repr__(self):
        return f"StreamConnection(Host={self.Host} Port={self.Port})"

class Listen():
    def __init__(self, host:str, port:int, waitQueue:int=5):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.s.listen(waitQueue)

        self.q:Chan[StreamConnection] = Chan(10)

        Thread(self.acceptloop)
    
    def acceptloop(self):
        while True:
            ss, addr = self.s.accept()
            self.q.Put(StreamConnection(ss, addr[0], addr[1]))

    def Accept(self) -> StreamConnection:
        return self.q.Get()
    
    def Close(self):
        self.s.close()
    
    def __iter__(self) -> typing.Iterator[StreamConnection]:
        while True:
            yield self.Accept()

def Connect(host:str, port:int, timeout:int=15, SSL:bool=False, SNI:str=None, sslcertfile=None, sslkeyfile=None, proxy:dict={"type": None, "addr": None, "port": None, "username": None, "password": None}):
    """
    The Connect function establishes a connection to a host and port, optionally using a proxy.
    proxy例如: {"type": "socks5", "addr": "127.0.0.1", "port": 25783}. type可选socks5, socks4, http
    
    :param host: The "host" parameter is a string that represents the hostname or IP address of the
    server you want to connect to
    :type host: str
    :param port: The `port` parameter is an integer that represents the port number on the host to
    connect to. It is used to establish a connection with the specified port on the host
    :type port: int
    :param proxy: The `proxy` parameter is a dictionary that contains information about the proxy server
    to connect through. It has the following keys:
    :type proxy: dict
    :return: a StreamConnection object.
    """
    # Lg.Trace(proxy)
    # Lg.Trace([i for i in filter(lambda x: proxy[x] == None, proxy)])
    if len([i for i in filter(lambda x: proxy[x] == None, proxy)]) == 0:
        # Lg.Trace("设置proxy")
        s = socks.socksocket()

        if proxy['type'] == 'socks5':
            proxy['type'] = socks.SOCKS5
        elif proxy['type'] == 'socks4':
            proxy['type'] = socks.SOCKS4
        elif proxy['type'] == 'http':
            proxy['type'] = socks.HTTP
        
        proxy['proxy_type'] = proxy['type']
        del(proxy['type'])

        s.set_proxy(**proxy)
    else:
        # Lg.Trace("直连")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

    if timeout != None:
        s.settimeout(timeout)

    if SSL != None:
         # 将普通的TCP连接包装成SSL连接
        context = ssl.create_default_context()
        if sslcertfile and sslkeyfile:
            context.load_cert_chain(certfile=sslcertfile, keyfile=sslkeyfile)

        if SNI != None:
            s = context.wrap_socket(s, server_hostname=SNI)
        else:
            s = context.wrap_socket(s, server_hostname=host)

    s.connect((host, port))  
    return StreamConnection(s, host, port)

if __name__ == "__main__":
    import time 

    def test1():
        def server():
            print("listen on: ", "127.0.0.1", 22222)
            l = Listen("127.0.0.1", 22222)
            for s in l:
                print("Connect from:",s.PeerAddress())
                print("Receive:",s.Recv(512))
                print("Close on server side")
                s.Close()
            
        Thread(server)

        time.sleep(2)

        def client():
            print("connect to", "127.0.0.1", 22222)
            s = Connect("127.0.0.1", 22222)
            s.Send(str(int(time.time())))
            time.sleep(1)
            print("Close on client side")
            s.Close()

        for _ in range(10):
            client()
            time.sleep(1)
    # test1()

    l = Listen("127.0.0.1", 22222)
    s = l.Accept()

    while True:
        # print(type(s.RecvBytes(1024)))
        time.sleep(1)
        s.Send(str(time.time()))