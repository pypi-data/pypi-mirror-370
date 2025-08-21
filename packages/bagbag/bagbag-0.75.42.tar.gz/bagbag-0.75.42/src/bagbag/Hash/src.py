import hashlib
    
#print("load hash")

def Md5sum(data:str|bytes) -> str:
    if type(data) == str:
        data = data.encode('utf-8')
    return hashlib.md5(data).hexdigest()

def Md5sumFile(fpath:str, block_size=2**20) -> str:
    md5 = hashlib.md5()
    with open(fpath, "rb" ) as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def Sha256sum(data:str|bytes) -> str:
    if type(data) == str:
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def Sha256sumFile(fpath:str, block_size=2**20) -> str:
    sha256 = hashlib.sha256()
    with open(fpath, "rb" ) as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def Sha1sum(data:str|bytes) -> str:
    if type(data) == str:
        data = data.encode('utf-8')
    return hashlib.sha1(data).hexdigest()

def Sha1sumFile(fpath:str, block_size=2**20) -> str:
    sha1 = hashlib.sha1()
    with open(fpath, "rb" ) as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

if __name__ == "__main__":
    print(Md5sum("abc"))
    print(Sha256sum("abc"))
    print(Sha256sumFile("Hash.py"))
    print(Sha1sumFile("Hash.py"))