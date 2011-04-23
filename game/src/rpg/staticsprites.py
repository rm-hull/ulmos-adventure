#!/usr/bin/env python

from sprites import *

from rpg.spritemetadata import KeyMetadata, CoinMetadata, DoorMetadata

"""
Defines a sprite that doesn't move independently, although (unlike FixedSprite)
it does move with the view.
"""
class StaticSprite(RpgSprite):
    
    def __init__(self, uid, registry, animationFrames, frameSkip, position = (0, 0)):
        RpgSprite.__init__(self, uid, registry, frameSkip, position)
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
    
    def __init__(self, uid, rpgMap, registry):
        if Flames.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "flame-frames.png")
            Flames.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Flames.framesImage)
        StaticSprite.__init__(self, uid, registry, animationFrames, 6, (4, 2))

class Coin(StaticSprite):
    
    baseRectWidth = 8 * SCALAR    
    framesImage = None
    
    def __init__(self, uid, rpgMap, registry):
        if Coin.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "coin-frames.png")
            Coin.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Coin.framesImage)
        StaticSprite.__init__(self, uid, registry, animationFrames, 6, (2, 2))
        
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
        StaticSprite.__init__(self, uid, registry, animationFrames, 6, (2, 2))
        
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
        self.additionalFrames = view.processStaticFrames(Door.framesImage, 8)
        animationFrames = [self.additionalFrames[0]]
        StaticSprite.__init__(self, uid, registry, animationFrames, 6, (0, 0))
        self.rpgMap = rpgMap
        self.opening = False
        
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
        metadata = DoorMetadata(self.uid, self.x, self.y, self.level)
        metadata.applyMapActions(self.rpgMap)
        self.registry.registerMetadata(metadata)
        self.toRemove = True
        
    def processAction(self, player):
        if player.getKeyCount() > 0 and not self.opening:
            player.incrementKeyCount(-1)
            self.opening = True
