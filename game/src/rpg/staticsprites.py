#!/usr/bin/env python

from sprites import *

from spritemetadata import KeyMetadata, CoinMetadata, DoorMetadata
from spriteframes import StaticFrames

"""
Defines a sprite that doesn't move independently, although (unlike FixedSprite)
it does move with the view.
"""
class StaticSprite(RpgSprite):
    
    def __init__(self, uid, registry, spriteFrames, position = (0, 0)):
        RpgSprite.__init__(self, uid, registry, spriteFrames, position)

    def update(self, viewRect, gameSprites, visibleSprites, increment):
        if self.toRemove:
            self.remove(gameSprites)
        elif self.mapRect.colliderect(viewRect):
            # some part of this sprite is in the current view
            self.image = self.spriteFrames.advanceFrame(increment)
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
            
    """def advanceFrame(self, increment):
        if increment:
            self.frameCount = (self.frameCount + increment) % self.frameSkip
            if self.frameCount == 0:
                self.animFrameCount = (self.animFrameCount + 1) % self.numFrames       
                self.image = self.animationFrames[self.animFrameCount]"""
            
class Flames(StaticSprite):
    
    framesImage = None
    
    def __init__(self, uid, rpgMap, registry):
        if Flames.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "flame-frames.png")
            Flames.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Flames.framesImage)
        spriteFrames = StaticFrames(animationFrames, 6)
        StaticSprite.__init__(self, uid, registry, spriteFrames, (4, 2))

class Coin(StaticSprite):
    
    baseRectWidth = 8 * SCALAR    
    framesImage = None
    
    def __init__(self, uid, rpgMap, registry):
        if Coin.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "coin-frames.png")
            Coin.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Coin.framesImage)
        spriteFrames = StaticFrames(animationFrames, 6)
        StaticSprite.__init__(self, uid, registry, spriteFrames, (2, 2))
        
    def processCollision(self, player):
        metadata = CoinMetadata(self.uid)
        self.registry.registerMetadata(metadata)
        player.incrementCoinCount()
        self.toRemove = True

class Key(StaticSprite):
    
    baseRectWidth = 8 * SCALAR    
    framesImage = None
    
    def __init__(self, uid, rpgMap, registry):
        if Key.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "key-frames.png")
            Key.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Key.framesImage, 6)
        spriteFrames = StaticFrames(animationFrames, 6)
        StaticSprite.__init__(self, uid, registry, spriteFrames, (2, 2))
        
    def processCollision(self, player):
        metadata = KeyMetadata(self.uid)
        self.registry.registerMetadata(metadata)
        player.incrementKeyCount()
        self.toRemove = True

class Door(StaticSprite):
    
    baseRectWidth = 4 * SCALAR    
    framesImage = None
    
    def __init__(self, uid, rpgMap, registry):
        if Door.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "door-frames.png")
            Door.framesImage = view.loadScaledImage(imagePath, None)
        additionalFrames = view.processStaticFrames(Door.framesImage, 8)        
        self.additionalFrames = view.copyStaticFrames(additionalFrames)
        animationFrames = [additionalFrames[0]]
        spriteFrames = StaticFrames(animationFrames, 6)
        StaticSprite.__init__(self, uid, registry, spriteFrames, (0, 0))
        self.rpgMap = rpgMap
        self.opening = False
        
    # override
    def advanceFrame(self, increment):
        if increment and self.opening:
            self.frameCount = (self.frameCount + increment) % self.frameSkip
            if self.frameCount == 0:
                self.animFrameCount = (self.animFrameCount + 1) % 8       
                if self.animFrameCount == 0:
                    self.opened()
                else:
                    self.image = self.additionalFrames[self.animFrameCount]
    
    def opened(self):
        metadata = DoorMetadata(self.uid, self.x, self.y, self.level)
        metadata.applyMapActions(self.rpgMap)
        self.registry.registerMetadata(metadata)
        self.toRemove = True
        
    def processAction(self, player):
        if player.getKeyCount() > 0 and not self.opening:
            player.incrementKeyCount(-1)
            self.opening = True
