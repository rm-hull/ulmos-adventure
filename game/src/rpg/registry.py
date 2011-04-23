#! /usr/bin/env python

"""
Registry class that stores the state of the game.  A save game feature could be
implemented by serializing this class.
"""
class Registry:
    
    def __init__(self):
        # a map of sprite metadata keyed on uid 
        self.spriteMetadata = {}
        self.coinCount = 0;
        self.keyCount = 0;

    def registerMetadata(self, spriteMetadata):
        self.spriteMetadata[spriteMetadata.uid] = spriteMetadata
        
    def getMetadata(self, uid):
        if uid in self.spriteMetadata:
            return self.spriteMetadata[uid]
        return None
    
    def incrementCoinCount(self, n = 1):
        self.coinCount += n

    def incrementKeyCount(self, n = 1):
        self.keyCount += n
