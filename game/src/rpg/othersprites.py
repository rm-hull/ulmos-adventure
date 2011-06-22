#!/usr/bin/env python

from sprites import *
from spriteframes import DirectionalFrames

class Beetle(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (9 * SCALAR, 12 * SCALAR)    

    def __init__(self, rpgMap):
        if Beetle.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "beetle-frames.png")
            Beetle.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processMovementFrames(Beetle.framesImage, 2)
        spriteFrames = DirectionalFrames(animationFrames, 12)
        OtherSprite.__init__(self, rpgMap, spriteFrames)

    def processCollision(self, player):
        print "life lost!"
        player.loseLife()
        return True

class ZoomBeetle(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (9 * SCALAR, 12 * SCALAR)    

    def __init__(self, rpgMap):
        if ZoomBeetle.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "beetle-frames.png")
            ZoomBeetle.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processMovementFrames(ZoomBeetle.framesImage, 2)
        spriteFrames = DirectionalFrames(animationFrames, 12)
        OtherSprite.__init__(self, rpgMap, spriteFrames)
        self.turning = False
        self.zooming = False
        
    def update(self, player, viewRect, gameSprites, visibleSprites, increment):
        # is the player aligned vertically / horizontally with this sprite?
        # if yes, turn to face the player
        self.turning = True
        # are we facing the player?
        # if yes, start zooming towards the player
        self.turning = False
        self.zooming = True
        
    def processCollision(self, player):
        print "life lost!"
        player.loseLife()
        return True
    
    