from .whois import whois 
from .. import Time

def DomainWhois(domain:str, retryTimes:int=3, useCommand:bool=False) -> dict | None:
        for _ in range(retryTimes):
            try:
                if useCommand:
                    data = whois(domain, command=True, executable='whois')
                else:
                    data = whois(domain)
                
                datadict = dict(data)
                datadict['raw_data'] = data.text

                return datadict
            except Exception as e:
                pass 
        
        return None

    # whois(domain, command=True, executable='whois') # 使用系统的命令行客户端

def IPWhois(ip:str, ignore_referral_errors:bool=True) -> dict | None:
    """
    The function `IPWhois` takes an IP address as input and returns WHOIS information for that IP
    address.
    
    :param ip: The `IPWhois` function takes two parameters:
    :type ip: str
    :param ignore_referral_errors: The `ignore_referral_errors` parameter in the `IPWhois` function is a
    boolean parameter that determines whether referral errors should be ignored during the WHOIS lookup
    process, defaults to True
    :type ignore_referral_errors: bool (optional)
    :return: The function `IPWhois` is returning a dictionary or `None` depending on the result of the
    IPWhois lookup operation.
    """
    import ipwhois 
    obj = ipwhois.IPWhois(ip)
    # http 
    # result = obj.lookup_rdap(
    #     depth=10, 
    #     inc_raw=True,
    #     nir_field_list=None, 
    #     asn_methods=None,
    # )
    while True:
        try:
            result = obj.lookup_whois(
                inc_raw=True, 
                ignore_referral_errors=ignore_referral_errors,
            )
            break 
        except ipwhois.exceptions.WhoisRateLimitError:
            Time.Sleep(5, bar=False)

    return result