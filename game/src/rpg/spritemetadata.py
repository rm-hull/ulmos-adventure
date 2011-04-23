#! /usr/bin/env python

class SpriteMetadata:
    
    def __init__(self, uid):
        self.uid = uid
    
    # placeholder method    
    def isRemovedFromMap(self):
        return False
    
    # placeholder method
    def applyMapActions(self, rpgMap):
        pass
    
class FlamesMetadata(SpriteMetadata):

    def __init__(self, uid):
        SpriteMetadata.__init__(self, uid)

class CoinMetadata(SpriteMetadata):
    
    def __init__(self, uid, collected = True):
        SpriteMetadata.__init__(self, uid)
        self.collected = collected

    def isRemovedFromMap(self):
        return self.collected
        
class KeyMetadata(SpriteMetadata):

    def __init__(self, uid, collected = True):
        SpriteMetadata.__init__(self, uid)
        self.collected = collected
        
    def isRemovedFromMap(self):
        return self.collected

class DoorMetadata(SpriteMetadata):
    
    def __init__(self, uid, x, y, level, open = True):
        SpriteMetadata.__init__(self, uid)
        self.x, self.y = x, y
        self.level = level
        self.open = open

    def isRemovedFromMap(self):
        return self.open
    
    # makes the corresponding tile available for this level
    def applyMapActions(self, rpgMap):
        rpgMap.addLevel(self.x, self.y + 1, self.level)
