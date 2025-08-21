import web3

#print("load " + '/'.join(__file__.split('/')[-2:]))

class EthereumClient():
    def __init__(self, nodeServer:str=None) -> None:
        w3 = web3.Web3(web3.Web3.HTTPProvider("https://llamanodes.com"))
        b = w3.eth.get_block('latest')
        print(b)

if __name__ == "__main__":
    e = EthereumClient()
