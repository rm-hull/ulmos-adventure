#! /usr/bin/env python

class Registry:
    
    def __init__(self):
        # a map of sprite metadata keyed on uid 
        self.spriteMetadata = {}
        # self.coinCount = 0;
        # self.keyCount = 0;

    def registerMetadata(self, spriteMetadata):
        self.spriteMetadata[spriteMetadata.uid] = spriteMetadata
        
    def getMetadata(self, uid):
        if uid in self.spriteMetadata:
            return self.spriteMetadata[uid]
        return None
