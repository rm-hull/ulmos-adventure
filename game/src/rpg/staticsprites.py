#!/usr/bin/env python

from sprites import *

from spritemetadata import KeyMetadata, CoinMetadata, DoorMetadata
from spriteframes import StaticFrames

pickupSoundPath = os.path.join(SOUNDS_FOLDER, "pickup.wav")
pickupSound = pygame.mixer.Sound(pickupSoundPath)

doorSoundPath = os.path.join(SOUNDS_FOLDER, "door.wav")
doorSound = pygame.mixer.Sound(doorSoundPath)

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
        pickupSound.play()
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
        pickupSound.play()
        metadata = KeyMetadata(self.uid)
        self.registry.registerMetadata(metadata)
        player.incrementKeyCount()
        self.toRemove = True

class Chest(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (8 * SCALAR, BASE_RECT_HEIGHT)
        
    def __init__(self, rpgMap):
        if Chest.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "chest.png")
            Chest.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Chest.framesImage, 1)
        spriteFrames = StaticFrames(animationFrames, 6)
        OtherSprite.__init__(self, rpgMap, spriteFrames)
        
    # override
    def advanceFrame(self, increment, metadata):
        pass
                
class Rock(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (8 * SCALAR, BASE_RECT_HEIGHT)
        
    def __init__(self, rpgMap):
        if Rock.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "rock.png")
            Rock.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Rock.framesImage, 1)
        spriteFrames = StaticFrames(animationFrames, 6)
        OtherSprite.__init__(self, rpgMap, spriteFrames, (0, -4))
        
    # override
    def advanceFrame(self, increment, metadata):
        pass
                
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

    """
    Base rect extends beyond the bottom of the sprite image so player's base
    rect can intersect with it and allow it to be opened.
    """
    def getBaseRectTop(self, baseRectHeight):
        return self.mapRect.bottom + BASE_RECT_EXTEND - baseRectHeight
        
    # override
    def advanceFrame(self, increment, metadata):
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
            doorSound.play()
