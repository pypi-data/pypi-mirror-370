from ... import Http, String, Lg

import requests
import urllib3
import socket

def GetRealUrl(url:str) -> str | None:
    if url.startswith("http://t.co/"):
        url = 'https' + url[4:]

    if url.startswith('https://t.co/'):
        try:
            resp = Http.Get(url, followRedirect=False, randomUA=False)
            # Lg.Trace(resp)
            uu = None 
            while True:
                # import ipdb
                # ipdb.set_trace()
                # Lg.Trace()
                if resp.StatusCode > 300 and resp.StatusCode < 310:
                    # Lg.Trace()
                    headers = resp.Headers
                    if 'location' in headers and headers['location'][0] != "/":
                        # Lg.Trace()
                        uu = headers["location"]
                        break 
                    else:
                        # Lg.Trace()
                        break 

                elif resp.StatusCode == 200:
                    urlfromtitle = String(resp.Content).RegexFind("<title>(.+)</title>")
                    if len(urlfromtitle) != 0:
                        urlfromtitle = urlfromtitle[0][1]
                        # Lg.Trace(uu)
                        if not String(urlfromtitle).IsURL():
                            # Lg.Trace("Not url")
                            uu = None 
                            break 
                        else:
                            if urlfromtitle != '/':
                                uu = urlfromtitle
                            else:
                                uu = None 
                                break 
                    else:
                        # Lg.Trace(url, uu, resp)
                        break 
                else:
                    # Lg.Trace()
                    break 
                
                if uu == None:
                    # Lg.Trace()
                    break 

                if len(uu) < 30:
                    # Lg.Trace('checking', uu)
                    try:
                        resp = Http.Get(uu, followRedirect=False, randomUA=False)
                    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError, socket.gaierror):
                        break 
                else:
                    break 
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError, socket.gaierror):
            # Lg.Trace()
            uu = None  

        # Lg.Trace(url + ' ==> ' + str(uu))
        return uu

    else:
        raise Exception("只能转换t.co域名的短链")