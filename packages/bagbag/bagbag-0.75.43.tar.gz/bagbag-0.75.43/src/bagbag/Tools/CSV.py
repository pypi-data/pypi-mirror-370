import csv 

#print("load " + '/'.join(__file__.split('/')[-2:]))

class Reader():
    def __init__(self, fpath:str, withHeader:bool=True):
        self.fpath = fpath 
        self.fd = open(self.fpath)
        self.csvrd = csv.reader(self.fd, delimiter=',', quotechar='"', escapechar='\\')
        
        self.withHeader = withHeader
        self.headers = None
        if self.withHeader:
            self.headers = next(self.csvrd)
    
    def SetHeaders(self, *headers):
        self.headers = headers
    
    def Read(self) -> dict | list:
        while True:
            try:
                r = next(self.csvrd)
                break 
            except StopIteration:
                raise StopIteration
            except Exception:
                pass 
        
        if self.headers != None:
            row = {}
            for idx in range(len(self.headers)):
                try:
                    row[self.headers[idx]] = r[idx]
                except IndexError:
                    row[self.headers[idx]] = "" 
        else:
            return r 
        
        return row
    
    def __iter__(self):
        while True:
            try:
                yield self.Read()
            except StopIteration:
                self.Close()
                return 
    
    def Close(self):
        self.fd.close()
        
class Writer():
    def __init__(self, fpath:str, mode:str="w", autoflush:bool=True):
        self.fpath = fpath
        self.fd = open(self.fpath, mode, newline='')
        self.csvwd = csv.writer(self.fd, delimiter=',', quotechar='"', escapechar='\\', doublequote=False)# , quoting=csv.QUOTE_NONE)
        self.fdmode = mode
        self.headers = None
        if self.fdmode != "w":
            try:
                self.headers = Reader(fpath).headers
            except StopIteration:
                self.fdmode = "w"
        self.autoflush = autoflush

    def SetHeaders(self, *headers):
        self.headers = headers
        if self.fdmode == "w":
            self.csvwd.writerow(headers)
    
    def Write(self, row:dict[str]):
        r = []
        for header in self.headers:
            if header in row:
                r.append(row[header])
            else:
                r.append("")
        
        self.csvwd.writerow(r)
        if self.autoflush:
            self.fd.flush()

    def Close(self):
        self.fd.close()
    
    def Flush(self):
        self.fd.flush()
    
    def __enter__(self):
        return self 
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.Close()
        except:
            pass

if __name__ == "__main__":
    w = Writer("test.csv")

    w.SetHeaders("h1", "h2")

    w.Write({"h1": "v1", "h2": '"v2,kkk|'})
    w.Write({"h1": "v,1", "h2": '"v222'})
    w.Write({"h1": "3", "h2": '"99kkk'})

    w.Close()

    # test.csv
    # h1,h2
    # v1,"\"v2,kkk|"
    # "v,1",\"v222
    # 3,\"99kkk

    r = Reader("test.csv")
    print(r.Read()) # {'h1': 'v1', 'h2': '"v2,kkk|'}

    for row in r:
        print(row) 
        # {'h1': 'v,1', 'h2': '"v222'}
        # {'h1': '3', 'h2': '"99kkk'}
    
    w = Writer("test.csv", "a")
    w.Write({"h1": "4", "h2": '5'}) 
    w.Write({"h1": "6", "h3": '7'}) # 6,

    w = Writer("test1.csv", "a")
    w.SetHeaders("h1", "h2")
    w.Write({"h1": "4", "h2": '5'}) 
    w.Write({"h1": "6", "h3": '7'}) # 6,
