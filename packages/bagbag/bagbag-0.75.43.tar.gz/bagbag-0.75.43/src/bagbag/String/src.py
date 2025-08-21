## print("load string")
import typing 
from .vars import * 
import sys
import copy

sentimentAnalyzer = None
jiebaimported = None 
stopwords = None

class cryptoAddress():
    def __init__(self, ctype:str, address:str) -> None:
        self.Type:str = ctype 
        self.Address = address
    
    def __repr__(self) -> str:
        return f"cryptoAddress(Type={self.Type} Address={self.Address})"

    def __str__(self) -> str:
        return f"cryptoAddress(Type={self.Type} Address={self.Address})"

class sentimentResult():
    def __init__(self) -> None:
        self.Negative:float = 0 # 消极的
        self.Neutral:float = 0 # 中性的
        self.Positive:float = 0 # 积极的
        self.Compound:float = 0 # 复合情绪
    
    def __repr__(self) -> str:
        return f"sentimentResult(Negative={self.Negative} Neutral={self.Neutral} Positive={self.Positive} Compound={self.Compound})"

    def __str__(self) -> str:
        return f"sentimentResult(Negative={self.Negative} Neutral={self.Neutral} Positive={self.Positive} Compound={self.Compound})"

class String():
    def __init__(self, string:typing.Any):
        self.string = string

    def RemoveHTMLTags(self) -> str:
        import re
        p = re.compile(r'<.*?>')
        return p.sub('', self.string)

    def IsDigit(self) -> bool:
        try:
            float(self.string)
            return True
        except ValueError:
            return False
    
    def Sentiment(self) -> sentimentResult:
        global sentimentAnalyzer
        if sentimentAnalyzer == None:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            sentimentAnalyzer = SentimentIntensityAnalyzer()

        res = sentimentAnalyzer.polarity_scores(self.string)
        # {'neg': 0.189, 'neu': 0.811, 'pos': 0.0, 'compound': -0.8331}

        resr = sentimentResult()
        resr.Negative = res['neg']
        resr.Neutral = res['neu']
        resr.Positive = res['pos']
        resr.Compound = res['compound']

        return resr

    def GetEmail(self) -> list[str]:
        return [i[0] for i in self.RegexFind(emailPattern)]
    
    def GetCryptoAddress(self) -> list[cryptoAddress]:
        resca = []
        adds = []

        for ctype in addrPattern:
            pattern = addrPattern[ctype]
            text = self.string

            res = String(text).RegexFind(pattern)
            if len(res) != 0:
                for r in res:
                    address = r[0]

                    if len(String(text).RegexFind("[@_/#A-Za-z0-9]" + address)) != 0 or len(String(text).RegexFind(address + "[_/#A-Za-z0-9]")) != 0:
                        continue 

                    if len(String(address).RegexFind("[0-9]")) == 0:
                        continue 

                    if len(String(address).RegexFind("[A-Z]")) == 0:
                        continue 

                    if len(String(address).RegexFind("[a-z]",)) == 0:
                        continue 

                    if len(String(text).RegexFind('https{0,1}://.+?' + address)) != 0:
                        continue 

                    if len(String(address).RegexFind("[a-z]{"+str(int(len(address)/3))+",}")) != 0:
                        continue 

                    if len(String(address).RegexFind("[A-Z]{"+str(int(len(address)/3))+",}")) != 0:
                        continue 
                    
                    if address in adds:
                        for idx in range(len(resca)):
                            if resca[idx].Address == address:
                                resca[idx].Type.append(ctype)
                    else:
                        resca.append(cryptoAddress([ctype], address))
                        adds.append(address)

        for idx in range(len(resca)):
            resca[idx].Type = ','.join(set(resca[idx].Type))

        return resca
    
    def GetURL(self) -> list[str]:
        import re
        urls = re.findall(r'(?:http|ftp|https|ssh|ftps|sftp)://(?:[-\w./]|(?:%[\da-fA-F]{2}/))+', self.string, re.IGNORECASE)
        urls = list(set(urls))

        return urls
    
    def IsASCII(self) -> bool:
        return self.string.isascii()
    
    def GetDomain(self) -> list[str]:
        import validators
        import tld
        from ..Tools import URL
        dms = []
        for u in self.GetURL():
            try:
                h = URL(u).Parse().Host
            except:
                continue 
            if h.strip() != "" and h.strip() not in dms and tld.get_tld(h.strip(), fix_protocol=True, fail_silently=True) != None:
                dms.append(h.strip())
        
        for i in self.string.split():
            if validators.domain(i) == True and tld.get_tld(i, fix_protocol=True, fail_silently=True) != None and i.strip() not in dms:
                    dms.append(i.strip())
        
        return dms
    
    def __GetFirstLevelDomain(self) -> str | list[str]:
        import tld
        res = []
        for dm in self.GetDomain():
            r = tld.get_fld(dm, fix_protocol=True, fail_silently=True)
            if r != None:
                res.append(r)
        
        if len(res) == 0:
            return None 
        elif len(res) == 1:
            return res[0]
        else:
            return res
    
    def GetFirstLevelDomain(self) -> str | list[str]:
        import tldextract
        res = []
        for dm in self.GetDomain():
            extracted = tldextract.extract(dm)
            primordial_domain = f"{extracted.domain}.{extracted.suffix}"
            res.append(primordial_domain)
        
        if len(res) == 0:
            return None 
        elif len(res) == 1:
            return res[0]
        else:
            return res

    def HasChinese(self) -> bool:
        import re
        return len(re.findall(r'[\u4e00-\u9fff]+', self.string)) != 0
    
    def HasChineseSimplified(self) -> bool:
        import hanzidentifier
        hanzidentifier.is_simplified(self.string)
    
    def HasChineseTraditional(self) -> bool:
        import hanzidentifier
        hanzidentifier.is_traditional(self.string)
    
    def Language(self) -> str:
        """
        The function takes a string as input and returns the language of the string
        :return: The language of the string.
        """
        import langid
        return langid.classify(self.string)[0]

    def Repr(self) -> str:
        return str(repr(self.string).encode("ASCII", "backslashreplace"), "ASCII")[1:-1]
    
    def SimplifiedChineseToTraditional(self) -> str:
        import opencc
        return opencc.OpenCC('s2t.json').convert(self.string)
    
    def TraditionalChineseToSimplified(self) -> str:
        import opencc
        return opencc.OpenCC('t2s.json').convert(self.string)
    
    def Ommit(self, length:int) -> str:
        """
        If the length of the string is greater than the length of the argument, return the string up to
        the length of the argument and add "..." to the end. Otherwise, return the string
        
        :param length: The length of the string you want to return
        :type length: int
        :return: The string is being returned.
        """
        if len(self.string) > length:
            return self.string[:length] + "..."
        else:
            return self.string
        
    def Filter(self, chars:str="1234567890qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM", replaceTo:str="") -> str:
        """
        这个函数会根据指定的一组字符过滤掉字符串中的字符，并用指定的替换字符代替它们。

        参数 `chars` 是一个包含你想在过滤后字符串中保留的所有字符的字符串。在输入字符串中，任何不在 `chars` 字符串中的字符都会被替换为 `replaceTo` 字符串，默认为 1234567890qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM

        参数 `replaceTo` 用来指定替换字符，即在输入字符串中，任何在 `chars` 参数中找不到的字符都会被这个字符替换。例如，如果 `replaceTo` 设置为 `"*"`, 那么输入字符串中任何不在 `chars` 中的字符都会被替换为 `"*"`。

        函数返回的是一个新的字符串，其中输入字符串中任何不在指定 `chars` 参数中的字符都会被 `replaceTo` 参数替换。 
        """
        res = []
        for i in self.string:
            if i in chars:
                res.append(i)
            else:
                res.append(replaceTo)
        
        return ''.join(res)
    
    def Len(self) -> int:
        return len(self.string)
    
    def PinYin(self) -> str:
        import pypinyin
        res = pypinyin.lazy_pinyin(self.string, style=pypinyin.Style.TONE3)
        py = String(('-'.join(res)).replace(" ", "-")).Filter('1234567890qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM -').replace('--', '-')
        return py
    
    def EnsureUTF8(self) -> str:
        return self.string.encode('utf-8', errors='ignore').decode('utf-8')
    
    def HTMLDecode(self) -> str:
        import html
        return html.unescape(self.string)
    
    def HTMLEncode(self) -> str:
        import html
        return html.escape(self.string)

    def URLEncode(self) -> str:
        from urllib.parse import quote_plus
        return quote_plus(self.string)
    
    def URLDecode(self) -> str:
        from urllib.parse import unquote
        return unquote(self.string)

    def FormatHTML(self) -> str:
        import bs4
        from lxml import etree, html
        try:
            document_root = html.fromstring(self.string)
            return etree.tostring(document_root, encoding='unicode', pretty_print=True)
        except:
            soup = bs4.BeautifulSoup(self.string, 'html.parser')
            return soup.prettify()
    
    def IsURL(self, public:bool=False) -> bool:
        import validators
        return validators.url(self.string, public=public) == True

    def IsDomain(self) -> bool:
        import validators
        import tld
        if validators.domain(self.string) == True:
            if tld.get_tld(self.string, fix_protocol=True, fail_silently=True) != None:
                return True 
            
        return False
    
    def IsEmail(self) -> bool:
        import validators
        return validators.email(self.string) == True 
    
    def IsIBAN(self) -> bool:
        import validators
        return validators.iban(self.string) == True 

    def IsIPAddress(self) -> bool:
        import ipaddress
        try:
            ipaddress.ip_address(self.string)
            return True 
        except ValueError:
            return False 
    
    def IsIPv4(self) -> bool:
        import validators
        return validators.ipv4(self.string) == True
    
    def IsIPv4CIDR(self) -> bool:
        """
        Returns True if the string is a valid IPv4 CIDR notation, otherwise returns False
        
        >>> IsIPv4CIDR('1.1.1.1/8')
        True
        
        :return: True or False
        """
        import re
        pattern = re.compile(
            r'^'
            r'((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
            r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])'
            r'/([0-9]|[1-2][0-9]|3[0-2])'
            r'$'
        )
        return bool(pattern.match(self.string))
    
    def IsIPv4Public(self) -> bool:
        import ipaddress
        try:
            # 将字符串地址转换为ip地址对象
            ip_obj = ipaddress.ip_address(self.string)
            # 检查IP地址是否是私有地址
            if ip_obj.is_private:
                return False
            # 检查是否是特殊的保留地址，例如localhost
            if ip_obj.is_reserved:
                return False
            # 其他情况下认为是公网IP
            return True
        except ValueError:
            # 如果IP地址无效，返回False
            return False

    def IsIPv6(self) -> bool:
        import validators
        return validators.ipv6(self.string) == True
    
    def IsIPv6CIDR(self) -> bool:
        import validators
        """
        Returns True if the string is a valid IPv6 CIDR notation, otherwise False
        
        >>> ipv6_cidr('::1/128')
        True
        
        :return: True or False
        """
        return validators.ipv6_cidr(self.string) == True
    
    def IsMacAddress(self) -> bool:
        import validators
        return validators.mac_address(self.string) == True

    def IsUUID(self) -> bool:
        import validators
        return validators.uuid(self.string) == True 
    
    def IsMD5(self) -> bool:
        import validators
        return validators.md5(self.string) == True 
    
    def IsSHA1(self) -> bool:
        import validators
        return validators.sha1(self.string) == True 
    
    def IsSHA224(self) -> bool:
        import validators
        return validators.sha224(self.string) == True 
    
    def IsSHA256(self) -> bool:
        import validators
        return validators.sha256(self.string) == True 
    
    def IsSHA512(self) -> bool:
        import validators
        return validators.sha512(self.string) == True 
    
    def IsJCBCardNumber(self) -> bool:
        import validators
        """
        It checks if the card number is a JCB card number.
        :return: True or False
        """
        return validators.jcb(self.string) == True 
    
    def SmartSplit(self, chars_per_string: int = 3800) -> list[str]:
        def _text_before_last(substr: str) -> str:
            return substr.join(part.split(substr)[:-1]) + substr
        
        text = copy.deepcopy(self.string)

        parts = []
        while True:
            if len(text) < chars_per_string:
                parts.append(text)
                return parts

            part = text[:chars_per_string]

            if "\n" in part:
                part = _text_before_last("\n")
            elif ". " in part:
                part = _text_before_last(". ")
            elif " " in part:
                part = _text_before_last(" ")

            parts.append(part)
            text = text[len(part):]
    
    def IsDinersClubCardNumber(self) -> bool:
        import validators
        return validators.diners(self.string) == True 
    
    def IsMastercardCardNumber(self) -> bool:
        import validators
        return validators.mastercard(self.string) == True 

    def IsUnionpayCardNumber(self) -> bool:
        import validators
        return validators.unionpay(self.string) == True 

    def IsUnionpayCardNumber(self) -> bool:
        import validators
        return validators.unionpay(self.string) == True 
    
    def IsAmericanExpressCardNumber(self) -> bool:
        import validators
        return validators.amex(self.string) == True 

    def IsVisaCardNumber(self) -> bool:
        import validators
        return validators.visa(self.string) == True
    
    def RegexFind(self, pattern:str, multiline=False) -> list[list[str]]:
        import re
        res = []

        pattern1 = ""
        lasti = ""
        for idx in range(len(pattern)):
            i = pattern[idx]
            pattern1 = pattern1 + i
            if i == "(" and lasti != "\\" and (pattern[idx+1] != "?" and pattern[idx+2] != ":"):
                pattern1 = pattern1 + "?:"
            lasti = i 

        flags = 0
        if multiline:
            flags |= re.MULTILINE | re.DOTALL  # 添加DOTALL标志

        if pattern != pattern1:
            if multiline:
                reres1 = re.findall(pattern1, self.string, flags)
                reres2 = re.findall(pattern, self.string, flags)
            else:
                reres1 = re.findall(pattern1, self.string)
                reres2 = re.findall(pattern, self.string)
                
            for idx in range(len(reres1)):
                r1 = reres1[idx]
                r2 = reres2[idx]

                if type(r1) == tuple and type(r2) == tuple:
                    res.append(list(r1) + list(r2))
                elif type(r1) == tuple and type(r2) != tuple:
                    t = list()
                    t.append(r2)
                    res.append(list(r1) + t)
                elif type(r1) != tuple and type(r2) == tuple:
                    t = list()
                    t.append(r1)
                    res.append(t + list(r2))
                else:
                    t = list()
                    t.append(r1)
                    t.append(r2)
                    res.append(t)
        else:
            if multiline:
                reres = re.findall(pattern, self.string, flags)
            else:
                reres = re.findall(pattern, self.string)

            for i in reres:
                if type(i) == tuple:
                    res.append(list(i))
                else:
                    t = list()
                    t.append(i)
                    res.append(t)

        return res 
    
    def RegexReplace(self, pattern:str, string:str) -> str:
        import re
        return re.sub(pattern, string, self.string)

    def Markdown2HTML(self) -> str:
        import markdown2
        extras = [
            'tables', 
            'toc', 
            'fenced-code-blocks', 
            'footnotes', 
            'task_list',
            'break-on-newline',
            'cuddled-lists',
            'strike',
            'target-blank-links'
        ]
        return markdown2.markdown(self.string, extras=extras)

    def HTML2Markdown(self) -> str:
        import markdownify
        return markdownify.markdownify(self.string)

    def Cut(self, filterStopWords:bool=True) -> list[str]:
        """
        分词, 支持中英文, 或者混合
        """
        # import ipdb
        # ipdb.set_trace()

        global stopwords
        if stopwords == None:
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, 'stopwords.txt')

            stopwords = set()
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stopwords.add(line.strip())

        global jiebaimported
        if jiebaimported == None:
            import jieba
            import logging
            jieba.setLogLevel(logging.INFO)
            jiebaimported = True
        else:
            import jieba
            
        import re

        s = re.sub(symbols, ' ', self.string)  # 去掉标点

        ss = []
        last = ""
        for i in s:
            # if i == '，':
            #     ipdb.set_trace()
            if last == " " and i == " ":
                continue 

            if String(i).HasChinese() or String(i).RegexFind("[0-9a-zA-Z]") or i == " ":
                ss.append(i)
            else:
                ss.append(' ')

            last = i 

        # print(ss)
        sss = []
        for i in jieba.cut(''.join(ss), cut_all=False):
            if len(i) == 1 and i == ' ':
                continue 

            if filterStopWords and i in stopwords:
                continue

            sss.append(i)
        
        return sss

    def EditDistance(self, text:str) -> int:
        from Levenshtein import distance
        return distance(self.string, text)

    def EditDistanceRatio(self, text:str) -> float:
        from Levenshtein import ratio
        return ratio(self.string, text)
    
    def HexDecode(self) -> bytes:
        """
        解码十六进制表示形式的字节对象。例如: "^\\\\0\\\\0\\\\x84abcd\\\\r\\\\n"
        """
        import codecs
        # cleaned_hex_string = self.string.replace("\\x", "").replace("\\0", "00")
        # byte_array = codecs.decode(cleaned_hex_string, "hex")
        string = codecs.decode(self.string, 'unicode_escape')
        byte_array = string.encode('latin-1')

        return byte_array
    
    def HexEncode(self) -> str:
        """
        函数HexEncode接收一个bytes输入，将其转换为十六进制表示，并在每对字符前加上\\x进行格式化。
        :返回值 : HexEncode方法返回输入字符串格式化的十六进制表示。
        """
        import binascii
        print(type(self.string))
        hex_string = binascii.hexlify(self.string).decode('utf-8')
        formatted_hex_string = ''.join(['\\x' + hex_string[i:i+2] for i in range(0, len(hex_string), 2)])

        return formatted_hex_string
    
    def ExtractTextFromHTML(self) -> str:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(self.string, 'html5lib')
        # Get text by stripping out all tags
        text = soup.get_text(separator=' ', strip=True)
        return text
    
    def UnitToNumber(self) -> int:
        '''
        1K 输出: 1000
        1.5M 输出: 1500000
        2G 输出: 2000000000
        0.5T 输出: 500000000000
        1P 输出: 1000000000000000
        2.5E 输出: 2500000000000000000
        3Z 输出: 3000000000000000000000
        0.75Y 输出: 750000000000000000000000
        '''
        from decimal import Decimal, getcontext, InvalidOperation

        # 设置 Decimal 模块的精度
        getcontext().prec = 30

        units = {
            'K': Decimal('1E3'),
            'M': Decimal('1E6'),
            'G': Decimal('1E9'),
            'T': Decimal('1E12'),
            'P': Decimal('1E15'),
            'E': Decimal('1E18'),
            'Z': Decimal('1E21'),
            'Y': Decimal('1E24')
        }
        
        try:
            return int(Decimal(self.string))
        except InvalidOperation:
            unit = self.string[-1].upper()  # 提取最后一个字符作为单位
            try:
                number = Decimal(self.string[:-1])  # 使用 Decimal 进行高精度浮点数转换
            except InvalidOperation:
                raise ValueError(f"Invalid number format: {self.string[:-1]}")
            
            if unit in units:
                return int(number * units[unit])
            else:
                raise ValueError(f"Unknown unit: {unit}")

    def TokensCount(self, model:str='gpt-4') -> int:
        import tiktoken
        encoding = tiktoken.encoding_for_model(model) 
        tokens = encoding.encode(self.string)
        return len(tokens)
    
    def tokenize(self, text:str, usestopwords:bool) -> list[str]:
        if usestopwords:
            global stopwords
            if stopwords == None:
                import os
                script_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(script_dir, 'stopwords.txt')

                stopwords = set()
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        stopwords.add(line.strip())

        import re 
        import jieba 
        # 判断文本是否包含中文
        if re.search(r'[\u4e00-\u9fff]', text):
            if usestopwords:
                # 使用 jieba 切词处理中文，并过滤停用词
                return [word for word in jieba.cut(text) if word not in stopwords]
            else:
                return list(jieba.cut(text))
        else:
            if usestopwords:
                # 使用空格切词处理英文或其他语种，并过滤停用词
                return [word for word in text.split() if word not in stopwords]
            else:
                return text.split()
    
    def CosineSimilarityScore(self, text:str, usestopwords:bool=True) -> float:
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        # 分词
        tokens1 = self.tokenize(self.string, usestopwords)
        tokens2 = self.tokenize(text, usestopwords)
        
        # 创建词频向量化器
        vectorizer = CountVectorizer(token_pattern=r'(?u)\b\w+\b').fit_transform([' '.join(tokens1), ' '.join(tokens2)])
        vectors = vectorizer.toarray()
        
        # 计算余弦相似度矩阵
        cosine_sim_matrix = cosine_similarity(vectors)
        
        # 因为是两个字符串，相似度矩阵是2x2的，对角线为1，取[0,1]位置的相似度
        cosine_sim = cosine_sim_matrix[0, 1]
        
        return cosine_sim

if __name__ == "__main__":
    print(1, String("ABC").HasChinese())
    print(2, String("ddddd中kkkkkkk").HasChinese())
    print(3, String("\"wef\t测\b试....\n\tffef'").Repr())
    print(4, String("这是一段用鼠标写的简体中文").SimplifiedChineseToTraditional())
    print(5, String("這是一段用鍵盤點擊出來的軌跡").TraditionalChineseToSimplified())
    print(6, String("This is a 用鼠标写的简体中文").SimplifiedChineseToTraditional())
    print(7, String("This is a 用鼠标写的盤點擊出來的軌跡").PinYin())
    print(8, String("ac123bd456").RegexFind("([a-z])([a-z])[0-9]+"))     # ==> [['ac123', 'a', 'c'], ['bd456', 'b', 'd']]
    print(9, String("c123d456").RegexFind("([a-z])[0-9]+"))              # ==> [['c123', 'c'], ['d456', 'd']]
    print(10, String("c123d456").RegexFind("[a-z][0-9]+"))               # ==> [['c123'], ['d456']]
    print(11, String("(c123d456").RegexFind("(\\()[a-z][0-9]+"))         # ==> [['(c123', '(']]
    print(12, String("c123d456").RegexFind("(?:[a-z])[0-9]+"))           # ==> [['c123'], ['d456']]
    print(13, String("111-def").RegexFind("(111|222)-def"))              # ==> [['111-def', '111']]
    print(14, String("222-def").RegexFind("(111|222)-def"))              # ==> [['222-def', '222']]
    print(15, String("example@gov.com, s899@gov.uk").GetEmail())              # ==> [['222-def', '222']]
    