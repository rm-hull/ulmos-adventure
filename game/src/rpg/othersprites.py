#!/usr/bin/env python

from sprites import *
from rpg.spritemovement import RobotMovementStrategy

"""
Defines a sprite that doesn't move independently, although (unlike FixedSprite)
it does move with the view.
"""
class OtherSprite(MaskSprite):
    
    def __init__(self, uid, registry, animationFrames, position = (0, 0)):
        MaskSprite.__init__(self, uid, registry, 6, position)
        # view rect is the scrolling window onto the map
        #self.viewRect = Rect((0, 0), pygame.display.get_surface().get_size())
        # animation frames
        #self.direction = DOWN
        self.animationFrames = animationFrames     
        self.numFrames = len(animationFrames)
        # additional animation properties
        self.image = animationFrames[self.animFrameCount]
        self.movement = RobotMovementStrategy([(4, 4), (9, 4)], (4, 2));

    def update(self, viewRect, gameSprites, visibleSprites, increment):
        if self.toRemove:
            self.remove(gameSprites)
        else:
            self.advanceFrame(increment)
            px, py = self.movement.getMovement(self.mapRect.topleft)            
            self.doMove(px, py)
            # make self.rect relative to the view
            self.rect.topleft = (self.mapRect.left - viewRect.left,
                                 self.mapRect.top - viewRect.top)
            print self.baseRect            
        if self.mapRect.colliderect(viewRect):
            if not self.active:
                self.active = True
                self.add(visibleSprites)
            return
        if self.active:
            self.active = False
            self.remove(visibleSprites)
            
    def advanceFrame(self, increment):
        if increment:
            self.frameCount = (self.frameCount + increment) % self.frameSkip
            if (self.frameCount == 0):
                self.animFrameCount = (self.animFrameCount + 1) % self.numFrames       
                self.image = self.animationFrames[self.animFrameCount]
            
class Baddie(OtherSprite):
    
    framesImage = None
    
    def __init__(self, uid, rpgMap, registry):
        if Baddie.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "flame-frames.png")
            Baddie.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Baddie.framesImage)
        OtherSprite.__init__(self, uid, registry, animationFrames, (4, 2))
        self.rpgMap = rpgMap

    def processCollision(self, player):
        #metadata = CoinMetadata(self.uid)
        #self.registry.registerMetadata(metadata)
        #player.incrementCoinCount()
        #self.toRemove = True
        pass
