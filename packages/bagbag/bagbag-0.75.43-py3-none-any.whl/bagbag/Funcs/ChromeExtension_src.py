from .. import Tools, Http, String, Time, Lg
import copy

def ChromeExtensionDownload(id_or_url:str, output_file:str, chromeversion:str='125.0.6422.113'):
    from urllib.parse import urlparse
    from urllib.parse import urlencode
    from urllib.request import urlopen
    import os

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    try:
        ext_url = urlparse(id_or_url)
        ext_id = os.path.basename(ext_url.path)
    except:
        ext_id = id_or_url

    crx_base_url = 'https://clients2.google.com/service/update2/crx'
    crx_params = urlencode({
        'response': 'redirect',
        'prodversion': chromeversion, # chrome的版本
        'acceptformat': 'crx2,crx3',
        'x': 'id=' + ext_id + '&uc'
    })

    crx_url = crx_base_url + '?' + crx_params
    crx_path = output_file if output_file is not None else ext_id + '.crx'

    with open(crx_path, 'wb') as file:
        file.write(urlopen(crx_url).read())

def chromeExtensionInfomation_1(x:Tools.XPath, res:dict) -> dict:
    rres = copy.deepcopy(res)

    # res['link'] = resp.URL
    rres['name'] = x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/a").Text()

    rres['category'] = String(', '.join([i[1] for i in String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r"<a.+?>(.+?)</a>")])).HTMLDecode()
    try:
        rres['users'] = int(String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r">([0-9,]+) user")[0][1].replace(',', ""))
    except:
        raise Exception("get_users_error")

    try:
        rres['score'] = float(String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[1]/span").Text()).RegexFind(r'(.+?)\((.+?) ratings\)')[0][1])
    except:
        raise Exception("get_score_error")
    rres['rates'] = String(String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[1]/span").Text()).RegexFind(r'(.+?)\((.+?) ratings\)')[0][2]).UnitToNumber()
    
    # Lg.Trace(rres)
    
    try:
        rres["version"] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[1]").Html()).RegexFind(r'<div.+?>Version</div><div.+?>(.+?)</div>')[0][1]
    except:
        raise Exception("get_version_error")
    rres['update_time_string'] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1]
    rres['update_timestamp'] = Time.Strptime(String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1])
    rres['description'] = x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]").Text()

    rres['isalive'] = True

    return rres

# dliccfbpegdcmlflaidhhnloeofgdnce
# obpgepecmhhglbagkeopjnmalogkhpjo
def chromeExtensionInfomation_2(x:Tools.XPath, res:dict) -> dict:
    rres = copy.deepcopy(res)
    rres['name'] = x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/a").Text()

    rres['category'] = String(', '.join([i[1] for i in String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r"<a.+?>(.+?)</a>")])).HTMLDecode()
    rres['users'] = int(String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r">([0-9,]+) user")[0][1].replace(',', ""))
    
    rres['score'] = float(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[1]/span/span/span[1]").Text())
    rres['rates'] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[1]/span/span/span[2]/a/p").Text().split()[0]).UnitToNumber()
    rres["version"] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[1]").Html()).RegexFind(r'<div.+?>Version</div><div.+?>(.+?)</div>')[0][1]
    rres['update_time_string'] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1]
    rres['update_timestamp'] = Time.Strptime(String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1])
    rres['description'] = x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]").Text()

    rres['isalive'] = True

    # Lg.Trace(rres)
    return rres

# cmogeohlpljgihhbafbnincahfmafbfn
def chromeExtensionInfomation_3(x:Tools.XPath, res:dict) -> dict:
    rres = copy.deepcopy(res)
    rres['name'] = x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/a").Text()

    rres['category'] = String(', '.join([i[1] for i in String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r"<a.+?>(.+?)</a>")])).HTMLDecode()
    rres['users'] = int(String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r">([0-9,]+) user")[0][1].replace(',', ""))
    
    rres['score'] = 0
    rres['rates'] = 0

    rres["version"] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[1]").Html()).RegexFind(r'<div.+?>Version</div><div.+?>(.+?)</div>')[0][1]
    rres['update_time_string'] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1]
    rres['update_timestamp'] = Time.Strptime(String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1])
    rres['description'] = x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]").Text()

    rres['isalive'] = True

    # Lg.Trace(rres)
    return rres

# mcdigjbnihajokfiolophengnjlcgeeb
def chromeExtensionInfomation_4(x:Tools.XPath, res:dict) -> dict:
    rres = copy.deepcopy(res)

    # res['link'] = resp.URL
    rres['name'] = x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/a").Text()

    rres['category'] = String(', '.join([i[1] for i in String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r"<a.+?>(.+?)</a>")])).HTMLDecode()
    rres['users'] = int(String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r">([0-9,]+) user")[0][1].replace(',', ""))
    rres['score'] = float(String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[1]/span").Text()).RegexFind(r'(.+?)\((.+?) ratings\)')[0][1])
    rres['rates'] = String(String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[1]/span").Text()).RegexFind(r'(.+?)\((.+?) ratings\)')[0][2]).UnitToNumber()
    
    rres["version"] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]/ul/li[1]").Html()).RegexFind(r'<div.+?>Version</div><div.+?>(.+?)</div>')[0][1]
    rres['update_time_string'] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1]
    rres['update_timestamp'] = Time.Strptime(String(x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1])
    rres['description'] = x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]").Text()

    rres['isalive'] = True

    return rres

# mhdijfejkhicinfgimimoohidelagmfn
def chromeExtensionInfomation_5(x:Tools.XPath, res:dict) -> dict:
    rres = copy.deepcopy(res)
    rres['name'] = x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/a").Text()

    rres['category'] = String(', '.join([i[1] for i in String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r"<a.+?>(.+?)</a>")])).HTMLDecode()
    rres['users'] = 0
    
    rres['score'] = 0
    rres['rates'] = 0
    rres["version"] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[1]").Html()).RegexFind(r'<div.+?>Version</div><div.+?>(.+?)</div>')[0][1]
    rres['update_time_string'] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1]
    rres['update_timestamp'] = Time.Strptime(String(x.Find("/html/body/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1])
    rres['description'] = x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]").Text()

    rres['isalive'] = True

    # Lg.Trace(rres)
    return rres

# alcgpfgkdjbabelklflpfkooadcfgoao
def chromeExtensionInfomation_6(x:Tools.XPath, res:dict) -> dict:
    rres = copy.deepcopy(res)
    rres['name'] = x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/a").Text()

    rres['category'] = String(', '.join([i[1] for i in String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r"<a.+?>(.+?)</a>")])).HTMLDecode()
    rres['users'] = int(String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r">([0-9,]+) user")[0][1].replace(',', ""))
    
    rres['score'] = 0
    rres['rates'] = 0

    rres["version"] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]/ul/li[1]").Html()).RegexFind(r'<div.+?>Version</div><div.+?>(.+?)</div>')[0][1]
    rres['update_time_string'] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1]
    rres['update_timestamp'] = Time.Strptime(String(x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1])
    rres['description'] = x.Find("/html/body/c-wiz/div/div/main/div/section[2]/div[2]").Text()

    rres['isalive'] = True

    # Lg.Trace(rres)
    return rres

# mfelkljfkmmafbmpodfancdighjdngcb
def chromeExtensionInfomation_7(x:Tools.XPath, res:dict) -> dict:
    rres = copy.deepcopy(res)
    rres['name'] = x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/a").Text()

    rres['category'] = String(', '.join([i[1] for i in String(x.Find("/html/body/c-wiz/div/div/main/div/section[1]/section/div[1]/div[2]").Html()).RegexFind(r"<a.+?>(.+?)</a>")])).HTMLDecode()
    rres['users'] = 0
    
    rres['score'] = 0
    rres['rates'] = 0
    rres["version"] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]/ul/li[1]").Html()).RegexFind(r'<div.+?>Version</div><div.+?>(.+?)</div>')[0][1]
    rres['update_time_string'] = String(x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1]
    rres['update_timestamp'] = Time.Strptime(String(x.Find("/html/body/c-wiz/div/div/main/div/section[3]/div[2]/ul/li[2]").Html()).RegexFind(r'<div .+?>Updated</div><div>(.+?)</div>')[0][1])
    rres['description'] = x.Find("/html/body/c-wiz/div/div/main/div/section[2]/div[2]").Text()

    rres['isalive'] = True

    # Lg.Trace(rres)
    return rres

def ChromeExtensionInfomation(id_or_url_or_pagesource:str) -> dict:
    res = {
        # 'name': "",     # str
        # "category": "", # str
        # "score": "",    # float
        # "rates": "",    # int                                                                                                                               
        # "users": "",    # int                                                                                                                                   
        # "version": "",  # string                                                                                                                              
        # "update_timestamp": "",     # int                                                                                                                        
        # "update_time_string": "",   # string                                                                                                                
        # "description": "",  # text                                                                                                                            
        # "link": "",     # string                                                                                                                                 
        # "extension_id": "", # string                                                                                                                         
        # "isalive": "",  # bool 
    }
    if id_or_url_or_pagesource.startswith("https://") or id_or_url_or_pagesource.startswith("http://"):
        resp = Http.Get(id_or_url_or_pagesource, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}) 
        res['extension_id'] = id_or_url_or_pagesource.strip('/').split('/')[-1]
        pagesource = resp.Content
    elif len(id_or_url_or_pagesource) == 32:
        resp = Http.Get(f"https://chromewebstore.google.com/detail/{id_or_url_or_pagesource}", headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}) 
        res['extension_id'] = id_or_url_or_pagesource
        pagesource = resp.Content
    else:
        pagesource = id_or_url_or_pagesource
    
    x = Tools.XPath(pagesource)

    if x.Find('/html/body/c-wiz/div/div/main/div/h1') != None:
        if x.Find('/html/body/c-wiz/div/div/main/div/h1').Text() == 'This item is not available':
            res['isalive'] = False
            return res
        else:
            raise Exception("????????")
    
    try:
        # Lg.Trace()
        res = chromeExtensionInfomation_1(x, res)
    except Exception as e:
        # Lg.Error()
        # Lg.Trace()
        # Lg.Trace(str(e))
        if str(e) == "get_users_error":
            # Lg.Trace()
            try:
                res = chromeExtensionInfomation_5(x, res)
            except:
                res = chromeExtensionInfomation_7(x, res)
        elif str(e) == 'get_version_error':
            # Lg.Trace()
            res = chromeExtensionInfomation_4(x, res) 
        elif str(e) == 'get_score_error':
            # Lg.Trace()
            # Lg.Error("")
            try:
                # Lg.Trace()
                res = chromeExtensionInfomation_2(x, res)
            except:
                # Lg.Trace()
                # Lg.Error("")
                try:
                    res = chromeExtensionInfomation_3(x, res)
                except:
                    res = chromeExtensionInfomation_6(x, res)
        else:
            raise e
        
    
    return res