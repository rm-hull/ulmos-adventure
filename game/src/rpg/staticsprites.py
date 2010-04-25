#!/usr/bin/env python

from sprites import *

import registry

"""
Defines a sprite that doesn't move independently, although (unlike FixedSprite)
it does move with the view.
"""
class StaticSprite(RpgSprite):
    
    def __init__(self, animationFrames, frameSkip, position = (0, 0)):
        RpgSprite.__init__(self, frameSkip, position)
        # animation frames
        self.animationFrames = animationFrames     
        self.numFrames = len(animationFrames)
        # additional animation properties
        self.image = animationFrames[self.animFrameCount]

    def update(self, viewRect, gameSprites, visibleSprites, increment):
        if self.toRemove:
            self.remove(gameSprites)
        elif self.mapRect.colliderect(viewRect):
            # some part of this sprite is in the current view
            self.advanceFrame(increment)
            # make self.rect relative to the view
            self.rect.topleft = (self.mapRect.left - viewRect.left,
                                 self.mapRect.top - viewRect.top)
            if not self.active:
                self.active = True
                self.add(visibleSprites)
            return
        if self.active:
            self.active = False
            self.remove(visibleSprites)
            
    def advanceFrame(self, increment):
        if increment:
            self.frameCount += increment
            if (self.frameCount % self.frameSkip == 0):
                self.animFrameCount = (self.animFrameCount + 1) % self.numFrames       
                self.image = self.animationFrames[self.animFrameCount]
            
class Flames(StaticSprite):
    
    framesImage = None
    
    def __init__(self, flamesInfo):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "flame-frames.png")
            self.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(self.framesImage)
        StaticSprite.__init__(self, animationFrames, 6, (4, 2))
        self.flamesInfo = flamesInfo

class Coin(StaticSprite):
    
    baseRectWidth = 8 * SCALAR    
    framesImage = None
    
    def __init__(self, coinInfo):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "coin-frames.png")
            self.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(self.framesImage)
        StaticSprite.__init__(self, animationFrames, 6, (2, 2))
        self.coinInfo = coinInfo
        
    def processCollision(self, player):
        self.coinInfo.collected = True
        player.incrementCoinCount()
        self.toRemove = True

class Key(StaticSprite):
    
    baseRectWidth = 8 * SCALAR    
    framesImage = None
    
    def __init__(self, keyInfo):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "key-frames.png")
            self.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(self.framesImage, 6)
        StaticSprite.__init__(self, animationFrames, 6, (2, 2))
        self.keyInfo = keyInfo
        
    def processCollision(self, player):
        self.keyInfo.collected = True
        player.incrementKeyCount()
        self.toRemove = True

class Door(StaticSprite):
    
    baseRectWidth = 4 * SCALAR    
    framesImage = None
    
    def __init__(self, rpgMap, doorInfo):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "door-frames.png")
            self.framesImage = view.loadScaledImage(imagePath, None)        
        self.additionalFrames = view.processStaticFrames(self.framesImage, 8)
        animationFrames = [self.additionalFrames[0]]
        StaticSprite.__init__(self, animationFrames, 6, (0, 0))
        self.rpgMap = rpgMap
        self.opening = False
        self.doorInfo = doorInfo
               
    # override
    def setPosition(self, x, y, level):
        self.x, self.y = x, y
        self.resetPosition(x * view.TILE_SIZE + self.position[0],
                           y * view.TILE_SIZE + self.position[1],
                           level)
        
    # override
    def advanceFrame(self, increment):
        if increment and self.opening:
            self.frameCount += increment
            if (self.frameCount % self.frameSkip == 0):
                self.animFrameCount = (self.animFrameCount + 1) % 8       
                if (self.animFrameCount == 0):
                    self.opened()
                else:
                    self.image = self.additionalFrames[self.animFrameCount]
    
    def opened(self):
        self.toRemove = True
        self.doorInfo.open = True
        # make the corresponding tile available for this level
        self.rpgMap.addLevel(self.x, self.y + 1, self.level)
        
    def processAction(self, player):
        if player.keyCount.count > 0:
            player.keyCount.incrementCount(-1)
            self.opening = True
