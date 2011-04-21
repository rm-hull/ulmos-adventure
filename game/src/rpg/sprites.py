#!/usr/bin/env python

import os
import pygame
import view

from pygame.locals import Rect
from view import SCALAR, TILE_SIZE

MOVE_UNIT = 1 * SCALAR
NO_BOUNDARY = 0

# we may need to specify these on a sprite by sprite basis 
BASE_RECT_HEIGHT = 9 * SCALAR
BASE_RECT_EXTEND = 1 * SCALAR

SPRITES_FOLDER = "sprites"

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
        self.x, self.y = x, y
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
        