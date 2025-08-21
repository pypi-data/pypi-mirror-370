from ..... import Http

import json
import uuid
import time

#print("load " + '/'.join(__file__.split('/')[-2:]))

url = 'https://www.binance.com/bapi/composite/v1/public/official-channel/verify'

def Twitter(account:str, waiteOnRateLimit:bool=True) -> bool:
    tu = f"https://twitter.com/{account}"
    data = {"content": tu}

    while True:
        headers = {
            "bnc-uuid": str(uuid.uuid4()),
            "content-type": "application/json",
        }
        
        resp = Http.PostRaw(url, json.dumps(data), headers=headers)

        if resp.StatusCode == 200:
            break 

        elif resp.StatusCode == 429:
            if waiteOnRateLimit == True:
                time.sleep(30)
            else:
                raise Exception(resp)

    c = json.loads(resp.Content)

    if len(c["data"]['data']) == 0:
        return False 
    
    for d in c['data']['data']:
        if d['content'] == tu:
            return True 
    
    return False 
