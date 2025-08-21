import inspect

import requests 
from urllib3.exceptions import InsecureRequestWarning
from requests_toolbelt.utils import dump

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from io import BytesIO, SEEK_SET, SEEK_END

from ..String import String

from random_user_agent.user_agent import UserAgent as useragent_generator
from random_user_agent.params import SoftwareName as useragent_softwarename
from random_user_agent.params import OperatingSystem as useragent_operatingsystem 

useragents = useragent_generator(
    software_names=[
        useragent_softwarename.CHROME.value,
        useragent_softwarename.CHROMIUM.value,
        useragent_softwarename.EDGE.value,
        # useragent_softwarename.FIREFOX.value,
        # useragent_softwarename.OPERA.value,
    ], 
    operating_systems=[
        useragent_operatingsystem.WINDOWS.value,
        useragent_operatingsystem.LINUX.value,
        useragent_operatingsystem.MAC.value,
        useragent_operatingsystem.MAC_OS_X.value,
        useragent_operatingsystem.MACOS.value,
        useragent_operatingsystem.FREEBSD.value,
    ],
    limit=50
).get_user_agents()

import random

#print("load http")

class responseStream(object):
    def __init__(self, request_iterator):
        self._bytes = BytesIO()
        self._iterator = request_iterator

    def _load_all(self):
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position):
        current_position = self._bytes.seek(0, SEEK_END)
        while current_position < goal_position:
            try:
                current_position += self._bytes.write(next(self._iterator))
            except StopIteration:
                break

    def tell(self):
        return self._bytes.tell()

    def read(self, size=None):
        left_off_at = self._bytes.tell()
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

        self._bytes.seek(left_off_at)
        return self._bytes.read(size)
    
    def seek(self, position, whence=SEEK_SET):
        if whence == SEEK_END:
            self._load_all()
        else:
            self._bytes.seek(position, whence)

class Response():
    def __init__(self):
        self.Headers:dict = None # dict[str]str
        self.Content:str = None # str 
        self.StatusCode:int = None # int
        self.URL:str = None # str
        self.Debug:str = None # str
        self.ContentBytes:bytes = None 
    
    def __str__(self) -> str:
        Debug = None
        if self.Debug != None:
            if len(self.Debug) > 160:
                Debug = String(self.Debug[:160]).Repr() + "..."
            else:
                Debug = String(self.Debug[:160]).Repr() 
        
        Content = None 
        if self.Content != None:
            if len(self.Content) > 160:
                Content = String(self.Content[:160]).Repr() + "..."
            else:
                Content = String(self.Content[:160]).Repr()
        return f"Http.Response(\n    URL={self.URL}, \n    StatusCode={self.StatusCode}, \n    headers={self.Headers}, \n    Debug={Debug}, \n    Content={Content}\n)"

    def __repr__(self) -> str:
        return str(self)

def makeResponse(response:requests.Response, Debug:bool, readBodySize:int) -> Response:
    resp = Response()

    # print(response)

    if Debug:
        resp.Debug = dump.dump_all(response).decode("utf-8")
    
    st = responseStream(response.iter_content(512))
    if not readBodySize:
        content = st.read()
    else:
        content = st.read(readBodySize)
        
    if content:
        resp.Content = content.decode("utf-8", errors="ignore")
        resp.ContentBytes = content
    
    resp.Headers = response.headers 
    resp.StatusCode = response.status_code
    resp.URL = response.url 
    
    return resp

def makeRequest(cfgargs:dict, reqargs:dict):
    funcmap = {
        'Get': requests.get,
        'Head':requests.head,
        'Get':requests.get,
        'PostRaw':requests.post,
        'PostJson':requests.post,
        'PostForm':requests.post,
        'Delete':requests.delete,
        'PutForm':requests.put,
        'PutRaw':requests.put,
        'PutJson':requests.put,
    }

    if cfgargs['randomUA'] and "User-Agent" not in reqargs['headers']:
        reqargs['headers']["User-Agent"] = random.choice(useragents)['user_agent']

    timeouttimes = 0
    while True:
        try:
            response = funcmap[cfgargs['funcname']](
                **reqargs
            )
            return makeResponse(response, cfgargs['debug'], cfgargs['readBodySize'])
        except requests.exceptions.Timeout as e:
            timeouttimes += 1
            if cfgargs['timeoutRetryTimes'] < timeouttimes:
                raise e

def Get(url:str, Params:dict=None, timeout:int=15, headers:dict={}, readBodySize:int=None, followRedirect:bool=True, proxy:str=None,  timeoutRetryTimes:int=0, insecureSkipVerify:int=False, randomUA:bool=True, debug:bool=False):
    varables = locals()
    
    reqargs = {
        "url": url,
        "timeout": timeout, 
        "allow_redirects": followRedirect,
        "proxies": {
            'http': proxy,
            "https": proxy,
        },
        "verify": (not insecureSkipVerify),
        "stream": True,
        "headers": headers,
        "params": Params,
    }

    cfgargs = {
        "funcname": inspect.currentframe().f_code.co_name,
    }
    for key in ["randomUA", "timeoutRetryTimes", "debug", "readBodySize"]:
        cfgargs[key] = varables[key]

    return makeRequest(cfgargs, reqargs)

def Head(url:str, timeout:int=15, headers:dict={}, readBodySize:int=None, followRedirect:bool=True, proxy:str=None, timeoutRetryTimes:int=0, insecureSkipVerify:int=False, randomUA:bool=True, debug:bool=False):
    varables = locals()

    reqargs = {
        "url": url,
        "timeout": timeout, 
        "allow_redirects": followRedirect,
        "proxies": {
            'http': proxy,
            "https": proxy,
        },
        "verify": (not insecureSkipVerify),
        "stream": True,
        "headers": headers,
    }

    cfgargs = {
        "funcname": inspect.currentframe().f_code.co_name,
    }
    for key in ["randomUA", "timeoutRetryTimes", "debug", "readBodySize"]:
        cfgargs[key] = varables[key]

    return makeRequest(cfgargs, reqargs)

def PostRaw(url:str, data:str, timeout:int=15, headers:dict={}, readBodySize:int=None, followRedirect:bool=True, proxy:str=None, timeoutRetryTimes:int=0, insecureSkipVerify:int=False, randomUA:bool=True, debug:bool=False):
    varables = locals()

    reqargs = {
        "url": url,
        "data": data,
        "timeout": timeout, 
        "allow_redirects": followRedirect,
        "proxies": {
            'http': proxy,
            "https": proxy,
        },
        "verify": (not insecureSkipVerify),
        "stream": True,
        "headers": headers,
    }

    cfgargs = {
        "funcname": inspect.currentframe().f_code.co_name,
    }
    for key in ["randomUA", "timeoutRetryTimes", "debug", "readBodySize"]:
        cfgargs[key] = varables[key]

    return makeRequest(cfgargs, reqargs)

def PostJson(url:str, json:dict | list,timeout:int=15, headers:dict={}, readBodySize:int=None, followRedirect:bool=True, proxy:str=None, timeoutRetryTimes:int=0, insecureSkipVerify:int=False, randomUA:bool=True, debug:bool=False):
    varables = locals()

    reqargs = {
        "url": url,
        "json": json,
        "timeout": timeout, 
        "allow_redirects": followRedirect,
        "proxies": {
            'http': proxy,
            "https": proxy,
        },
        "verify": (not insecureSkipVerify),
        "stream": True,
        "headers": headers,
    }

    cfgargs = {
        "funcname": inspect.currentframe().f_code.co_name,
    }
    for key in ["randomUA", "timeoutRetryTimes", "debug", "readBodySize"]:
        cfgargs[key] = varables[key]

    return makeRequest(cfgargs, reqargs)

def PostForm(url:str, data:dict, timeout:int=15, headers:dict={}, readBodySize:int=None, followRedirect:bool=True, proxy:str=None, timeoutRetryTimes:int=0, insecureSkipVerify:int=False, randomUA:bool=True, debug:bool=False):
    varables = locals()

    reqargs = {
        "url": url,
        "data": data,
        "timeout": timeout, 
        "allow_redirects": followRedirect,
        "proxies": {
            'http': proxy,
            "https": proxy,
        },
        "verify": (not insecureSkipVerify),
        "stream": True,
        "headers": headers,
    }

    cfgargs = {
        "funcname": inspect.currentframe().f_code.co_name,
    }
    for key in ["randomUA", "timeoutRetryTimes", "debug", "readBodySize"]:
        cfgargs[key] = varables[key]

    return makeRequest(cfgargs, reqargs)

def Delete(url:str, timeout:int=15, headers:dict={}, readBodySize:int=None, followRedirect:bool=True, proxy:str=None, timeoutRetryTimes:int=0, insecureSkipVerify:int=False, randomUA:bool=True, debug:bool=False):
    varables = locals()

    reqargs = {
        "url": url,
        "timeout": timeout, 
        "allow_redirects": followRedirect,
        "proxies": {
            'http': proxy,
            "https": proxy,
        },
        "verify": (not insecureSkipVerify),
        "stream": True,
        "headers": headers,
    }

    cfgargs = {
        "funcname": inspect.currentframe().f_code.co_name,
    }
    for key in ["randomUA", "timeoutRetryTimes", "debug", "readBodySize"]:
        cfgargs[key] = varables[key]

    return makeRequest(cfgargs, reqargs)

def PutForm(url:str, data:dict,timeout:int=15, headers:dict={}, readBodySize:int=None, followRedirect:bool=True, proxy:str=None, timeoutRetryTimes:int=0, insecureSkipVerify:int=False, randomUA:bool=True, debug:bool=False):
    varables = locals()

    reqargs = {
        "url": url,
        "data": data,
        "timeout": timeout, 
        "allow_redirects": followRedirect,
        "proxies": {
            'http': proxy,
            "https": proxy,
        },
        "verify": (not insecureSkipVerify),
        "stream": True,
        "headers": headers,
    }

    cfgargs = {
        "funcname": inspect.currentframe().f_code.co_name,
    }
    for key in ["randomUA", "timeoutRetryTimes", "debug", "readBodySize"]:
        cfgargs[key] = varables[key]

    return makeRequest(cfgargs, reqargs) 
    
def PutRaw(url:str, data:str, timeout:int=15, headers:dict={}, readBodySize:int=None, followRedirect:bool=True, proxy:str=None, timeoutRetryTimes:int=0, insecureSkipVerify:int=False, randomUA:bool=True, debug:bool=False):
    varables = locals()

    reqargs = {
        "url": url,
        "data": data,
        "timeout": timeout, 
        "allow_redirects": followRedirect,
        "proxies": {
            'http': proxy,
            "https": proxy,
        },
        "verify": (not insecureSkipVerify),
        "stream": True,
        "headers": headers,
    }

    cfgargs = {
        "funcname": inspect.currentframe().f_code.co_name,
    }
    for key in ["randomUA", "timeoutRetryTimes", "debug", "readBodySize"]:
        cfgargs[key] = varables[key]

    return makeRequest(cfgargs, reqargs)

def PutJson(url:str, json:dict, timeout:int=15, headers:dict={}, readBodySize:int=None, followRedirect:bool=True, proxy:str=None, timeoutRetryTimes:int=0, insecureSkipVerify:int=False, randomUA:bool=True, debug:bool=False):
    varables = locals()

    reqargs = {
        "url": url,
        "json": json,
        "timeout": timeout, 
        "allow_redirects": followRedirect,
        "proxies": {
            'http': proxy,
            "https": proxy,
        },
        "verify": (not insecureSkipVerify),
        "stream": True,
        "headers": headers,
    }

    cfgargs = {
        "funcname": inspect.currentframe().f_code.co_name,
    }
    for key in ["randomUA", "timeoutRetryTimes", "debug", "readBodySize"]:
        cfgargs[key] = varables[key]

    return makeRequest(cfgargs, reqargs)

if __name__ == "__main__":
    # resp = Head("https://httpbin.org/redirect/2", debug=True)
    # print(resp)

    # resp = Get("https://httpbin.org", debug=True)
    # print(resp)

    resp = PutForm("http://127.0.0.1:8878", {"a": "b", "c": "d"})
    print(resp)