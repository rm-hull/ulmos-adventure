#! /usr/bin/env python

import staticsprites

gameInfo = {}

def registerInfo(info):
    gameInfo[info.uid] = info

def getInfo(uid):
    if uid in gameInfo:
        return gameInfo[uid]
    return None

class SpriteInfo:
    
    def __init__(self, uid):
        self.uid = uid
        
    def isInactive(self):
        return False
    
class FlamesInfo(SpriteInfo):

    def __init__(self, name):
        SpriteInfo.__init__(self, name)
        
    def getSprite(self):
        return staticsprites.Flames(self)

class CoinInfo(SpriteInfo):
    
    def __init__(self, name):
        SpriteInfo.__init__(self, name)
        self.collected = False

    def isInactive(self):
        return self.collected

    def getSprite(self):
        return staticsprites.Coin(self)
        
class KeyInfo(SpriteInfo):

    def __init__(self, name):
        SpriteInfo.__init__(self, name)
        self.collected = False
        
    def isInactive(self):
        return self.collected

    def getSprite(self):
        return staticsprites.Key(self)

class DoorInfo(SpriteInfo):
    
    def __init__(self, name):
        SpriteInfo.__init__(self, name)
        self.open = False

    def isInactive(self):
        return self.open

    def getSprite(self, rpgMap):
        return staticsprites.Door(self, rpgMap)
        