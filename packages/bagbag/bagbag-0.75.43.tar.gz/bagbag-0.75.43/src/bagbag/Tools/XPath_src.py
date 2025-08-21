from __future__ import annotations

#print("load " + '/'.join(__file__.split('/')[-2:]))

import lxml.html 
import lxml.html.soupparser

class XPath():
    def __init__(self, html:str|lxml.html.HtmlElement):
        if type(html) == str:
            try:
                self.root = lxml.html.fromstring(html)
            except:
                self.root = lxml.html.soupparser.fromstring(html)
        elif type(html) == lxml.html.HtmlElement:
            self.root = html 
        else:
            raise Exception("Unsupport type: ", str(type(html)))
    
    def _find(self, xpath:str) -> XPath | None:
        """
        > If the xpath is found, return the first matched XPath object, otherwise return None
        
        :param xpath: The XPath expression to search for
        :type xpath: str
        :return: XPath object
        """
        res = self.root.xpath(xpath)
        if len(res) == 0:
            return None 
        else:
            return XPath(lxml.html.tostring(res[0]).decode('utf-8'))
    
    def _findAll(self, xpath:str) -> list[XPath]:
        res = self.root.xpath(xpath)
        if len(res) == 0:
            return []
        else:
            return [XPath(lxml.html.tostring(i).decode('utf-8')) for i in res]
        
    def FindAll(self, xpath:str|list) -> list[XPath]:
        if type(xpath) == str:
            return self._findAll(xpath)
        else:
            result = []
            for x in xpath:
                result = result + self._findAll(x)

            return result
    
    def Find(self, xpath:str|list) -> XPath | None:
        if type(xpath) == str:
            return self._find(xpath)
        else:
            idx = self.Except(xpath)
            if idx == None:
                return None 
            else:
                return self._find(xpath[idx])
    
    def Except(self, *xpath:str|list) -> int | None:
        if type(xpath[0]) == list:
            xpath = xpath[0]
            
        for x in range(len(xpath)):
            if self._find(xpath[x]) != None:
                return x

        return None 
    
    def Attribute(self, name:str) -> str | None:
        """
        If the attribute name is in the element, return the attribute value, otherwise return None
        
        :param name: The name of the attribute to get
        :type name: str
        :return: The value of the attribute name.
        """
        if name in self.root.attrib:
            return self.root.attrib[name]
        else:
            return None 
        
    def Text(self) -> str:
        """
        It returns the text content of the element of the HTML document

        :return: The text content of the root element.
        """
        return str(self.root.text_content())

    def Html(self) -> str:
        """
        Return the HTML of the element.

        :return: The HTML of the element.
        """
        return lxml.html.tostring(self.root).decode('utf-8')

# x = XPath('string')
# x.FindAll("//div[contains(@class, 'message default')]") # 找div标签的class属性包含message和default的
# x.Find("//div[contains(@class, 'media_wrap')]") # 找div标签的class属性包含media_wrap的
# x.Find("//div[@class='text']") # 找div标签的class属性等于text的
# x.Find(f"/html/body/div[1]/div/div/div/main/div/div[4]/section/div[{idx}]/article/aside/div/a/span") # 根据XPath来查找
# x.Find("//div[@class='profile-website']/span/a") # 根据属性和xpath来查找