#!/usr/bin/env python

from sprites import *
from spritemovement import NoMovementStrategy, RobotMovementStrategy
from spriteframes import StaticFrames
from rpg.spritemetadata import KeyMetadata, CoinMetadata

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

