#! /usr/bin/env python

class SpriteInfo:
    
    def __init__(self, uid):
        self.uid = uid
    
    # placeholder method    
    def isInactive(self):
        return False
    
    # placeholder method
    def applyMapActions(self, rpgMap):
        pass
    
class FlamesInfo(SpriteInfo):

    def __init__(self, uid):
        SpriteInfo.__init__(self, uid)

class CoinInfo(SpriteInfo):
    
    def __init__(self, uid, collected = True):
        SpriteInfo.__init__(self, uid)
        self.collected = collected

    def isInactive(self):
        return self.collected
        
class KeyInfo(SpriteInfo):

    def __init__(self, uid, collected = True):
        SpriteInfo.__init__(self, uid)
        self.collected = collected
        
    def isInactive(self):
        return self.collected

class DoorInfo(SpriteInfo):
    
    def __init__(self, uid, x, y, level, open = True):
        SpriteInfo.__init__(self, uid)
        self.x = x
        self.y = y
        self.level = level
        self.open = open

    def isInactive(self):
        return self.open
    
    def applyMapActions(self, rpgMap):
        rpgMap.addLevel(self.x, self.y + 1, self.level)
