#! /usr/bin/env python

"""
Registry class that stores the state of the game.  A save game feature could be
implemented by serializing this class.
"""
class Registry:
    
    def __init__(self, mapName, playerPosition, playerLevel, spriteMetadata = {},
                 coinCount = 0, keyCount = 0, checkpoint = None):
        self.mapName = mapName
        self.playerPosition = playerPosition
        self.playerLevel = playerLevel
        # a map of sprite metadata keyed on uid 
        self.spriteMetadata = spriteMetadata
        self.coinCount = coinCount
        self.keyCount = keyCount
        # metadata for the last checkpoint reached
        self.checkpoint = checkpoint
        # registry snapshot
        self.snapshot = None

    def registerMetadata(self, spriteMetadata):
        self.spriteMetadata[spriteMetadata.uid] = spriteMetadata
        
    def getMetadata(self, uid):
        if self.checkpoint and self.checkpoint.uid == uid:
            return self.checkpoint
        if uid in self.spriteMetadata:
            return self.spriteMetadata[uid]
        return None
    
    def copyMetadata(self):
        return dict((uid, self.spriteMetadata[uid]) for uid in self.spriteMetadata)
            
    def takeSnapshot(self):
        self.snapshot = Registry(self.mapName,
                                 self.playerPosition,
                                 self.playerLevel,
                                 self.copyMetadata(),
                                 self.coinCount,
                                 self.keyCount,
                                 self.checkpoint)
                
    # ==========================================================================
         
    def coinCollected(self, coinCollectedEvent):
        self.registerMetadata(coinCollectedEvent.getMetadata())
        self.coinCount += 1
        
    def keyCollected(self, keyCollectedEvent):
        self.registerMetadata(keyCollectedEvent.getMetadata())
        self.keyCount += 1
        
    def doorOpened(self, doorOpenedEvent):
        self.registerMetadata(doorOpenedEvent.getMetadata())
        
    def checkpointReached(self, checkpointReachedEvent):
        checkpoint = checkpointReachedEvent.getMetadata()
        print "checkpoint reached: %s" % checkpoint.uid
        self.snapshot = Registry(checkpoint.mapName,
                                 checkpoint.tilePosition,
                                 checkpoint.level,
                                 self.copyMetadata(),
                                 self.coinCount,
                                 self.keyCount,
                                 checkpoint)
        