# 配合以下docker-compose使用
# 
# version: '3'
# services:
#   ocr-server:
#     image: darren2046/ocr-server
#     networks:
#       ocr-server-vpc:
#         ipv4_address: 192.168.168.63
#     container_name: ocr-server-192.168.168.63
#     restart: always
#     ports:
#       - 8990:8990
# 

#print("load " + '/'.join(__file__.split('/')[-2:]))

from .. import Http
from .. import Base64
from .. import Json

class ocrResultText():
    def __init__(self, Coordinate:list, Text:str, Confidence:float) -> None:
        self.Coordinate:list = Coordinate 
        self.Text:str = Text 
        self.Confidence:float = Confidence 

class ocrResult():
    def __init__(self) -> None:
        self.Data:bytes = b'' 
        self.Texts:list[ocrResultText] = [] 
    
    def SaveImage(self, fpath:str):
        """
        保存JPEG内容到文件路径, 覆盖已有文件.
        
        :param fpath: fpath is a string parameter that represents the file path where the image will be
        saved. It is used as an argument for the open() function to create a file object in binary write
        mode ('wb'). The image data is then written to this file object using the write() method, and
        the file
        :type fpath: str
        """
        fd = open(fpath, 'wb')
        fd.write(self.Data)
        fd.close()

class OCR():
    def __init__(self, server:str) -> None:
        self.server = server

        if not self.server.startswith('http://') and not self.server.startswith("https://"):
            self.server = 'https://' + self.server

    def Recognition(self, fpath:str, lang:str="ch") -> ocrResult:
        data = open(fpath, 'rb').read()

        resp = Http.PostJson(self.server + "/ocr", {
            "lang": lang, 
            "data": Base64.Encode(data),
        })

        r = Json.Loads(resp.Content)

        if r['code'] != 200:
            raise Exception("识别OCR出错:" + r['message'])
        
        ocrr = ocrResult()
        ocrr.Data = Base64.Decode(r['data'])
        for rr in r['result']:
            ocrr.Texts.append(ocrResultText(rr['coordinate'], rr['text'], rr['confidence']))

        return ocrr 
    
if __name__ == "__main__":
    ocr = OCR("api.svc.ltd")

    result = ocr.Recognition("foo.png")

    result.SaveImage("foo.result.jpg")

    for r in result.Texts:
        print(r.Text, r.Confidence)