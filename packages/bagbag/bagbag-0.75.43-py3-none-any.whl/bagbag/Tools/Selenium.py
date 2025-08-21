from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.common.by import By as webby
import selenium
from selenium.webdriver.common.keys import Keys as webkeys
from selenium.webdriver.firefox.options import Options as firefoxoptions
from selenium.webdriver.chrome.options import Options as chromeoptions

# from seleniumwire import webdriver as seleniumwirewebdriver
# from seleniumwire.utils import decode as decodeResponseBody

import time
import random
import typing
import copy
import base64

#print("load " + '/'.join(__file__.split('/')[-2:]))

from ..Http import useragents 
from .. import Lg
from ..Thread import Thread
from .URL_src import URL
from ..String import String 
from .. import Os
from ..File import File
from .. import Cmd

seleniumChromeWireSkipFilesSuffix = (
    # 图片
    '.png', 
    '.jpg', 
    '.gif', 
    '.jpeg', 
    '.tiff', 
    '.psd', 
    '.raw', 
    '.webp', 
    '.eps',
    '.svg',
    '.bmp',
    '.pdf',
    '.pcx',
    '.tga',
    '.exif',
    '.fpx',
    # 视频
    '.avi',
    '.wmv',
    '.mpg',
    '.mpeg',
    '.mov',
    '.rm',
    '.rmvb',
    '.swf',
    '.flv',
    '.mp4',
    '.asf',
    '.dat',
    '.asx',
    '.wvx',
    '.mpe',
    '.mpa',
    # 音频
    '.mp3',
    '.wma',
    '.wav',
    '.mid',
    '.ape',
    '.flac',

    # 其它
    # '.aiff', # 声音文件
    # '.aej', '.cab', '.rar', # 压缩文件
    # '.awd', # 传真文件
    # '.bak', #备份文件
    # '.scr', #屏保文件
    # '.sys', #系统文件
    # '.ttf', '.font', #字体文件
    # '.doc', #文档文件
)
    
def retryOnError(func):
    def ware(self, *args, **kwargs): # self是类的实例
        if self.ToRetryOnError == False:
            res = func(self, *args, **kwargs)
            return  
        
        if self.browserName in ["chrome", "chromewire"]:
            while True:
                try:
                    res = func(self, *args, **kwargs)

                    try:
                        NeedRefresh = False
                        # 如果载入页面失败, 有个Reload的按钮
                        if hasattr(self, "Find"):
                            if self._find("/html/body/div[1]/div[2]/div/button[1]", 0):
                                if self._find("/html/body/div[1]/div[2]/div/button[1]").Text() == "Reload":
                                    NeedRefresh = True
                        elif hasattr(self, "se") and hasattr(self.se, "Find"):
                            if self.se._find("/html/body/div[1]/div[2]/div/button[1]", 0):
                                if self.se._find("/html/body/div[1]/div[2]/div/button[1]").Text() == "Reload":
                                    NeedRefresh = True

                        if hasattr(self, "PageSource"):
                            page = self.PageSource()
                        elif hasattr(self, "se") and hasattr(self.se, "PageSource"):
                            page = self.se.PageSource()
                        
                        if hasattr(self, "Url"):
                            url = self.Url()
                        elif hasattr(self, "se") and hasattr(self.se, "Url"):
                            url = self.se.Url()

                        chklists = [
                            [
                                'This page isn’t working',
                                'ERR_EMPTY_RESPONSE',
                                'didn’t send any data',
                                URL(url).Parse().Host,
                            ],
                            [
                                'This site can’t be reached',
                                'unexpectedly closed the connection',
                                'ERR_CONNECTION_CLOSED',
                                URL(url).Parse().Host,
                            ],
                            [
                                "This site can’t be reached",
                                "took too long to respond",
                                "ERR_TIMED_OUT",
                                URL(url).Parse().Host,
                            ],
                            [
                                "No internet",
                                "There is something wrong with the proxy server, or the address is incorrect",
                                "ERR_PROXY_CONNECTION_FAILED",
                            ],
                            [
                                'ERR_CONNECTION_RESET',
                                'This site can’t be reached',
                                'The connection was reset',
                                URL(url).Parse().Host,
                            ]
                        ]
                        for chklist in chklists:
                            if False not in map(lambda x: x in page, chklist):
                                NeedRefresh = True 
                        
                        if NeedRefresh:
                            if hasattr(self, "Refresh"):
                                self.Refresh()
                            elif hasattr(self, "se") and hasattr(self.se, "Refresh"):
                                self.se.Refresh()
                            time.sleep(5)
                        else:
                            return res

                    except Exception as e:
                        if hasattr(self, "closed") and self.closed:
                            break 
                        elif hasattr(self, "se") and hasattr(self.se, "closed") and self.se.closed:
                            break
                        else:
                            raise e
                    time.sleep(1)
                except Exception as e:
                    chklist = [
                        'ERR_CONNECTION_CLOSED',
                        'ERR_EMPTY_RESPONSE',
                        'ERR_TIMED_OUT',
                        'ERR_PROXY_CONNECTION_FAILED',
                        'ERR_CONNECTION_RESET',
                    ]
                    if True in map(lambda x: x in str(e), chklist):
                        Lg.Trace("有错误, 自动刷新")
                        if hasattr(self, "Refresh"):
                            self.Refresh()
                        elif hasattr(self, "se") and hasattr(self.se, "Refresh"):
                            self.se.Refresh()
                        time.sleep(5)
                    else:
                        raise e

        elif self.browserName == "firefox":
            res = func(self, *args, **kwargs)
            return 

    return ware

# > The SeleniumElement class is a wrapper for the selenium.webdriver.remote.webelement.WebElement
# class
class SeleniumElement():
    def __init__(self, element:selenium.webdriver.remote.webelement.WebElement, se:seleniumBase, ToRetryOnError:bool):
        self.element = element
        self.se = se
        self.driver = self.se.driver
        self.browserName = self.se.browserName
        self.browserRemote = self.se.browserRemote
        self.ToRetryOnError = ToRetryOnError
    
    def Clear(self) -> SeleniumElement:
        """
        Clear() clears the text if it's a text entry element
        """
        self.element.clear()
        return self
    
    @retryOnError
    def Click(self) -> SeleniumElement:
        """
        Click() is a function that clicks on an element
        """
        if self.browserName in ["chrome", "chromewire"] and not self.browserName:
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": random.choice(useragents)['user_agent']})

        self.element.click()

        return self
    
    def Text(self) -> str:
        """
        The function Text() returns the text of the element
        :return: The text of the element.
        """
        return self.element.text

    def Attribute(self, name:str) -> str:
        """
        This function returns the value of the attribute of the element
        
        :param name: The name of the element
        :type name: str
        :return: The attribute of the element.
        """
        return self.element.get_attribute(name)
    
    def Input(self, string:str) -> SeleniumElement:
        """
        The function Input() takes in a string and sends it to the element
        
        :param string: The string you want to input into the text box
        :type string: str
        """
        self.element.send_keys(string)
        return self
    
    @retryOnError
    def Submit(self) -> SeleniumElement:
        """
        Submit() is a function that submits the form that the element belongs to
        """
        if self.browserName in ["chrome", "chromewire"] and not self.browserName:
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": random.choice(useragents)['user_agent']})
        
        self.element.submit()

        return self
    
    @retryOnError
    def PressEnter(self) -> SeleniumElement:
        """
        It takes the element that you want to press enter on and sends the enter key to it
        """

        if self.browserName  in ["chrome", "chromewire"] and not self.browserName:
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": random.choice(useragents)['user_agent']})
        
        self.element.send_keys(webkeys.ENTER)

        return self
    
    def ScrollIntoElement(self) -> SeleniumElement:
        self.driver.execute_script("arguments[0].scrollIntoView(true);", self.element)
        return self

    def HTML(self) -> str:
        return self.element.get_attribute('innerHTML')
    
    def Image(self) -> bytes:
        # 执行JavaScript将图片转换为Base64编码
        captcha_base64 = self.driver.execute_script("""
            var img = arguments[0];
            var canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            var ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, img.width, img.height);
            return canvas.toDataURL('image/png').split(',')[1];
        """, self.element)

        return base64.b64decode(captcha_base64)

class seleniumBase():
    def Find(self, xpath:str|list, timeout:int=60, scrollIntoElement:bool=True, retryOnError:int=5) -> SeleniumElement|None:
        """
        This is a Python function that finds a Selenium element based on an XPath string or list of XPath
        strings, with optional parameters for timeout, scrolling, and retrying on errors.
        
        :param xpath: The xpath expression used to locate the element(s) on the webpage
        :type xpath: str|list
        :param timeout: The maximum amount of time (in seconds) to wait for the element to be found before
        timing out and returning None, defaults to 60
        :type timeout: int (optional)
        :param scrollIntoElement: scrollIntoElement is a boolean parameter that determines whether the web
        page should be scrolled to bring the element into view before attempting to find it using the
        specified XPath. If set to True, the page will be scrolled to bring the element into view before
        attempting to find it. If set to False, the, defaults to True
        :type scrollIntoElement: bool (optional)
        :param retryOnError: The retryOnError parameter specifies the number of times the function should
        retry finding the element if an error occurs during the search. If the element is not found after
        the specified number of retries, the function will return None, defaults to 5
        :type retryOnError: int (optional)
        :return: The function `Find` returns a `SeleniumElement` object if it is found, or `None` if it is
        not found.
        """
        if type(xpath) == str:
            return self._find(xpath, timeout, scrollIntoElement, retryOnError)
        else:
            idx = self.Except(xpath, timeout=timeout)
            if idx == None:
                return None 
            else:
                return self._find(xpath[idx], timeout, scrollIntoElement, retryOnError)

    def _find(self, xpath:str, timeout:int=60, scrollIntoElement:bool=True, retryOnError:int=5) -> SeleniumElement|None:
        """
        > Finds an element by xpath, waits for it to appear, and returns it
        
        :param xpath: The xpath of the element you want to find
        :type xpath: str
        :param timeout: , defaults to 8 second
        :type timeout: int (optional)
        :param scrollIntoElement: If True, the element will be scrolled into view before returning it,
        defaults to True
        :type scrollIntoElement: bool (optional)
        :return: SeleniumElement
        """
        waited = 0
        errcount = 0
        while True:
            try:
                el = self.driver.find_element(webby.XPATH, xpath)
                if scrollIntoElement:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
                return SeleniumElement(el, self, self.ToRetryOnError)
            except selenium.common.exceptions.NoSuchElementException as e: 
                if timeout == 0:
                    return None 
                elif timeout == -1:
                    time.sleep(1)
                elif timeout > 0:
                    time.sleep(1)
                    waited += 1
                    if waited > timeout:
                        return None 
            except Exception as e:
                if retryOnError != 0:
                    errcount += 1
                    if errcount > retryOnError:
                        raise e 
                    time.sleep(1)
                else:
                    raise e 

        # import ipdb
        # ipdb.set_trace()
    
    def Exists(self, xpath:str, timeout:int=0) -> bool:
        return self._find(xpath, timeout=timeout) != None
    
    def StatusCode(self) -> int:
        self.driver.stat
    
    def ResizeWindow(self, width:int, height:int):
        """
        :param width: The width of the window in pixels
        :type width: int
        :param height: The height of the window in pixels
        :type height: int
        """
        self.driver.set_window_size(width, height)
    
    def ScrollRight(self, pixel:int):
        """
        ScrollRight(self, pixel:int) scrolls the page to the right by the number of pixels specified in
        the pixel parameter
        
        :param pixel: The number of pixels to scroll by
        :type pixel: int
        """
        self.driver.execute_script("window.scrollBy("+str(pixel)+",0);")
    
    def ScrollLeft(self, pixel:int):
        """
        Scrolls the page left by the number of pixels specified in the parameter.
        
        :param pixel: The number of pixels to scroll by
        :type pixel: int
        """
        self.driver.execute_script("window.scrollBy("+str(pixel*-1)+",0);")

    def ScrollUp(self, pixel:int):
        """
        Scrolls up the page by the number of pixels specified in the parameter.
        
        :param pixel: The number of pixels to scroll up
        :type pixel: int
        """
        self.driver.execute_script("window.scrollBy(0, "+str(pixel*-1)+");")

    def ScrollDown(self, pixel:int):
        """
        Scrolls down the page by the specified number of pixels
        
        :param pixel: The number of pixels to scroll down
        :type pixel: int
        """
        self.driver.execute_script("window.scrollBy(0, "+str(pixel)+");")

    def Url(self) -> str:
        """
        > The `Url()` function returns the current URL of the page
        :return: The current url of the page
        """
        return self.driver.current_url
    
    def Cookie(self) -> list[dict]:
        """
        This function gets the cookies from the driver and returns them as a list of dictionaries
        """
        return self.driver.get_cookies()
    
    def SetCookie(self, cookie:dict|list[dict]):
        """
        If the cookie is a dictionary, add it to the driver. If it's a list of dictionaries, add each
        dictionary to the driver
        
        :param cookie: dict|list[dict]
        :type cookie: dict|list[dict]
        """
        if type(cookie) == dict:
            self.driver.add_cookie(cookie)
        else:
            for i in cookie:
                self.driver.add_cookie(i)
    
    def Refresh(self):
        """
        Refresh() refreshes the current page
        """
        self.driver.refresh()
    
    def GetSession(self) -> str:
        """
        The function GetSession() returns the session ID of the current driver
        :return: The session ID of the driver.
        """
        return self.driver.session_id
    
    @retryOnError
    def Get(self, url:str):
        """
        The function Get() takes a string as an argument and uses the driver object to navigate to the
        url.
        
        :param url: The URL of the page you want to open
        :type url: str
        """

        if self.browserName in ["chrome", "chromewire"]:
            # if self.userAgent != None:
            #     self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.userAgent})
            if self.userAgent == None and self.randomUA:
                if not self.browserRemote:
                    self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": random.choice(useragents)['user_agent']})
            

        self.driver.get(url)
    
    def PageSource(self) -> str:
        """
        It returns the page source of the current page
        :return: The page source of the current page.
        """
        return self.driver.page_source

    def Title(self) -> str:
        """
        The function Title() returns the title of the current page
        :return: The title of the page
        """
        return self.driver.title
    
    def Close(self):
        """
        The function closes the browser window and quits the driver
        """
        self.closed = True
        if self.browserName == "chromewire":
            del(self.driver.requests)
        self.driver.close()
        self.driver.quit()
    
    def ClearIdent(self):
        if self.browserName in ["chrome", "chromewire"] :
            try:
                self.driver.delete_all_cookies()
            except:
                pass 
            try:
                self.driver.execute_script("localStorage.clear();")
            except:
                pass 
            try:
                self.driver.execute_script("sessionStorage.clear();")
            except:
                pass 
            try:
                self.driver.execute_script("const dbs = await window.indexedDB.databases();dbs.forEach(db => { window.indexedDB.deleteDatabase(db.name)});")
            except:
                pass
        else:
            raise Exception("未实现")
    
    def ExceptXPath(self, *xpath:str|list, timeout:int=30) -> int | None:
        """
        It waits for some certain elements to appear on the screen.
        
        :param : xpath:str - The xpaths of the element you want to find
        :type : str
        :param timeout: The number of seconds to wait for the element to appear, defaults to 30
        :type timeout: int (optional)
        :return: The index of the xpath that is found.
        """
        if type(xpath[0]) == list:
            xpath = xpath[0]
            
        for _ in range(timeout*2):
            for x in range(len(xpath)):
                if self._find(xpath[x], 0, scrollIntoElement=False) != None:
                    return x
            time.sleep(0.5)

        return None 

    def ExceptKeywords(self, *keywords:str|list, timeout:int=30) -> int | None:
        if type(keywords[0]) == list:
            keywords = keywords[0]
            
        for _ in range(timeout*2):
            for x in range(len(keywords)):
                if keywords[x] in self.PageSource():
                    return x 
                
            time.sleep(0.5)

        return None 
    
    def SwitchTabByID(self, number:int):
        """
        SwitchTabByID(self, number:int) switches to the tab with the given ID, start from 0
        
        :param number: The number of the tab you want to switch to
        :type number: int
        """
        self.driver.switch_to.window(self.driver.window_handles[number])
    
    def SwitchTabByIdent(self, ident:str):
        self.driver.switch_to.window(ident)

    def Tabs(self) -> list[str]:
        return self.driver.window_handles
    
    def NewTab(self) -> str:
        """
        It opens a new tab, and returns the ident of the new tab
        :return: The new tab's ident.
        """
        tabs = self.driver.window_handles
        self.driver.execute_script('''window.open();''')
        for i in self.driver.window_handles:
            if i not in tabs:
                return i
     
    def Screenshot(self, filepath:str) -> str:
        """
        It takes a screenshot of the current page and saves it to the filepath.
        只支持PNG. 
        
        :param filepath: The path to save the screenshot to
        :type filepath: str
        :return: The filepath of the screenshot.
        """
        filepath = Os.Path.Uniquify(filepath)
        self.driver.save_screenshot(filepath)
        return filepath
    
    def MaximizeWindow(self):
        self.driver.maximize_window()
    
    def ExecuteJavaScript(self, code:str) -> typing.Any:
        return self.driver.execute_script(code)
    
    def __enter__(self):
        return self 
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.Close()
        except:
            pass

class Chrome(seleniumBase):
    def __init__(
            self, 
            chromedriverServer:str=None,
            seleniumServer:str=None, 
            PACFileURL:str=None, 
            httpProxy:str=None, 
            sessionID=None, 
            randomUA:bool=True,
            userAgent:str=None,
            # chromeLocation:str=None,
            extensionsPath:str|list=None,
            retryOnError:bool=True,
        ):
        self.ToRetryOnError = retryOnError

        options = webdriver.ChromeOptions()
        # options = chromeoptions()

        if isinstance(extensionsPath, str):
            options.add_extension(extensionsPath)
        elif isinstance(extensionsPath, list):
            for ep in extensionsPath:
                options.add_extension(ep)

        # 这样设置chromedriver的位置会报错:session not created: DevToolsActivePort file doesn't exist
        # 不知为何.
        # 可以这样: driver = webdriver.Chrome(executable_path=chrome_driver_path)
        # 未测试
        # if chromeLocation != None:
        #     options.binary_location = chromeLocation
        # else:
        #     options.binary_location = Cmd.Where("chromedriver")

        # 防止通过navigator.webdriver来检测是否是被selenium操作
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")

        if Os.GetUID() == 0:
            options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--ignore-certificate-errors")
        options.add_argument('--ignore-ssl-errors')
        # options.add_argument('--no-sandbox')

        if userAgent != None:
            options.add_argument('--user-agent=' + userAgent + '')
        elif randomUA:
            options.add_argument('--user-agent=' + random.choice(useragents)['user_agent'] + '')
        self.randomUA = randomUA
        self.userAgent = userAgent

        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        if PACFileURL:
            options.add_argument("--proxy-pac-url=" + PACFileURL)
        elif httpProxy:
            options.add_argument('--proxy-server=' + httpProxy)

        if chromedriverServer:
            self.driver = webdriver.Remote(
                command_executor=chromedriverServer,
                options=options
            )
        elif seleniumServer:
            if not seleniumServer.endswith("/wd/hub"):
                seleniumServer = seleniumServer + "/wd/hub"
            self.driver = webdriver.Remote(
                command_executor=seleniumServer,
                options=options
            )
        else:
            self.driver = webdriver.Chrome(
                options=options,
            )

        if sessionID:
            self.Close()
            self.driver.session_id = sessionID
        
        self.ResizeWindow(1400, 1000)
        
        self.browserName = "chrome"
        self.browserRemote = seleniumServer != None 
        self.closed = False

# class seleniumFlowRequest():
#     def __init__(self) -> None:
#         self.Time:int = None 
#         self.Headers:dict = None 
#         self.Method:str = None 
#         self.URL:str = None 
#         self.BodyBytes:bytes = b'' 
#         self.Body:str = ''
    
#     def __repr__(self) -> str:
#         body = String(String(self.Body).Repr()).Ommit(80)
#         return f"seleniumFlowRequest(Time={self.Time}, Method={self.Method}, URL={self.URL}, Headers={self.Headers} Body={body})"

#     def __repr__(self) -> str:
#         body = String(String(self.Body).Repr()).Ommit(80)
#         return f"seleniumFlowRequest(Time={self.Time}, Method={self.Method}, URL={self.URL}, Headers={self.Headers} Body={body})"

# class seleniumFlowResponse():
#     def __init__(self) -> None:
#         self.Time:int = None 
#         self.BodyBytes:bytes = b'' 
#         self.Body:str = '' 
#         self.StatusCode:int = None 
#         self.Headers:dict = None 
    
#     def __repr__(self) -> str:
#         body = String(String(self.Body).Repr()).Ommit(80)
#         return f"seleniumFlowResponse(Time={self.Time}, StatusCode={self.StatusCode}, Headers={self.Headers} Body={body})"

#     def __str__(self) -> str:
#         body = String(String(self.Body).Repr()).Ommit(80)
#         return f"seleniumFlowResponse(Time={self.Time}, StatusCode={self.StatusCode}, Headers={self.Headers} Body={body})"

# class SeleniumFlow():
#     def __init__(self,id:str, req:seleniumFlowRequest, resp:seleniumFlowResponse) -> None:
#         self.Request = req
#         self.Response = resp
#         self.ID = id
    
#     def __repr__(self) -> str:
#         return f"SeleniumFlow(\n\tID={self.ID} \n\tRequest={self.Request} \n\tResponse={self.Response}\n)" 

# class ChromeWire(seleniumBase):
#     def __init__(self, 
#             blockSuffix:tuple[str]=seleniumChromeWireSkipFilesSuffix,
#             maxRequests:int=None, 
#             requestStorage:str="memory", # disk
#             urlFilterRegex:list[str]=[], 
#             excludeHosts:list[str]=[],
#             httpProxy:str=None, 
#             sessionID=None, 
#             randomUA:bool=True,
#             userAgent:str=None,
#             chromeLocation:str=None):
        
#         """
#         :param blockSuffix: A tuple of file suffixes to block. list是中括号, tuple是小括号
#         :type blockSuffix: tuple[str]
#         :param maxRequests: The maximum number of requests to store
#         :type maxRequests: int
#         :param requestStorage: The storage type for requests and responses. Can be either memory or disk, defaults to disk
#         :type requestStorage: str (optional)
#         :param urlFilterRegex: A list of regular expressions that will be used to filter requests
#         :type urlFilterRegex: list[str]
#         :param excludeHosts: A list of hosts to exclude from interception
#         :type excludeHosts: list[str]
#         :param httpProxy: The HTTP proxy to use
#         :type httpProxy: str
#         :param sessionID: If you want to use an existing session, you can pass the session ID here
#         :param randomUA: Whether to use a random user agent, defaults to True
#         :type randomUA: bool (optional)
#         """

#         options = webdriver.ChromeOptions()

#         if chromeLocation != None:
#             options.binary_location = chromeLocation
#         else:
#             options.binary_location = Cmd.Where("chromedriver")

#         # 防止通过navigator.webdriver来检测是否是被selenium操作
#         options.add_argument("--disable-blink-features")
#         options.add_argument("--disable-blink-features=AutomationControlled")

#         if Os.GetUID() == 0:
#             options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")

#         options.add_argument("--ignore-certificate-errors")

#         if userAgent != None:
#             options.add_argument('--user-agent=' + userAgent + '')
#         elif randomUA:
#             options.add_argument('--user-agent=' + random.choice(useragents)['user_agent'] + '')
#         self.randomUA = randomUA
#         self.userAgent = userAgent

#         options.add_experimental_option("excludeSwitches", ["enable-automation"])

#         seleniumwire_options = {
#             # 'request_storage': 'memory',  # Store requests and responses in memory only
#             # 'request_storage_max_size': maxRequests  # Store no more than 100 requests in memory
#         }

#         if maxRequests != None:
#             seleniumwire_options['request_storage_max_size'] = maxRequests

#         if requestStorage == "memory":
#             seleniumwire_options['request_storage'] = requestStorage
#             if maxRequests == None:
#                 seleniumwire_options['request_storage_max_size'] = 300

#         if excludeHosts != []:
#             seleniumwire_options['exclude_hosts'] = excludeHosts
        
#         if httpProxy != None:
#             seleniumwire_options['proxy'] = {
#                 'http': httpProxy,
#                 # 'https': httpProxy
#             }
        
#         # Lg.Trace(seleniumwire_options)
        
#         self.driver = seleniumwirewebdriver.Chrome(
#             options=options,
#             seleniumwire_options=seleniumwire_options
#         )

#         if self.driver.scopes != []:
#             self.driver.scopes = urlFilterRegex
#             # [
#             #     '.*stackoverflow.*',
#             #     '.*github.*'
#             # ]
        
#         def interceptor(request):
#             # Block PNG, JPEG and GIF images
#             if request.path.lower().endswith(blockSuffix):
#                 request.abort()

#         if blockSuffix != None:
#             self.driver.request_interceptor = interceptor

#         if sessionID:
#             self.Close()
#             self.driver.session_id = sessionID
        
#         self.ResizeWindow(1400, 1000)
        
#         self.browserName = "chromewire"
#         self.browserRemote = False
#         self.closed = False
#         self.blockSuffix = blockSuffix

#         self.tmpCacheFlows = []
    
#     def Flows(self, clean:bool=True) -> typing.Iterable[SeleniumFlow]:
#         """
#         > It iterates through all the requests made by the browser, and returns a `SeleniumFlow` object
#         for each request. 
#         这个方法迭代现有的队列里面的数据, 当到达末尾的时候就结束迭代. 
#         可以多次调用这个方法来获取新的flow. 
#         注意打开某些页面之后, 浏览器会隔一段时间就发起一次请求, 及时没有新Get页面, 也会有新的flow出现. 
#         如果是发起了请求, 但是还在等待回复, 或者正在传送大的回复回来, 则response为None, 在控制台看到的是在pending. 拿到完整的回复才会显示, 一瞬间刷出来.
#         如果是连接出错, 有request, 但response也还是为None. 
#         """
#         while True:
#             Lg.Trace()
#             # for req in self.tmpCacheFlows:
#             if len(self.tmpCacheFlows) == 0:
#                 time.sleep(1)
#                 if len(self.driver.requests) == 0:
#                     break 

#                 self.tmpCacheFlows = copy.deepcopy(self.driver.requests)
#                 Lg.Trace()
#                 if clean:
#                     Lg.Trace()
#                     del(self.driver.requests)
#                 Lg.Trace()
            
#             req = self.tmpCacheFlows.pop(0)

#             if self.blockSuffix != None and len(self.blockSuffix) != 0:
#                 if req.path.lower().endswith(self.blockSuffix):
#                     continue

#             resp = req.response

#             freq = seleniumFlowRequest()
#             freq.URL = req.url
#             freq.Time = req.date.timestamp()
#             freq.Method = req.method
#             freq.Headers = {}
#             for key in req.headers:
#                 freq.Headers[key] = req.headers[key]
#             if req.body != None:
#                 freq.BodyBytes = req.body
#                 freq.Body = req.body.decode(errors="ignore")

#             if resp != None:
#                 fresp = seleniumFlowResponse()
#                 fresp.Headers = {}
#                 for key in resp.headers:
#                     fresp.Headers[key] = resp.headers[key]
#                 fresp.StatusCode = resp.status_code
#                 fresp.Time = resp.date.timestamp()
#                 if resp.body != None:
#                     try:
#                         fresp.BodyBytes = decodeResponseBody(resp.body, resp.headers.get('Content-Encoding', 'identity'))
#                     except Exception as e:
#                         Lg.Warn("解码body报错:", e)
#                         fresp.BodyBytes = b''

#                     fresp.Body = fresp.BodyBytes.decode(errors="ignore")
#                     # if 'content-encoding' not in fresp.Headers:
#                     #     fresp.Body = resp.body.decode(errors="ignore")
#                     #     fresp.BodyBytes = resp.body 
#                     # else:
#                     #     if fresp.Headers['content-encoding'].strip() == 'br':
#                     #         # Lg.Trace("Before:", resp.body[:80])
#                     #         fresp.BodyBytes = brotli.decompress(resp.body)
#                     #         # Lg.Trace("After:", fresp.BodyBytes[:80])
#                     #         fresp.Body = fresp.BodyBytes.decode(errors="ignore")
#                     #     elif fresp.Headers['content-encoding'].strip() == 'gzip':
#                     #         fresp.BodyBytes = gzip.decompress(resp.body)
#                     #         fresp.Body = fresp.BodyBytes.decode(errors="ignore")
#                     #     else:
#                     #         Lg.Warn("未知的 Content-Encoding:", fresp.Headers['content-encoding'])
#                     #         fresp.Body = resp.body.decode(errors="ignore")
#                     #         fresp.BodyBytes = resp.body 
#             else:
#                 fresp = None 

#             Lg.Trace()
#             yield SeleniumFlow(req.id, freq, fresp)

#             if len(self.tmpCacheFlows) == 0:
#                 Lg.Trace()
#                 break 

if __name__ == "__main__":
    # Local 
    # with Chrome() as se:
    # Remote 
    # with Chrome("http://127.0.0.1:4444") as se:

    # With PAC 
    # with Firefox(PACFileURL="http://192.168.1.135:8000/pac") as se:
    # with Chrome("http://127.0.0.1:4444", PACFileURL="http://192.168.1.135:8000/pac") as se:

    # Example of PAC file
    # function FindProxyForURL(url, host)
    # {
    #     if (shExpMatch(host, "*.onion"))
    #     {
    #         return "SOCKS5 192.168.1.135:9150";
    #     }
    #     if (shExpMatch(host, "ipinfo.io"))
    #     {
    #         return "SOCKS5 192.168.1.135:7070";
    #     }
    #     return "DIRECT";
    # }

    # With Proxy
    # with Chrome("http://192.168.1.229:4444", httpProxy="http://192.168.168.54:8899") as se:
        
        # PAC test 
        # se.Get("http://ipinfo.io/ip")
        # print(se.PageSource())

        # se.Get("https://ifconfig.me/ip")
        # print(se.PageSource())
        
        # se.Get("http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/")
        # print(se.PageSource())

        # Function test
        # se.Get("https://find-and-update.company-information.service.gov.uk/")
        # inputBar = se.Find("/html/body/div[1]/main/div[3]/div/form/div/div/input")
        # inputBar.Input("ade")
        # button = se.Find('//*[@id="search-submit"]').Click()
        # print(se.PageSource())

    with Chrome(randomUA=False) as se:
        se.Get("http://google.com")
        while True:
            for request in se.Flows():
                ctype = request.Response.Headers['content-encoding'] if 'content-encoding' in request.Response.Headers else "plain"
                Lg.Trace({
                    "url": request.Request.URL,
                    "content-encoding": ctype,
                    "body": request.Response.BodyBytes[:80],
                })

            time.sleep(1)

