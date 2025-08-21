import time 

#print("load " + '/'.join(__file__.split('/')[-2:]))

pformat = (lambda a:lambda v,t="    ",n="\n",i=0:a(a,v,t,n,i))(lambda f,v,t,n,i:"{%s%s%s}"%(",".join(["%s%s%s: %s"%(n,t*(i+1),repr(k),f(f,v[k],t,n,i+1))for k in v]),n,(t*i)) if type(v)in[dict] else (type(v)in[list]and"[%s%s%s]"or"(%s%s%s)")%(",".join(["%s%s%s"%(n,t*(i+1),f(f,k,t,n,i+1))for k in v]),n,(t*i)) if type(v)in[list,tuple] else repr(v))

def Size(ByteNumber, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(ByteNumber) < 1024.0:
            return "%3.1f%s%s" % (ByteNumber, unit, suffix)
        ByteNumber /= 1024.0
    return "%.1f%s%s" % (ByteNumber, 'Y', suffix)

def TimeDuration(seconds:int) -> str:
    return time.strftime("%H:%M:%S", time.gmtime(seconds))

def PrettyJson(obj:dict|list) -> str:
    return pformat(obj)