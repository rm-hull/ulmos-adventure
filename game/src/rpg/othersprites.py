#!/usr/bin/env python

from sprites import *
from spritemovement import NoMovementStrategy, RobotMovementStrategy
from spriteframes import StaticFrames
from rpg.spritemetadata import KeyMetadata, CoinMetadata

"""
Defines a sprite that doesn't move independently, although (unlike FixedSprite)
it does move with the view.
"""
class OtherSprite(MaskSprite):
    
    def __init__(self, uid, registry, rpgMap, spriteFrames, position = (0, 0)):
        MaskSprite.__init__(self, uid, registry, rpgMap, spriteFrames, position)
    
    def setMovement(self, tilePoints, level):
        if len(tilePoints) == 1:
            self.movement = NoMovementStrategy()
        else:
            self.movement = RobotMovementStrategy(tilePoints, self.position)
        # use the first tile point to set the position
        x, y = tilePoints[0][0], tilePoints[0][1]    
        self.setPosition(x, y, level)
    
    def update(self, viewRect, gameSprites, visibleSprites, increment):
        if self.toRemove:
            self.remove(gameSprites)
        else:
            self.image = self.spriteFrames.advanceFrame(increment)
            px, py = self.movement.getMovement(self.mapRect.topleft)            
            self.doMove(px, py)
            # make self.rect relative to the view
            self.rect.topleft = (self.mapRect.left - viewRect.left,
                                 self.mapRect.top - viewRect.top)
            if self.mapRect.colliderect(viewRect):
                if not self.active:
                    self.active = True
                    self.add(visibleSprites)
                return
        if self.active:
            self.active = False
            self.remove(visibleSprites)
            
    # overidden  
    def repairImage(self):
        self.spriteFrames.repairLastFrame()
            
class Baddie(OtherSprite):
    
    framesImage = None
    
    def __init__(self, uid, rpgMap, registry):
        if Baddie.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "flame-frames.png")
            Baddie.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Baddie.framesImage)
        spriteFrames = StaticFrames(animationFrames, 6)
        OtherSprite.__init__(self, uid, registry, rpgMap, spriteFrames, (4, 2))
        self.rpgMap = rpgMap

    def processCollision(self, player):
        print "life lost!"
        return True

class MyFlames(OtherSprite):
    
    framesImage = None
    
    def __init__(self, uid, rpgMap, registry):
        if MyFlames.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "flame-frames.png")
            MyFlames.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(MyFlames.framesImage)
        spriteFrames = StaticFrames(animationFrames, 6)
        OtherSprite.__init__(self, uid, registry, rpgMap, spriteFrames, (4, 2))

class MyCoin(OtherSprite):
    
    baseRectWidth = 8 * SCALAR    
    framesImage = None
    
    def __init__(self, uid, rpgMap, registry):
        if MyCoin.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "coin-frames.png")
            MyCoin.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(MyCoin.framesImage)
        spriteFrames = StaticFrames(animationFrames, 6)
        OtherSprite.__init__(self, uid, registry, rpgMap, spriteFrames, (2, 2))
        
    def processCollision(self, player):
        metadata = CoinMetadata(self.uid)
        self.registry.registerMetadata(metadata)
        player.incrementCoinCount()
        self.toRemove = True

class MyKey(OtherSprite):
    
    baseRectWidth = 8 * SCALAR    
    framesImage = None
    
    def __init__(self, uid, rpgMap, registry):
        if MyKey.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "key-frames.png")
            MyKey.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(MyKey.framesImage, 6)
        spriteFrames = StaticFrames(animationFrames, 6)
        OtherSprite.__init__(self, uid, registry, rpgMap, spriteFrames, (2, 2))
        
    def processCollision(self, player):
        metadata = KeyMetadata(self.uid)
        self.registry.registerMetadata(metadata)
        player.incrementKeyCount()
        self.toRemove = True
