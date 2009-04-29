#! /usr/bin/env python

gameInfo = {}

def registerInfo(info):
    gameInfo[info.uid] = info

def getInfo(uid):
    if uid in gameInfo:
        return gameInfo[uid]
    return None

class Info:
    def __init__(self, uid):
        self.uid = uid
    
class CoinInfo(Info):
    def __init__(self, name):
        Info.__init__(self, name)
        self.available = True
        
registerInfo(CoinInfo("start"))
registerInfo(CoinInfo("bridge1"))
registerInfo(CoinInfo("bridge2"))
