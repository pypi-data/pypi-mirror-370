from __future__ import annotations

import tronpy
from tronpy import Tron as TronAPI
from tronpy.providers import HTTPProvider

import traceback

#print("load " + '/'.join(__file__.split('/')[-2:]))

from .... import Http, Json, String, Lg, Time, Random

tronOfficialNodes = [
    '3.225.171.164',
    '52.53.189.99',
    '18.196.99.16',
    '34.253.187.192',
    '35.180.51.163',
    '54.252.224.209',
    '52.15.93.92',
    '34.220.77.106',
    '13.124.62.58',
    '18.209.42.127',
    '3.218.137.187',
    '34.237.210.82'
]

assetDecimals = {}
contractDecimals = {}

class tronAssetInfo():
    def __init__(self) -> None:
        self.raw_data:dict = None 
        self.TokenID:int = None 
        self.Precision:int = None 
        self.Description:int = None
        self.DateCreated:int = None  
        self.Abbr:str = None 
        self.Email:str = None
        self.Website:str = None 
        self.Github:str = None 
        self.URL:str = None 
        self.Name:str = None
        self.OwnerAddress:str = None 
        self.WhitePaper:str = None 
        self.TotalSupply:int = None 
        self.SocialMedia:list = None 
        self.GreyTag:str = None 
        self.RedTag:str = None 
        self.PublicTag:str = None 
        self.BlueTag:str = None 
    
    def __str__(self) -> str:
        m = f"tronAssetInfo("
        m += f"TokenID={self.TokenID} "
        m += f"Precision={self.Precision} "
        m += f"Description={self.Description} "
        m += f"DataCreated={self.DateCreated}) "
        m += f"Abbr={self.Abbr} "
        m += f"Email={self.Email} "
        m += f"Website={self.Website} "
        m += f"Github={self.Github} "
        m += f"URL={self.URL} "
        m += f"Name={self.Name} "
        m += f"OwnerAddress={self.OwnerAddress} "
        m += f"WhitePaper={self.WhitePaper} "
        m += f"TotalSupply={self.TotalSupply} "
        m += f"SocialMedia={self.SocialMedia} "
        m += f"GreyTag={self.GreyTag} "
        m += f"RedTag={self.RedTag} "
        m += f"PublicTag={self.PublicTag} "
        m += f"BlueTag={self.BlueTag}"
        m += ")"

        return m
    
    def __repr__(self) -> str:
        return self.__str__()

class TronAsset():
    def __init__(self, name:str) -> None:
        self.name = name 
    
    def Name(self) -> str:
        return self.name 
    
    def Info(self) -> tronAssetInfo:
        hresp = Http.Get("https://apilist.tronscanapi.com/api/token?id=%s&showAll=1" % str(self.name), timeoutRetryTimes=999)
        content = hresp.Content
        try:
            contentj = Json.Loads(content)
        except Exception as e:
            raise Exception("服务器返回的状态码为: " + str(hresp.StatusCode) + "\n\n服务器返回的数据为:\n\n" + content + "\n\n" + traceback.format_exc())

        tronassetinfo = tronAssetInfo()

        tronassetinfo.raw_data = contentj

        rd = None 
        for rr in contentj['data']:
            if str(self.name) == str(rr['tokenID']):
                rd = rr
                break 

        if rd == None:
            raise Exception(f"找不到trc10的info:{self.name}\n服务器返回的数据为:\n{content}")

        tronassetinfo.TokenID = rd['tokenID'] # asset_name 
        tronassetinfo.Precision = rd['precision']
        tronassetinfo.Description = rd['description']
        tronassetinfo.DateCreated = rd['dateCreated']
        tronassetinfo.Abbr = rd['abbr']
        tronassetinfo.Email = rd['email']
        tronassetinfo.Website = rd['website']
        tronassetinfo.Github = rd['github']
        tronassetinfo.URL = rd['url']
        tronassetinfo.Name = rd['name']
        tronassetinfo.OwnerAddress = rd['ownerAddress']
        tronassetinfo.WhitePaper = rd['white_paper']
        tronassetinfo.TotalSupply = rd['totalSupply']
        tronassetinfo.SocialMedia = rd['social_media']
        tronassetinfo.GreyTag = rd["greyTag"]
        tronassetinfo.RedTag = rd["redTag"]
        tronassetinfo.PublicTag = rd['publicTag']
        tronassetinfo.BlueTag = rd['blueTag']

        return tronassetinfo

# TLTPqeNi3DXgNdNiSYtx91nUK7PEk8siEx
class tronContractTokenInfo():
    def __init__(self) -> None:
        self.raw_data:dict = None 
        self.Address:str = None 
        self.Abbr:str = None 
        self.Name:str = None 
        self.Decimal:int = None  
        self.Type:str = None 
        self.IssuerAddr:str = None 
    
    def __str__(self) -> str:
        m = f"tronContractTokenInfo("
        m += f"Address={self.Address} "
        m += f"Abbr={self.Abbr} "
        m += f"Name={self.Name} "
        m += f"Decimal={self.Decimal} "
        m += f"Type={self.Type} "
        m += f"IssuerAddr={self.IssuerAddr}"
        m += ")"

        return m

    def __repr__(self) -> str:
        return self.__str__()

class tronContractInfo():
    def __init__(self) -> None:
        self.raw_data:dict = None 
        self.ContractAddress:str = None 
        self.ContractName:str = None 
        self.Symbol:str = None 
        self.Name:str = None 
        self.IssueAddress:str = None 
        self.IssueTime:int = None 
        self.Decimals:int = None 
        self.HomePage:str = None
        self.TokenDesc:str = None 
        self.Email:str = None 
        self.SocialMediaList:list = None 
        self.WhitePaper:str = None 
        self.GitHub:str = None 
        self.TotalSupplyWithDecimals:int = None 
        self.GreyTag:str = None 
        self.RedTag:str = None 
        self.PublicTag:str = None 
        self.BlueTag:str = None 
        self.TokenType:str = None 
        self.Reputation:str = None 
        # self.TokenInfo:tronContractTokenInfo = None 
    
    def __str__(self) -> str:
        m = "tronContractInfo("
        m += f"ContractAddress={self.ContractAddress} "
        m += f"ContractName={self.ContractName} "
        m += f"Symbol={self.Symbol} "
        m += f"Name={self.Name} "
        m += f"IssueAddress={self.IssueAddress} "
        m += f"IssueTime={self.IssueTime} "
        m += f"Decimals={self.Decimals} "
        m += f"HomePage={self.HomePage} "
        m += f"TokenDesc={self.TokenDesc} "
        m += f"Email={self.Email} "
        m += f"SocialMediaList={self.SocialMediaList} "
        m += f"WhitePaper={self.WhitePaper} "
        m += f"GitHub={self.GitHub} "
        m += f"TotalSupplyWithDecimals={self.TotalSupplyWithDecimals} "
        m += f"GreyTag={self.GreyTag} "
        m += f"RedTag={self.RedTag} "
        m += f"PublicTag={self.PublicTag} "
        m += f"BlueTag={self.BlueTag} "
        m += f"TokenType={self.TokenType} "
        m += f"Reputation={self.Reputation}"
        # m += f"TokenInfo={self.TokenInfo}"
        m += ")"

        return m
    
    def __repr__(self) -> str:
        return self.__str__()

class TronContract():
    def __init__(self, address:str) -> None:
        self.address = address 
        self.ReputationMap = {
            0: "Unknown",
            1: "Neutral",
            2: "OK",
            3: "Suspicious",
            4: "Unsafe"
        }
    
    def Address(self) -> str:
        return self.address 
    
    def Info(self) -> tronContractInfo:
        hresp = Http.Get("https://apilist.tronscanapi.com/api/token_trc20?contract=%s&showAll=1" % self.address, timeoutRetryTimes=999)
        content = hresp.Content
        try:
            contentj = Json.Loads(content)
        except Exception as e:
            raise Exception("服务器返回的状态码为: " + str(hresp.StatusCode) + "\n\n服务器返回的数据为:\n\n" + content + "\n\n" + traceback.format_exc())

        troncontractinfo = tronContractInfo()

        rd = None 
        for rd in contentj['trc20_tokens']:
            if self.address == rd['contract_address']:
                break 

        if rd != None:
            troncontractinfo.raw_data = [contentj]

            troncontractinfo.ContractAddress = rd['contract_address']
            troncontractinfo.ContractName = rd['contract_name']
            troncontractinfo.Symbol = rd['symbol']
            troncontractinfo.Name = rd['name']
            troncontractinfo.IssueAddress = rd['issue_address']
            troncontractinfo.IssueTime = Time.Strptime(rd['issue_time'])
            troncontractinfo.Decimals = rd['decimals']
            troncontractinfo.HomePage = rd['home_page']
            troncontractinfo.TokenDesc = rd['token_desc']
            troncontractinfo.Email = rd['email']
            troncontractinfo.SocialMediaList = rd['social_media_list']
            troncontractinfo.WhitePaper = rd['white_paper']
            troncontractinfo.GitHub = rd['git_hub']
            troncontractinfo.TotalSupplyWithDecimals = rd['total_supply_with_decimals'] 
            troncontractinfo.GreyTag = rd["greyTag"]
            troncontractinfo.RedTag = rd["redTag"]
            troncontractinfo.PublicTag = rd['publicTag']
            troncontractinfo.BlueTag = rd['blueTag']
            troncontractinfo.TokenType = rd['tokenType']

            content = Http.Get("https://apilist.tronscanapi.com/api/contract?contract=%s&type=contract" % self.address, timeoutRetryTimes=999).Content
            contentj = Json.Loads(content)

            troncontractinfo.raw_data.append(contentj)

            rd = None 
            for rr in contentj['data']:
                if self.address == rr['address']:
                    rd = rr
                    break 
            
            try:
                troncontractinfo.Reputation = self.ReputationMap[int(rd['tokenInfo']['tokenLevel'])]
            except:
                pass 

        else:
            content = Http.Get("https://apilist.tronscanapi.com/api/contract?contract=%s&type=contract" % self.address, timeoutRetryTimes=999).Content
            contentj = Json.Loads(content)

            rd = None 
            for rr in contentj['data']:
                if self.address == rr['address']:
                    rd = rr
                    break 
            
            if rd != None:
                troncontractinfo.raw_data = contentj

                # Lg.Trace(self.address)
                # Lg.Trace(rd)

                troncontractinfo.ContractAddress = rd['address']
                troncontractinfo.IssueTime = rd['date_created'] / 1000
                troncontractinfo.IssueAddress = rd['creator']['address']
                troncontractinfo.Name = rd['name']
                troncontractinfo.GreyTag = rd["greyTag"]
                troncontractinfo.RedTag = rd["redTag"]
                troncontractinfo.PublicTag = rd['publicTag']
                troncontractinfo.BlueTag = rd['blueTag']

                try:
                    troncontractinfo.Reputation = self.ReputationMap[int(rd['tokenInfo']['tokenLevel'])]
                except:
                    pass 
                
                # ti = tronContractTokenInfo()

                # if 'tokenInfo' in rd:
                #     tidi = rd['tokenInfo']
                #     ti.raw_data = tidi

                #     if 'tokenId' in tidi:
                #         ti.Address = tidi['tokenId']
                #     if 'tokenAbbr' in tidi:
                #         ti.Abbr = tidi['tokenAbbr']
                #     if 'tokenName' in tidi:
                #         ti.Name = tidi['tokenName']
                #     if 'tokenDecimal' in tidi:
                #         ti.Decimal = tidi['tokenDecimal']
                #     if 'tokenType' in tidi:
                #         ti.Type = tidi['tokenType']
                #     if 'issuerAddr' in tidi:
                #         ti.IssuerAddr = tidi['issuerAddr']
                
                # troncontractinfo.TokenInfo = ti
            else:
                raise Exception(f"找不到trc20的info:{self.address}\n服务器返回的数据为:\n{content}")

        return troncontractinfo
    
    def __str__(self) -> str:
        return f"TronContract(Address={self.address})"
    
    def __repr__(self) -> str:
        return self.__str__()

class tronTranscation():
    def __init__(self, trx:dict, tron:TronClient, block:tronBlock) -> None:
        # Lg.Trace()
        self.block:tronBlock = block
        self.tron:TronClient = tron
        self.raw_data:dict = trx

        self.contract:dict = trx["raw_data"]["contract"][0]
        
        self.ContractRet:str = trx['ret'][0]['contractRet']
        self.Asset:TronAsset = None 
        self.Contract:TronContract = None 
        self.Decimals:int = None 

        self.TxID:str = trx["txID"]
        self.Type:str = self.contract["type"]
        # Lg.Trace()

        self.Amount:int = None
        self.FromAddress:str = None 
        self.ToAddress:str = None 

        self.Expiration:int = None 
        if 'expiration' in trx["raw_data"]:
            self.Expiration = trx["raw_data"]["expiration"]
        
        self.Timestamp:int = None 
        if "timestamp" in trx["raw_data"]:
            self.Timestamp = trx["raw_data"]["timestamp"]

        if self.contract["type"] == "TransferContract":
            # Lg.Trace()
            self.Amount:int = None 
            if "amount" in self.contract["parameter"]["value"]:
                self.Amount = self.contract["parameter"]["value"]["amount"] / (10 ** 6)
            self.FromAddress:str = self.contract["parameter"]["value"]["owner_address"]
            self.ToAddress:str = self.contract["parameter"]["value"]["to_address"]

        elif self.contract["type"] == "TransferAssetContract":
            # Lg.Trace()
            self.Asset:TronAsset = TronAsset(self.contract["parameter"]["value"]["asset_name"])
            self.Amount:str = self.contract["parameter"]["value"]["amount"]
            self.FromAddress:str = self.contract["parameter"]["value"]["owner_address"]
            self.ToAddress:str = self.contract["parameter"]["value"]["to_address"]

            if not self.Asset.Name() in assetDecimals:
                # Lg.Trace()
                assetDecimals[self.Asset.Name()] = self.getAssetDecimals(self.Asset.Name())
            
            # Lg.Trace()
            # decimals = assetDecimals[self.AssetName]
            # if decimals != 0:
            #     # Lg.Trace()
            #     # txinfo["amount"] = txinfo["amount"] / (10 ** decimals)
            #     self.Decimals = 10 ** decimals
            self.Decimals:int = assetDecimals[self.Asset.Name()]

        elif self.contract["type"] == "TriggerSmartContract":
            # Lg.Trace()
            self.Contract:TronContract = TronContract(self.contract["parameter"]["value"]["contract_address"])

            if 'data' in self.contract["parameter"]["value"]:
                data = self.contract["parameter"]["value"]['data'] 

                # 这个交易的data只有8个字符的长度
                # b9fdb6cfc13845fce23da0762393482c145bbb8c2ac6094faf3a67ae3f389649
                # 'contractRet': 'REVERT'
                # 'data': 'a9059cbb',
                if len(data) != 8:
                    if data[:8] in [
                        "a9059cbb", # transfer 
                        "23b872dd", # transferFrom
                    ]:
                        if self.Contract.Address() not in contractDecimals:
                            try:
                                contractDecimals[self.Contract.Address()] = self.getContractDecimals(self.Contract.Address())
                            except Exception as e:
                                Lg.Warn(f"获取合约{self.Contract.Address()}精度失败:\n" + traceback.format_exc())
                                contractDecimals[self.Contract.Address()] = None 

                    # transfer
                    if data[:8] == "a9059cbb":
                        # Lg.Trace()
                        self.FromAddress:str = self.contract["parameter"]["value"]["owner_address"]
                        self.ToAddress:str = tronpy.keys.to_base58check_address('41' + (data[8:72])[-40:])
                        self.Amount:int = int(data[-64:], 16)

                        # if contractDecimals[self.ContractAddress] != None:
                        #     # Lg.Trace()
                        #     if contractDecimals[self.ContractAddress] <= 18:
                        #         self.Decimals = 10 ** contractDecimals[self.ContractAddress] 
                        #         # Lg.Trace()
                        self.Decimals:int = contractDecimals[self.Contract.Address()]

                    # transferFrom
                    elif data[:8] == "23b872dd":
                        self.FromAddress:str = tronpy.keys.to_base58check_address('41' + (data[8:72])[-40:])
                        self.ToAddress:str = tronpy.keys.to_base58check_address('41' + (data[72:136])[-40:])
                        self.Amount:int = int(data[-64:], 16) 

                        # if contractDecimals[self.ContractAddress] != None:
                        #     if contractDecimals[self.ContractAddress] <= 18:
                        #         self.Decimals = 10 ** contractDecimals[self.ContractAddress]
                        self.Decimals:int = contractDecimals[self.Contract.Address()]
        
    def __str__(self) -> str:
        m = "tronTranscation("
        m += f"TxID={self.TxID} "
        m += f"Type={self.Type} "
        m += f"ContractRet={self.ContractRet} "
        m += f"Asset={self.Asset} "
        m += f"Contract={self.Contract} "
        m += f"Decimals={self.Decimals} "
        m += f"Expiration={self.Expiration} "
        m += f"Timestamp={self.Timestamp} "
        m += f"Amount={self.Amount} "
        m += f"FromAddress={self.FromAddress} "
        m += f"ToAddress={self.ToAddress}"
        m += ")"

        return m
    
    def __repr__(self) -> str:
        return self.__str__()

    def getAssetDecimals(self, assetName:str) -> int:
        data = Http.PostJson(self.tron.nodeServer + "/wallet/getassetissuebyid", {'value': assetName, 'visible': True}, timeoutRetryTimes=999999).Content.replace('\n', '')
        if '"precision"' in data:

            res = []
            for i in data:
                if i in r'''1234567890qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM{}" :,''':
                    res.append(i)
            
            data = ''.join(res)

            # data = String(data).Filter(r'''1234567890qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM{}" :,''')
            try:
                c = Json.Loads(data)
                precision = c["precision"]
            except:
                precision = int(String(data).RegexFind('"precision": *([0-9]+)')[0][1])

            
            return precision
        else:
            return 0

    def getContractDecimals(self, contract:str) -> int:
        errcount = 0
        while True:
            try:
                contractobj = self.tron.tron.get_contract(contract)
                if hasattr(contractobj.functions, 'decimals'):
                    return contractobj.functions.decimals()
                else:
                    return self.getContractDecimalsFromWeb(contract)
            except ValueError as e:
                if 'can not call a contract without ABI' in str(e):
                    while True:
                        try:
                            return self.getContractDecimalsFromWeb(contract)
                        except Exception as e:
                            errcount += 1
                            if errcount > 5:
                                raise e
                else:
                    raise e
            except Exception as e:
                errcount += 1
                if errcount > 5:
                    raise e
    
    def getContractDecimalsFromWeb(self, contract:str) -> int:
        # Lg.Trace("从web获取精度")
        content = Http.Get("https://apilist.tronscanapi.com/api/token_trc20?contract=%s&showAll=1" % contract, timeoutRetryTimes=999).Content
        contentj = Json.Loads(content)
        if contentj['total'] == 0:
            return None  
        
        rd = None 
        for rd in contentj['trc20_tokens']:
            if contract == rd['contract_address']:
                break 
        if rd == None:
            return None  
        
        return int(rd['decimals'])

class tronBlock():
    def __init__(self, block:dict, tron:TronClient) -> None:
        self.tron:TronClient = tron
        # Lg.Trace()

        self.raw_data:dict = block 
        self.BlockID:str = block['blockID']
        self.TxTrieRoot:str = block['block_header']['raw_data']['txTrieRoot']
        self.WitnessAddress:str = block['block_header']['raw_data']['witness_address']
        self.ParentHash:str = block['block_header']['raw_data']['parentHash']

        # Lg.Trace()

        self.Number:int = None 
        if 'number' in block['block_header']['raw_data']:
            self.Number = block['block_header']['raw_data']['number']

        self.Timestamp:int = None
        if 'timestamp' in block['block_header']['raw_data']:
            self.Timestamp = block['block_header']['raw_data']['timestamp']
        
        self.WitnessSignature:str = None 
        if 'witness_signature' in block['block_header']['raw_data']:
            self.WitnessSignature = block['block_header']['witness_signature']
        
        # Lg.Trace()
    
    def __str__(self) -> str:
        m = "tronBlock("
        m += f"BlockID={self.BlockID} "
        m += f"TxTrieRoot={self.TxTrieRoot} "
        m += f"WitnessAddress={self.WitnessAddress} "
        m += f"ParentHash={self.ParentHash} "
        m += f"Number={self.Number} "
        m += f"Timestamp={self.Timestamp} "
        m += f"WitnessSignature={self.WitnessSignature}"
        m += ")"

        return m
    
    def __repr__(self) -> str:
        return self.__str__()

    def Transcations(self) -> list[tronTranscation]:
        """
        返回block里面的transcation的列表.
        不会解析所有的transcation, 只会解析一部分交易相关的. 
        具体会解析哪些, 还需要看看源码. 
        """
        # Lg.Trace(self.raw_data)
        trxs = []
        if "transactions" not in self.raw_data:
            return trxs 

        for trx in self.raw_data["transactions"]:
            txid = trx["txID"]
            contract = trx["raw_data"]["contract"][0]

            if contract["type"] not in [
                "TransferContract", 
                "TransferAssetContract", 
                "TriggerSmartContract"
            ]:
                continue
            try:
                trxs.append(tronTranscation(trx, self.tron, self))
            except Exception as e:
                Lg.Warn(f"处理block'{self.BlockID}'的tx'{txid}'出错:\n" + traceback.format_exc())
                pass 

        return trxs 

class TronClient():
    def __init__(self, fullNodeServer:str=None) -> None:
        if fullNodeServer != None:
            self.nodeServer:str = fullNodeServer
            self.tron = TronAPI(HTTPProvider(self.nodeServer))
        else:
            while True:
                try:
                    self.nodeServer:str = 'http://' + Random.Choice(tronOfficialNodes) + ":8090"
                    self.tron = TronAPI(HTTPProvider(self.nodeServer))
                    self.tron.get_latest_block()
                    break 
                except:
                    pass 
    
    def Block(self, blockNumber:int=None) -> tronBlock:
        if blockNumber == None:
            block = self.tron.get_latest_block()
        else:
            block = self.tron.get_block(blockNumber)
        # Lg.Trace(block)
        return tronBlock(block, self)

# class Tron:
#     TronClient
#     TronContract
#     TronAsset

if __name__ == "__main__":
    # tttt = TronClient("http://13.124.62.58:8090")
    # bdf = tttt.Block(48311298)
    # Lg.Trace(bdf)
    # txs = bdf.Transcations()
    # for tx in txs:
    #     if tx.TxID == '8e055811c777cd0cf5ec2b74f79a2cb4f1aaf143011e9afe468760d654f86465':
    #         Lg.Trace(tx)
    #         if tx.Asset != None:
    #             Lg.Trace(tx.Asset)
    #             Lg.Trace(tx.Asset.Info())
    #         if tx.Contract != None:
    #             Lg.Trace(tx.Contract)
    #             Lg.Trace(tx.Contract.Info())
    #         # ipdb.set_trace()

    t = TronContract("TS6dob4Cbrfvi1oSxm5WrbyZZQLCqgFjHV")
    Lg.Trace(t.Info())
