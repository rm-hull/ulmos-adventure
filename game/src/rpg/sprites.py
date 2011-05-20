#!/usr/bin/env python

import os
import pygame
import view

from pygame.locals import Rect
from view import SCALAR, TILE_SIZE
from rpg.spritemovement import NoMovementStrategy, RobotMovementStrategy

MOVE_UNIT = 1 * SCALAR
NO_BOUNDARY = 0

# we may need to specify these on a sprite by sprite basis 
BASE_RECT_HEIGHT = 9 * SCALAR
BASE_RECT_EXTEND = 1 * SCALAR

SPRITES_FOLDER = "sprites"

"""
Base sprite class that supports being masked by the map.
"""
class RpgSprite(pygame.sprite.Sprite):

    def __init__(self, uid, registry, rpgMap, spriteFrames, position = (0, 0)):
        pygame.sprite.Sprite.__init__(self)
        # properties common to all RpgSprites
        self.uid = uid
        self.registry = registry
        self.rpgMap = rpgMap
        self.spriteFrames = spriteFrames
        self.position = [i * SCALAR for i in position]
        self.image = self.spriteFrames.getCurrentFrame()
        # indicates if this sprite is currently visible
        self.active = False
        # indicates if this sprite is currently masked by any map tiles
        self.masked = False
        # indicates if this sprite should be removed on next update
        self.toRemove = False

    def setPosition(self, x, y, level):
        self.x, self.y = x, y
        self.resetPosition(x * TILE_SIZE + self.position[0],
                           y * TILE_SIZE + self.position[1],
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
        # print self.uid, self.baseRect.width, self.baseRect.height

    def doMove(self, px, py):
        self.mapRect.move_ip(px, py)
        self.baseRect.move_ip(px, py)
        # pseudo z order that is used to test if one sprite is behind another
        self.z = int(self.mapRect.bottom + self.level * TILE_SIZE)

    def clearMasks(self):
        if self.masked:
            self.masked = False
            self.spriteFrames.repairCurrentFrame()
        
    def applyMasks(self):
        # masks is a map of lists, keyed on the associated tile points
        masks = self.rpgMap.getMasks(self)
        if len(masks) > 0:
            self.masked = True
            for tilePoint in masks:
                px = tilePoint[0] * view.TILE_SIZE - self.mapRect.left
                py = tilePoint[1] * view.TILE_SIZE - self.mapRect.top
                [self.image.blit(mask, (px, py)) for mask in masks[tilePoint]]
                
    def advanceFrame(self, increment):
        self.image = self.spriteFrames.advanceFrame(increment)
        
    def isIntersecting(self, sprite):
        if self != sprite and self.level == sprite.level and self.baseRect.colliderect(sprite.baseRect):
            return True
        return False;
        
    def processCollision(self, player):
        pass
    
    def processAction(self, player):
        pass

"""
Base class for any sprites that aren't either the player or a fixed sprite.
"""
class OtherSprite(RpgSprite):
    
    def __init__(self, uid, registry, rpgMap, spriteFrames, position = (0, 0)):
        RpgSprite.__init__(self, uid, registry, rpgMap, spriteFrames, position)
    
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
            # apply movement
            px, py = self.movement.getMovement(self.mapRect.topleft)            
            self.doMove(px, py)
            # make self.rect relative to the view
            self.rect.topleft = (self.mapRect.left - viewRect.left,
                                 self.mapRect.top - viewRect.top)
            if self.mapRect.colliderect(viewRect):
                # some part of this sprite is in the view
                self.clearMasks()
                self.advanceFrame(increment)
                self.applyMasks()
                if not self.active:
                    self.active = True
                    self.add(visibleSprites)
                return
        if self.active:
            self.active = False
            self.remove(visibleSprites)
                                   
"""
Sprite group that ensures pseudo z ordering for the sprites.  This works
because internally AbstractGroup calls self.sprites() to get a list of sprites
before it draws them.  I've overidden the sprites() method to return the
sprites in the correct order - this works, but I might be in trouble if the
internals of AbstractGroup ever changes.
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
        