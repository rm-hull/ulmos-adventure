#!/usr/bin/env python

import os
import pygame
import view

from pygame.locals import Rect
from view import UP, DOWN, LEFT, RIGHT, OFFSET, SCALAR, TILE_SIZE

MOVE_UNIT = 1 * SCALAR
NO_BOUNDARY = 0

# valid movement combinations - movement is keyed on direction bits and is
# stored as a tuple (px, py, direction) 
MOVEMENT = {UP: (0, -MOVE_UNIT, UP),
            DOWN: (0, MOVE_UNIT, DOWN),
            LEFT: (-MOVE_UNIT, 0, LEFT),
            RIGHT: (MOVE_UNIT, 0, RIGHT),
            UP + LEFT: (-MOVE_UNIT, -MOVE_UNIT, UP),
            UP + RIGHT: (MOVE_UNIT, -MOVE_UNIT, UP),
            DOWN + LEFT: (-MOVE_UNIT, MOVE_UNIT, DOWN),
            DOWN + RIGHT: (MOVE_UNIT, MOVE_UNIT, DOWN)}

# we may need to specify these on a sprite by sprite basis 
BASE_RECT_HEIGHT = 9 * SCALAR
BASE_RECT_EXTEND = 1 * SCALAR

SPRITES_FOLDER = "sprites"

# ====================
# == MODULE METHODS ==
# ====================

def getMovement(directionBits):
    if directionBits in MOVEMENT:
        return MOVEMENT[directionBits]
    return None

"""
Sprite that supports movement and being masked by tile images that are 'closer'
to the viewer than the sprite.
"""
class MaskSprite(pygame.sprite.Sprite):
    
    def __init__(self, rpgMap, position = (0, 0)):
        # pygame.sprite.Sprite.__init__(self, self.containers)
        pygame.sprite.Sprite.__init__(self)
        # properties common to all MaskSprites
        self.rpgMap = rpgMap
        self.masked = False
        self.position = [i * SCALAR for i in position]

    def setPosition(self, x, y, level):
        self.resetPosition(x * view.TILE_SIZE + self.position[0],
                           y * view.TILE_SIZE + self.position[1],
                           level)
        
    def resetPosition(self, px = 0, py = 0, level = None):
        # main rect
        self.rect = self.image.get_rect()
        # other rectangles as required by the game engine
        self.mapRect = self.image.get_rect()
        baseTop = self.mapRect.bottom + BASE_RECT_EXTEND - BASE_RECT_HEIGHT - 1
        self.baseRect = Rect(0, baseTop, self.mapRect.width, BASE_RECT_HEIGHT)
        # view rect is the scrolling window onto the map
        self.viewRect = Rect((0, 0), pygame.display.get_surface().get_size())
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
    
    # Override this method - this needs to repair the previous image used by the
    # sprite since we have just drawn a piece of the background over it.    
    def repairImage(self):
        pass

"""
An animated player controlled sprite.  This provides movement + masking by
extending MaskSprite, but all animation functionality is encapsulated here.
"""        
class Player(MaskSprite):
    
    def __init__(self, rpgMap, animationFrames, position = (0, 0)):
        MaskSprite.__init__(self, rpgMap, position)
        self.animFrameCount = 1
        self.direction = DOWN
        # tweak these for animation variation
        self.frameSkip = 6
        self.frameCount = 0
        # init animation frames
        self.numFrames = len(animationFrames[self.direction])
        self.animationFrames = animationFrames     
        # essential sprite fields
        self.imageInfo = (self.direction, self.animFrameCount)
        self.image = animationFrames[self.direction][self.animFrameCount]
    
    # The view rect is entirely determined by what the main sprite is doing.
    # Sometimes we move the view, sometimes we move the sprite - it just depends
    # where the main sprite is on the map
    def getViewRect(self):
        # centre self.rect in the view
        px, py = (self.viewRect.width - self.rect.width) // 2, (self.viewRect.height - self.rect.height) // 2
        self.rect.topleft = (px, py)
        self.viewRect.topleft = (self.mapRect.left - px, self.mapRect.top - py)
        # mapImage = self.rpgMap.mapImage
        rpgMapRect = self.rpgMap.mapRect
        if rpgMapRect.contains(self.viewRect):
            return self.viewRect
        # the requested view falls partially outside the map - we need to move
        # the sprite instead of the view
        px, py = 0, 0
        if self.viewRect.left < 0:
            px = self.viewRect.left
        elif self.viewRect.right > rpgMapRect.right:
            px = self.viewRect.right - rpgMapRect.right
        if self.viewRect.top < 0:
            py = self.viewRect.top
        elif self.viewRect.bottom > rpgMapRect.bottom:
            py = self.viewRect.bottom - rpgMapRect.bottom
        self.rect.move_ip(px, py)
        self.viewRect.move_ip(-px, -py)
        return self.viewRect
    
    def move(self, directionBits):
        useCurrentView, boundary = True, NO_BOUNDARY
        movement = getMovement(directionBits)
        if movement:
            px, py, direction = movement
            boundary = self.getBoundary(px, py)
            if boundary == NO_BOUNDARY:
                # we're within the boundary, but is it valid?
                valid, level = self.rpgMap.isMoveValid(self.level,
                                                       self.baseRect.move(px, py))
                if valid:
                    self.applyMovement(level, direction, px, py)
                    useCurrentView = False
                else:
                    if self.direction != direction:
                        # we need to animate the sprite to show a change in direction
                        # but we set px and py to zero so it doesn't move anywhere
                        self.applyMovement(level, direction, 0, 0)
        # return
        if useCurrentView:
            return boundary, self.viewRect
        return boundary, self.getViewRect()
    
    def applyMovement(self, level, direction, px, py):
        # change any fields required for animation
        self.level = level
        self.direction = direction
        self.frameCount += 1
        if (self.frameCount % self.frameSkip == 0):
            self.animFrameCount = (self.animFrameCount + 1) % self.numFrames    
        self.image = self.animationFrames[self.direction][self.animFrameCount]
        # move the sprite to its new location
        self.doMove(px, py)
        # keep this information for next time
        self.imageInfo = (self.direction, self.animFrameCount)
    
    def getBoundary(self, px, py):
        testMapRect = self.mapRect.move(px, py)
        if self.rpgMap.mapRect.contains(testMapRect):
            # we're within the boundary
            return NO_BOUNDARY
        boundary = NO_BOUNDARY
        rpgMapRect = self.rpgMap.mapRect
        if testMapRect.left < 0:
            boundary = LEFT
        elif testMapRect.right > rpgMapRect.right:
            boundary = RIGHT
        if testMapRect.top < 0:
            boundary = UP
        elif testMapRect.bottom > rpgMapRect.bottom:
            boundary = DOWN
        return boundary
            
    # overidden  
    def repairImage(self):
        lastImage = self.animationFrames[self.imageInfo[0]][self.imageInfo[1]]
        lastImage.blit(self.animationFrames[self.imageInfo[0] + OFFSET][self.imageInfo[1]], (0, 0))

class Ulmo(Player):
    
    framesImage = None
    
    def __init__(self, rpgMap):
        if self.framesImage is None:          
            imagePath = os.path.join(SPRITES_FOLDER, "ulmo-frames.png")
            self.framesImage = view.loadScaledImage(imagePath, None, 2)
        animationFrames = view.processMovementFrames(self.framesImage)
        Player.__init__(self, rpgMap, animationFrames, (1, 4))
        
class Dude(Player):

    framesImage = None
    
    def __init__(self, rpgMap):    
        if self.framesImage is None:          
            imagePath = os.path.join(SPRITES_FOLDER, "dude.png")
            self.framesImage = view.loadScaledImage(imagePath, None, 2)
        animationFrames = view.processMovementFrames(framesImage, 3)
        Player.__init__(self, rpgMap, animationFrames)

"""
Defines a sprite that doesn't move independently, although it does move with the view.
"""
class Static(pygame.sprite.Sprite):
    
    def __init__(self, animationFrames, position = (0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.animFrameCount = 0
        # tweak these for animation variation
        self.frameSkip = 6
        self.frameCount = 0
        # init animation frames
        self.numFrames = len(animationFrames)
        self.animationFrames = animationFrames     
        # essential sprite fields
        self.image = animationFrames[self.animFrameCount]
        self.rect = self.image.get_rect()
        # other rectangles as required by the game engine
        self.mapRect = self.image.get_rect()
        self.position = [i * SCALAR for i in position]
        # indicates if this sprite is currently visible
        self.active = False

    def setPosition(self, x, y, level):
        self.level = level
        self.mapRect.topleft = (x * view.TILE_SIZE + self.position[0],
                                y * view.TILE_SIZE + self.position[1])
        # pseudo z order that is used to test if one sprite is behind another
        self.z = int(self.mapRect.bottom + self.level * TILE_SIZE)

    def update(self, viewRect, spriteGroup):
        if self.mapRect.colliderect(viewRect):
            # some part of this sprite is in the current view
            self.frameCount += 1
            if (self.frameCount % self.frameSkip == 0):
                self.animFrameCount = (self.animFrameCount + 1) % self.numFrames       
            self.image = self.animationFrames[self.animFrameCount]
            # make self.rect relative to the view
            self.rect.topleft = (self.mapRect.left - viewRect.left,
                                 self.mapRect.top - viewRect.top)
            if not self.active:
                self.active = True
                self.add(spriteGroup)
        elif self.active:
            self.active = False
            self.remove(spriteGroup)
            
class Flames(Static):
    
    framesImage = None
    
    def __init__(self):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "flames.png")
            self.framesImage = view.loadScaledImage(imagePath, None, 2)        
        animationFrames = view.processStaticFrames(self.framesImage)
        Static.__init__(self, animationFrames, (4, 2))

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
        
    def zOrder(self, sprite, anotherSprite):
        return sprite.z - anotherSprite.z
    
    def sprites(self):
        # return the sprites sorted on their z field to ensure 
        # that they appear in the correct 'z' order
        return sorted(self.spritedict.keys(), self.zOrder)
        