from __future__ import annotations

import socket
import typing

# from bagbag import Lg
# import ipdb 

class UDPPacket():
    def __init__(self, host:str, port:int, message:bytes, socket:socket.socket) -> None:
        # print(8, message)
        self.Host = host 
        self.Port = port 
        self.Message = message
        self.socket = socket
    
    def ReplyBytes(self, message:bytes | UDPPacket | None):
        if type(message) == bytes:
            self.socket.sendto(message, (self.Host, self.Port))
        elif type(message) == UDPPacket:
            self.socket.sendto(message.Message, (self.Host, self.Port))
        
        return self

    def __repr__(self):
        return f"UDPPacket(Host={self.Host} Port={self.Port} Message={self.Message})"
    
    def __str__(self):
        return self.__repr__()

class Listen():
    def __init__(self, host:str, port:int, itermode:str='bytes'):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        self.itermode = itermode

    def RecvBytes(self, bufsize:int=1024, timeout:float=5.0) -> UDPPacket | None:
        self.server_socket.settimeout(timeout)
        try:
            message, address = self.server_socket.recvfrom(bufsize)
            return UDPPacket(address[0], address[1], message, self.server_socket)
        except socket.timeout:
            return None 
    
    def __iter__(self) -> typing.Iterator[UDPPacket]:
        while True:
            if self.itermode == 'bytes':
                yield self.RecvBytes()

class Connect():
    def __init__(self, host:str, port:int) -> None:
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host 
        self.port = port
    
    def SendBytes(self, message:bytes | UDPPacket | None):
        # ipdb.set_trace()
        if type(message) == bytes:
            self.client_socket.sendto(message, (self.host, self.port))
        elif type(message) == UDPPacket:
            self.client_socket.sendto(message.Message, (self.host, self.port))
            
        return self
    
    def RecvBytes(self, bufsize:int=2048, timeout:float=5.0) -> UDPPacket | None:
        self.client_socket.settimeout(timeout)
        try:
            message, address = self.client_socket.recvfrom(bufsize)
            return UDPPacket(address[0], address[1], message, self.client_socket)
        except socket.timeout:
            return None 

if __name__ == "__main__":
    for pkg in Listen("0.0.0.0", 53):
        pkg.ReplyBytes(Connect("114.114.114.114", 53).SendBytes(pkg).RecvBytes())