from Crypto.Cipher import AES as AAAES
from Crypto import Random
import base64

#print("load cryptoo")

class AES():
    def __init__(self, key:str, mode:str="cfb"): 
        """
        The function takes a key and a mode as arguments, and sets the block size, key, and mode of the
        cipher
        
        :param key: The key to use for the encryption
        :type key: str
        :param mode: The mode of operation for the cipher object; must be one of "ecb", "cbc", "cfb",
        "ofb", defaults to cfb
        :type mode: str (optional)
        """
        self.key = key.encode("utf-8")
        self.mode = {
            "cfb": AAAES.MODE_CFB, 
            "cbc": AAAES.MODE_CBC,
            "ecb": AAAES.MODE_ECB, 
            "ofb": AAAES.MODE_OFB,
        }[mode.lower()]
    
    def pading(self, text):
        """对加密字符的处理"""
        return text + (len(self.key) - len(text) % len(self.key)) * chr(len(self.key) - len(text) % len(self.key))

    def unpading(self, text):
        """对解密字符的处理"""
        return text[0:-ord(text[-1:])]

    def Encrypt(self, raw:str) -> str:
        # raw = self._pad(raw)
        if self.mode == AAAES.MODE_ECB:
            cipher = AAAES.new(self.key, self.mode)
            ciphertext = cipher.encrypt(bytes(self.pading(raw), encoding="utf8"))
            encrypt_string = base64.b64encode(ciphertext).decode("utf-8")
        else:
            iv = Random.new().read(AAAES.block_size)
            cipher = AAAES.new(self.key, self.mode, iv)
            ciphertext = cipher.encrypt(bytes(self.pading(raw), encoding="utf8"))
            encrypt_string = base64.b64encode(iv + ciphertext).decode("utf-8")

        return encrypt_string

    def Decrypt(self, enc:str) -> str:
        enc = base64.b64decode(enc)
        if self.mode == AAAES.MODE_ECB:
            cipher = AAAES.new(self.key, self.mode)
            plain_text = cipher.decrypt(enc)
        else:
            iv = enc[:AAAES.block_size]
            cipher = AAAES.new(self.key, self.mode, iv)
            plain_text = cipher.decrypt(enc[AAAES.block_size:])

        return self.unpading(plain_text).decode("utf-8")

if __name__ == "__main__":

    for mode in ["ecb", "cbc", "cfb", "ofb"]:
        print(mode)
        a = AES("we1d3cwged6sh6k1", mode)

        e = a.Encrypt("enc = base64.b64decode(enc)")
        print(e)

        c = a.Decrypt(e)
        print(c)
    
    print(AES("we1d3cwged6sh6k1", "ecb").Decrypt("cP9Kr1qeHXLnWBsWHVF+yFZHjy5Hq7gNl8a/1Npwu88pfDXOLnTBECVtPMQ3rgpC"))