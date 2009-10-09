#!/usr/bin/env python

import os
import pygame
import view
import eventinfo

from pygame.locals import Rect
from view import UP, DOWN, LEFT, RIGHT, OFFSET, SCALAR, TILE_SIZE, VIEW_WIDTH

MOVE_UNIT = 1 * SCALAR
NO_BOUNDARY = 0

# we may need to specify these on a sprite by sprite basis 
BASE_RECT_HEIGHT = 9 * SCALAR
BASE_RECT_EXTEND = 1 * SCALAR

SPRITES_FOLDER = "sprites"

EMPTY_LIST = []

DUMMY_EVENT = eventinfo.DummyEvent()

# ====================
# == MODULE METHODS ==
# ====================

# valid movement combinations - movement is keyed on direction bits and is
# stored as a tuple (px, py, direction, diagonal) 
MOVEMENT = {UP: (0, -MOVE_UNIT, UP, False),
            DOWN: (0, MOVE_UNIT, DOWN, False),
            LEFT: (-MOVE_UNIT, 0, LEFT, False),
            RIGHT: (MOVE_UNIT, 0, RIGHT, False),
            UP + LEFT: (-MOVE_UNIT, -MOVE_UNIT, UP, True),
            UP + RIGHT: (MOVE_UNIT, -MOVE_UNIT, UP, True),
            DOWN + LEFT: (-MOVE_UNIT, MOVE_UNIT, DOWN, True),
            DOWN + RIGHT: (MOVE_UNIT, MOVE_UNIT, DOWN, True)}

def getMovement(directionBits):
    if directionBits in MOVEMENT:
        return MOVEMENT[directionBits]
    return None

"""
Base sprite class.
"""
class RpgSprite(pygame.sprite.Sprite):

    def __init__(self, frameSkip, position = (0, 0)):
        # pygame.sprite.Sprite.__init__(self, self.containers)
        pygame.sprite.Sprite.__init__(self)
        # properties common to all RpgSprites
        self.position = [i * SCALAR for i in position]
        self.frameSkip = frameSkip
        self.animFrameCount = 0
        self.frameCount = 0
        # indicates if this sprite is currently visible
        self.active = False
        # indicates if this sprite should be removed on next update
        self.toRemove = False

    def setPosition(self, x, y, level):
        self.resetPosition(x * view.TILE_SIZE + self.position[0],
                           y * view.TILE_SIZE + self.position[1],
                           level)

    def resetPosition(self, px = 0, py = 0, level = None):
        # main rect
        self.rect = self.image.get_rect()
        # other rectangles as required by the game engine
        self.mapRect = self.image.get_rect()
        self.initBaseRect()
        # if required, move to the requested position
        if level:
            self.level = level
        if px > 0 or py > 0:
            self.doMove(px, py)
        
    def doMove(self, px, py):
        self.mapRect.move_ip(px, py)
        self.baseRect.move_ip(px, py)
        # pseudo z order that is used to test if one sprite is behind another
        self.z = int(self.mapRect.bottom + self.level * TILE_SIZE)

    def initBaseRect(self):
        myBaseRectWidth = self.mapRect.width 
        if hasattr(self, "baseRectWidth"):
            myBaseRectWidth = self.baseRectWidth
        myBaseRectHeight = BASE_RECT_HEIGHT
        if hasattr(self, "baseRectHeight"):
            myBaseRectHeight = self.baseRectHeight
        baseRectTop = self.mapRect.bottom + BASE_RECT_EXTEND - myBaseRectHeight
        baseRectLeft = (self.mapRect.width - myBaseRectWidth) / 2
        self.baseRect = Rect(baseRectLeft, baseRectTop, myBaseRectWidth, myBaseRectHeight)

"""
Sprite that supports being masked by tile images that are 'closer' to the viewer
than the sprite.
"""
class MaskSprite(RpgSprite):
    
    def __init__(self, frameSkip, position = (0, 0)):
        # pygame.sprite.Sprite.__init__(self, self.containers)
        RpgSprite.__init__(self, frameSkip, position)
        # properties common to all MaskSprites
        self.masked = False

    def doMove(self, px, py):
        RpgSprite.doMove(self, px, py)
        self.applyMasks()
        
    def applyMasks(self):
        # clear any existing masking first
        if self.masked:
            self.masked = False
            self.repairImage()
        # masks is a map of lists, keyed on the associated tile points
        masks = self.rpgMap.getMasks(self)
        if len(masks) > 0:
            self.masked = True
            for tilePoint in masks:
                px = tilePoint[0] * view.TILE_SIZE - self.mapRect.left
                py = tilePoint[1] * view.TILE_SIZE - self.mapRect.top
                [self.image.blit(mask, (px, py)) for mask in masks[tilePoint]]
    
    """
    Override this method - this needs to repair the previous image used by the
    sprite since we have just drawn a piece of the background over it.
    """
    def repairImage(self):
        pass

"""
Defines a sprite that doesn't move independently, although it does move with the view.
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
    
    def __init__(self):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "flame-frames.png")
            self.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(self.framesImage)
        StaticSprite.__init__(self, animationFrames, 6, (4, 2))

class Coin(StaticSprite):
    
    baseRectWidth = 8 * SCALAR    
    framesImage = None
    
    def __init__(self, coinInfo = None):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "coin-frames.png")
            self.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(self.framesImage)
        StaticSprite.__init__(self, animationFrames, 6, (2, 2))
        self.coinInfo = coinInfo
        
    def processCollision(self, player):
        if self.coinInfo:
            self.coinInfo.available = False
        player.incrementCoinCount()
        self.toRemove = True

class Key(StaticSprite):
    
    baseRectWidth = 8 * SCALAR    
    framesImage = None
    
    def __init__(self, keyInfo = None):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "key-frames.png")
            self.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(self.framesImage, 6)
        StaticSprite.__init__(self, animationFrames, 6, (2, 2))
        self.keyInfo = keyInfo
        
    def processCollision(self, player):
        if self.keyInfo:
            self.keyInfo.available = False
        player.incrementKeyCount()
        self.toRemove = True

class Door(StaticSprite):
    
    baseRectWidth = 4 * SCALAR    
    framesImage = None
    
    def __init__(self, rpgMap, doorInfo = None):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "door-frames.png")
            self.framesImage = view.loadScaledImage(imagePath, None)        
        self.additionalFrames = view.processStaticFrames(self.framesImage, 8)
        animationFrames = [self.additionalFrames[0]]
        StaticSprite.__init__(self, animationFrames, 6, (0, 0))
        self.rpgMap = rpgMap
        self.doorInfo = doorInfo
        self.opening = False
        
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
        if self.doorInfo:
            self.doorInfo.closed = False
        # make the corresponding tile available for this level
        self.rpgMap.addLevel(self.x, self.y + 1, self.level)
        
    def processAction(self, player):
        if player.keyCount.count > 0:
            player.keyCount.incrementCount(-1)
            self.opening = True
    
       
"""
Defines a sprite that is fixed on the game display.
"""
class FixedSprite(pygame.sprite.Sprite):

    def __init__(self, image, position = (0, 0)):
        # pygame.sprite.Sprite.__init__(self, self.containers)
        pygame.sprite.Sprite.__init__(self)
        # properties common to all RpgSprites
        self.position = [i * SCALAR for i in position]
        self.setImage(image)
        
    def setImage(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.move_ip(self.position[0], self.position[1])
        

class FixedCoin(FixedSprite):

    initialImage = None
    
    def __init__(self, position = (0, 0)):
        if self.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "small-coin.png")
            self.initialImage = view.loadScaledImage(imagePath, None)
        FixedSprite.__init__(self,
                             view.createDuplicateSpriteImage(self.initialImage),
                             position)

class CoinCount(FixedSprite):
    
    initialImage = None
    
    def __init__(self, position = (0, 0)):
        if self.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "numbers.png")
            self.initialImage = view.loadScaledImage(imagePath, None)
        self.numbers = view.processStaticFrames(self.initialImage, 10)        
        FixedSprite.__init__(self, self.numbers[0], position)
        self.count = 0;
        
    def incrementCount(self, increment = 1):
        self.count += increment
        self.newImage()
        
    def newImage(self):
        countString = str(self.count)
        dimensions = (len(countString) * 8 * SCALAR, 8 * SCALAR)
        newImage = view.createTransparentRect(dimensions)
        newImage.set_colorkey(view.TRANSPARENT_COLOUR, view.RLEACCEL)
        px = 0;
        for n in countString:
            newImage.blit(self.numbers[int(n)], (px, 0))
            px += 8 * SCALAR
        self.setImage(newImage)

class KeyCount(FixedSprite):
    
    initialImage = None
    
    def __init__(self, position = (0, 0)):
        FixedSprite.__init__(self, view.createTransparentRect((0, 8)), position)
        if self.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "small-key.png")
            self.initialImage = view.loadScaledImage(imagePath, None)
        self.keyImage = view.createDuplicateSpriteImage(self.initialImage)
        self.count = 0;
        
    def incrementCount(self, increment = 1):
        self.count += increment
        self.newImage()
        
    def newImage(self):        
        # countString = str(self.count)
        dimensions = (self.count * 8 * SCALAR, 8 * SCALAR)
        newImage = view.createTransparentRect(dimensions)
        px = 0;
        for n in range(self.count):
            newImage.blit(self.keyImage, (px, 0))
            px += 8 * SCALAR
        self.setImage(newImage)
        self.rect.left = VIEW_WIDTH - (3 + self.count * 8) * SCALAR
            
"""
Sprite group that ensures pseudo z ordering for the sprites.  This works
because internally AbstractGroup calls self.sprites() to get a list of sprites
before it draws them.  I've overidden the sprites() method to return the
sprites in the correct order - this works, but I might be in trouble if the
internals of AbstractGroup should ever change.
"""
class RpgSprites(pygame.sprite.Group):
    
    def __init__(self, *sprites):
        pygame.sprite.AbstractGroup.__init__(self)
        self.add(*sprites)
        
    def sprites(self):
        # return the sprites sorted on their z field to ensure 
        # that they appear in the correct 'z' order
        return sorted(self.spritedict.keys(),
                      lambda sprite1, sprite2: sprite1.z - sprite2.z)
        