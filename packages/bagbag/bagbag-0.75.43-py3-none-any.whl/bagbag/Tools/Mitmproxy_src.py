from mitmproxy.tools.main import mitmdump
from .. import Process

class Mitmproxy():
    def __init__(
            self, 
            addonFilePath:str|list[str]=None, 
            saveStreamToFile:str=None,
            listenAddress:str="0.0.0.0",
            listenPort:int=8080,
            mode:str="http", # socks5
            sslInsecure:bool=False,
        ) -> None:

        args = [
            "--quiet",
        ]

        if addonFilePath != None:
            if type(addonFilePath) == str:
                args.append("--scripts")
                args.append(addonFilePath)
            elif type(addonFilePath) == list:
                for a in addonFilePath:
                    args.append("--scripts")
                    args.append(addonFilePath)
        
        if saveStreamToFile != None:
            args.append('--save-stream-file')
            args.append(f"+{saveStreamToFile}")
        
        if mode == 'http':
            mode = 'regular'

        args.append("--listen-host")
        args.append(listenAddress)

        args.append("--listen-port")
        args.append(str(listenPort))
        
        args.append("--mode")
        args.append(mode)

        if sslInsecure == False:
            args.append('--ssl-insecure')

        try:
            self.pm = Process(mitmdump, args)
        except RuntimeError:
            raise Exception('需要在__name__ == "__main__"中执行Mitmproxy')

    def Stop(self):
        self.pm.Kill()