from .... import Http, Json
from ... import RateLimit

class API():
    def __init__(self, key:str) -> None:
        self.key = key 
        self.headers = {'Ok-Access-Key': self.key}
        self.domain = 'www.oklink.com'
        self.rl = RateLimit("5/s")
    
    def CheckLabel(self, chan:str, address:list[str]) -> list[dict]:
        '''
        只可以批量查询20个同一个链的地址的标签. 支持的链有：BTC, BCH, LTC, DASH, DOGE, ETH, OKTC, XLAYER, BSC, ETC, POLYGON, AVAXC, ETHW, DIS, FTM, OP, ARBITRUM, KLAYTN, ZKSYNC, GNOSIS, RONIN, LINEA, POLYGON_ZKEVM, APT, SUI, TRON, STARKNET, BASE, SCROLL, OMEGA, OPBNB
        返回的数据格式是
        [
            {
                "label": [
                    "OKX.Cold Wallet"
                ],
                "address": "0x539c92186f7c6cc4cbf443f26ef84c595babbca1"
            }
        ]
        '''

        address = ','.join(address)
        url = f'https://{self.domain}/api/v5/explorer/address/entity-label?chainShortName={chan}&address={address}'

        self.rl.Take()
        resp = Http.Get(url, headers=self.headers)

        if resp.StatusCode != 200:
            raise Exception(f"状态码不为200: {resp.StatusCode} ==> {resp.Content}")
        
        content = Json.Loads(resp.Content)
        data = content['data']

        resp = []
        for item in data:
            resp.append({
                'label': item['label'].split(','),
                "address": item['address']
            })

        return resp