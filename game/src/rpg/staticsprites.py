#!/usr/bin/env python

from sprites import *

from spritemetadata import KeyMetadata, CoinMetadata, DoorMetadata
from spriteframes import StaticFrames

class Flames(OtherSprite):
    
    framesImage = None
    
    def __init__(self, rpgMap):
        if Flames.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "flame-frames.png")
            Flames.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Flames.framesImage)
        spriteFrames = StaticFrames(animationFrames, 6)
        OtherSprite.__init__(self, rpgMap, spriteFrames, (4, 2))

class Coin(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (8 * SCALAR, BASE_RECT_HEIGHT)
        
    def __init__(self, rpgMap):
        if Coin.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "coin-frames.png")
            Coin.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Coin.framesImage)
        spriteFrames = StaticFrames(animationFrames, 6)
        OtherSprite.__init__(self, rpgMap, spriteFrames, (2, 2))
        
    def processCollision(self, player):
        metadata = CoinMetadata(self.uid)
        self.registry.registerMetadata(metadata)
        player.incrementCoinCount()
        self.toRemove = True

class Key(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (8 * SCALAR, BASE_RECT_HEIGHT)
        
    def __init__(self, rpgMap):
        if Key.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "key-frames.png")
            Key.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Key.framesImage, 6)
        spriteFrames = StaticFrames(animationFrames, 6)
        OtherSprite.__init__(self, rpgMap, spriteFrames, (2, 2))
        
    def processCollision(self, player):
        metadata = KeyMetadata(self.uid)
        self.registry.registerMetadata(metadata)
        player.incrementKeyCount()
        self.toRemove = True

class Door(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (4 * SCALAR, BASE_RECT_HEIGHT)    

    def __init__(self, rpgMap):
        if Door.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "door-frames.png")
            Door.framesImage = view.loadScaledImage(imagePath, None)
        animationFrames = view.processStaticFrames(Door.framesImage, 8)
        spriteFrames = StaticFrames(animationFrames, 6)
        OtherSprite.__init__(self, rpgMap, spriteFrames)
        self.opening = False
        self.frameCount = 0
        self.frameIndex = 0
        
    # override
    def advanceFrame(self, increment):
        if increment and self.opening:
            self.frameCount = (self.frameCount + increment) % self.spriteFrames.frameSkip
            if self.frameCount == 0:
                self.frameIndex += 1       
                if self.frameIndex == self.spriteFrames.numFrames:
                    self.opened()
                else:
                    self.image = self.spriteFrames.animationFrames[self.frameIndex]
    
    def opened(self):
        metadata = DoorMetadata(self.uid, self.x, self.y, self.level)
        metadata.applyMapActions(self.rpgMap)
        self.registry.registerMetadata(metadata)
        self.toRemove = True
        
    def processAction(self, player):
        if player.getKeyCount() > 0 and not self.opening:
            player.incrementKeyCount(-1)
            self.opening = True
