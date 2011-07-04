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

class Wasp(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (9 * SCALAR, 12 * SCALAR)    

    def __init__(self, rpgMap):
        if Wasp.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "wasp-frames.png")
            Wasp.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processMovementFrames(Wasp.framesImage, 2)
        spriteFrames = DirectionalFrames(animationFrames, 4)
        OtherSprite.__init__(self, rpgMap, spriteFrames)
        
    def processCollision(self, player):
        print "life lost!"
        player.loseLife()
        return True
    
    