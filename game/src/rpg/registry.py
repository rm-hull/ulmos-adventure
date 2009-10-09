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

class KeyInfo(Info):
    def __init__(self, name):
        Info.__init__(self, name)
        self.available = True
        
class DoorInfo(Info):
    def __init__(self, name):
        Info.__init__(self, name)
        self.closed = True
        
registerInfo(CoinInfo("start.coin.1"))
registerInfo(CoinInfo("start.coin.2"))
# registerInfo(CoinInfo("start.coin.3"))
registerInfo(CoinInfo("start.key.1"))
registerInfo(DoorInfo("start.door"))

registerInfo(KeyInfo("east.key"))