#print("load " + __file__.split('/')[-1])

def UUID() -> str:
    import shortuuid
    return shortuuid.uuid()

def UUID_Full() -> str:
    import uuid 
    return str(uuid.uuid4())