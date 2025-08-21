from packaging import version

def VersionCompare(version1:str, operator:str, version2:str) -> bool:
    v1 = version.parse(version1)
    v2 = version.parse(version2)
    o = operator

    if o == ">":
        return v1 > v2 
    elif o == ">=":
        return v1 >= v2 
    elif o == "=" or o == "==":
        return v1 == v2
    elif o == "<":
        return v1 < v2 
    elif o == "<=":
        return v1 <= v2 
    else:
        raise Exception(f'Unsupport operator: {o}, must be on of >, >=, =, ==, <, <=')