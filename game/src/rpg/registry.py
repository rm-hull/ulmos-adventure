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
    
class FlamesInfo(Info):
    def __init__(self, name):
        Info.__init__(self, name)
        self.goneOut = False

class CoinInfo(Info):
    def __init__(self, name):
        Info.__init__(self, name)
        self.collected = False

class KeyInfo(Info):
    def __init__(self, name):
        Info.__init__(self, name)
        self.collected = False
        
class DoorInfo(Info):
    def __init__(self, name):
        Info.__init__(self, name)
        self.open = False
        