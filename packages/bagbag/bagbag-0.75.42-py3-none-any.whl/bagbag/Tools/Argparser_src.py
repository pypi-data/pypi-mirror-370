from __future__ import annotations

#print("load " + '/'.join(__file__.split('/')[-2:]))

import argparse

class Argparser():
    def __init__(self, description:str=None) -> None:
        self.parser = argparse.ArgumentParser(description=description)

    def Add(self, arg:str, help:str=None) -> Argparser:
        return self.AddString(arg, help)
    
    def AddOpt(self, arg:str, default:str=None, help:str=None) -> Argparser:
        return self.AddOptString(arg, default, help)
    
    def AddStr(self, arg:str, help:str=None) -> Argparser:
        return self.AddString(arg, help)
    
    def AddOptStr(self, arg:str, default:str=None, help:str=None) -> Argparser:
        return self.AddOptString("--" + arg, default, help)
    
    def AddString(self, arg:str, help:str=None) -> Argparser:
        self.parser.add_argument(arg, help=help, type=str)
        return self
    
    def AddOptString(self, arg:str, default:str=None, help:str=None) -> Argparser:
        self.parser.add_argument("--" + arg, default=default, help=help, type=str)
        return self

    def AddOptBool(self, arg:str, default:bool=False, help:str=None) -> Argparser:
        self.parser.add_argument("--" + arg, default=default, help=help, action='store_true')
        return self
    
    def AddInt(self, arg:str, help:str=None) -> Argparser:
        self.parser.add_argument(arg, help=help, type=int)
        return self
    
    def AddOptInt(self, arg:str, default:int=None, help:str=None) -> Argparser:
        self.parser.add_argument("--" + arg, default=default, help=help, type=int)
        return self
    
    def AddFloat(self, arg:str, help:str=None) -> Argparser:
        self.parser.add_argument(arg, help=help, type=float)
        return self
    
    def AddOptFloat(self, arg:str, default:float=None, help:str=None) -> Argparser:
        self.parser.add_argument("--" + arg, default=default, help=help, type=float)
        return self
    
    def Get(self):
        return self.parser.parse_args()

if __name__ == "__main__":
    args = (
        Argparser().
        AddOptBool("arg1").
        AddString("arg2"). 
        Add("arg3", "help string 3"). 
        AddOpt("optionArgs4"). 
        AddOpt("optionArgs5", "defaultValue5").
        AddOpt("optionArgs6", "defaultValue6", "help string 6"). 
        AddInt("intKey"). 
        AddOptFloat("floatKey").
        Get()
    )
    print(args.arg3)
    print(args.floatKey)
    print(args)
