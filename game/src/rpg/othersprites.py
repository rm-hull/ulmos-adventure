#!/usr/bin/env python

from sprites import *
from spriteframes import StaticFrames

class Baddie(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (4 * SCALAR, 12 * SCALAR)    

    def __init__(self, rpgMap):
        if Baddie.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "beetle-frames.png")
            Baddie.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Baddie.framesImage)
        spriteFrames = StaticFrames(animationFrames, 12)
        OtherSprite.__init__(self, rpgMap, spriteFrames)

    def processCollision(self, player):
        print "life lost!"
        return True

