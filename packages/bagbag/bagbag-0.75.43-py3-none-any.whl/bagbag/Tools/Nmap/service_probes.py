from .service_probes_parser import parse_nmap_probes
from ... import String
import re
import copy
import os
from ... import Lg, Http

class ServiceProbes():
    def __init__(self, localfilepath:str=None, useonlinefile:bool=False) -> None:
        if localfilepath != None:
            nblines = [i for i in open(localfilepath)]
        elif useonlinefile != None:
            nblines = Http.Get("https://svn.nmap.org/nmap/nmap-service-probes").Content.splitlines()
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            nblines = [i for i in open(os.path.join(current_dir, 'nmap-service-probes'))]

        self.nbs = parse_nmap_probes(nblines)
            
        for idx in range(len(self.nbs)):
            self.nbs[idx]['probestring'] = String(self.nbs[idx]['probestring']).HexDecode()

            for midx in range(len(self.nbs[idx]['matches'])):
                try:
                    self.nbs[idx]['matches'][midx]['pattern'] = self.nbs[idx]['matches'][midx]['pattern'].encode('latin-1')
                except:
                    self.nbs[idx]['matches'][midx]['pattern'] = self.nbs[idx]['matches'][midx]['pattern'].encode('utf-8')

                if self.nbs[idx]['matches'][midx]['pattern_flag'] == 'i':
                    self.nbs[idx]['matches'][midx]['pattern'] = re.compile(self.nbs[idx]['matches'][midx]['pattern'], re.IGNORECASE)
                elif self.nbs[idx]['matches'][midx]['pattern_flag'] == 's':
                    self.nbs[idx]['matches'][midx]['pattern'] = re.compile(self.nbs[idx]['matches'][midx]['pattern'], re.DOTALL)
                else:
                    self.nbs[idx]['matches'][midx]['pattern'] = re.compile(self.nbs[idx]['matches'][midx]['pattern'])
                
                self.nbs[idx]['matches'][midx]['versioninfo']['name'] = self.nbs[idx]['matches'][midx]['name']
                self.nbs[idx]['matches'][midx]['versioninfo']['matchtype'] = 'match'

            for midx in range(len(self.nbs[idx]['softmatches'])):
                try:
                    self.nbs[idx]['softmatches'][midx]['pattern'] = self.nbs[idx]['softmatches'][midx]['pattern'].encode('latin-1')
                except:
                    self.nbs[idx]['softmatches'][midx]['pattern'] = self.nbs[idx]['softmatches'][midx]['pattern'].encode('utf-8')

                if self.nbs[idx]['softmatches'][midx]['pattern_flag'] == 'i':
                    self.nbs[idx]['softmatches'][midx]['pattern'] = re.compile(self.nbs[idx]['softmatches'][midx]['pattern'], re.IGNORECASE)
                elif self.nbs[idx]['softmatches'][midx]['pattern_flag'] == 's':
                    self.nbs[idx]['softmatches'][midx]['pattern'] = re.compile(self.nbs[idx]['softmatches'][midx]['pattern'], re.DOTALL)
                else:
                    self.nbs[idx]['softmatches'][midx]['pattern'] = re.compile(self.nbs[idx]['softmatches'][midx]['pattern'])
                
                self.nbs[idx]['softmatches'][midx]['versioninfo']['name'] = self.nbs[idx]['softmatches'][midx]['name']
                self.nbs[idx]['softmatches'][midx]['versioninfo']['matchtype'] = 'softmatch'

    def replace_placeholders(self, string, replacements):
        # 定义匹配 "$" 后跟数字的正则表达式
        pattern = re.compile(r'\$(\d+)')
        
        # 统计 replacements 的使用次数
        used_replacements = [False] * len(replacements)
        
        def replacer(match):
            # 获取匹配的数字
            index = int(match.group(1)) - 1
            # 如果 index 在 replacements 的范围内且未被使用过，则进行替换
            if 0 <= index < len(replacements) and not used_replacements[index]:
                used_replacements[index] = True
                return replacements[index]
            # 否则返回原匹配字符串
            return match.group(0)
        
        # 使用替换函数替换所有匹配项
        result = pattern.sub(replacer, string)
        return result

    def CheckApplication(self, send:bytes|str, recv:bytes|str) -> dict | None:
        if recv == b'' or recv == '':
            return None 

        if isinstance(send, str):
            try:
                send = send.encode('latin-1')
            except:
                send = send.encode('utf-8')
        
        if isinstance(recv, str):  
            try: 
                recv = recv.encode('latin-1')
            except:
                recv = recv.encode('utf-8')

        # Lg.Trace("send:", send)
        # Lg.Trace("recv:", recv)

        for nb in self.nbs:
            if send != String(nb['probestring']).HexDecode():
                continue 

            for match in (nb['matches'] + nb['softmatches']):
                res = match['pattern'].findall(recv)
                if len(res) != 0:
                    if isinstance(res[0], tuple):
                        res = list(res[0])
                        
                    for idx in range(len(res)):
                        res[idx] = res[idx].decode('latin-1')

                    versioninfo = copy.deepcopy(match['versioninfo'])

                    for key in versioninfo:
                        if '$' in versioninfo[key]:
                            versioninfo[key] = self.replace_placeholders(versioninfo[key], res)

                    return versioninfo
            
if __name__ == "__main__":
    from ... import Base64

    result = {
        "send": "",
        "recv": "U1NILTIuMC1kcm9wYmVhcl8yMDE5Ljc4DQoAAAF0BRSVcIN5+vyOCBHBv2RgTep9AAAAu2N1cnZlMjU1MTktc2hhMjU2LGN1cnZlMjU1MTktc2hhMjU2QGxpYnNzaC5vcmcsZWNkaC1zaGEyLW5pc3RwNTIxLGVjZGgtc2hhMi1uaXN0cDM4NCxlY2RoLXNoYTItbmlzdHAyNTYsZGlmZmllLWhlbGxtYW4tZ3JvdXAxNC1zaGEyNTYsZGlmZmllLWhlbGxtYW4tZ3JvdXAxNC1zaGExLGtleGd1ZXNzMkBtYXR0LnVjYy5hc24uYXUAAAAHc3NoLXJzYQAAABVhZXMxMjgtY3RyLGFlczI1Ni1jdHIAAAAVYWVzMTI4LWN0cixhZXMyNTYtY3RyAAAADWhtYWMtc2hhMi0yNTYAAAANaG1hYy1zaGEyLTI1NgAAABV6bGliQG9wZW5zc2guY29tLG5vbmUAAAAVemxpYkBvcGVuc3NoLmNvbSxub25lAAAAAAAAAAAAAAAAAOviM0xW"
    }

    n = ServiceProbes()

    res = n.CheckApplication(result['send'], Base64.Decode(result['recv']))

    Lg.Trace(res)