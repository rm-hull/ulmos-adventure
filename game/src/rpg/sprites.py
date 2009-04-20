#!/usr/bin/env python

import os
import pygame
import view

from pygame.locals import Rect
from view import UP, DOWN, LEFT, RIGHT, OFFSET, SCALAR, TILE_SIZE

MOVE_UNIT = 1 * SCALAR
NO_BOUNDARY = 0

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

# we may need to specify these on a sprite by sprite basis 
BASE_RECT_HEIGHT = 9 * SCALAR
BASE_RECT_EXTEND = 1 * SCALAR

SPRITES_FOLDER = "sprites"

EMPTY_LIST = []

# ====================
# == MODULE METHODS ==
# ====================

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
        baseRectTop = self.mapRect.bottom + BASE_RECT_EXTEND - myBaseRectHeight - 1
        baseRectLeft = (self.mapRect.width - myBaseRectWidth) / 2
        self.baseRect = Rect(baseRectLeft, baseRectTop, myBaseRectWidth, myBaseRectHeight)

"""
Sprite that supports being masked by tile images that are 'closer' to the viewer
than the sprite.
"""
class MaskSprite(RpgSprite):
    
    def __init__(self, rpgMap, frameSkip, position = (0, 0)):
        # pygame.sprite.Sprite.__init__(self, self.containers)
        RpgSprite.__init__(self, frameSkip, position)
        # properties common to all MaskSprites
        self.rpgMap = rpgMap
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
An animated player controlled sprite.  This provides movement + masking by
extending MaskSprite, but all animation functionality is encapsulated here.
"""        
class Player(MaskSprite):
    
    def __init__(self, rpgMap, animationFrames, position = (0, 0)):
        MaskSprite.__init__(self, rpgMap, 6, position)
        # view rect is the scrolling window onto the map
        self.viewRect = Rect((0, 0), pygame.display.get_surface().get_size())
        # animation frames
        self.direction = DOWN
        self.animationFrames = animationFrames     
        self.numFrames = len(animationFrames[self.direction])
        # additional animation properties
        self.imageInfo = (self.direction, self.animFrameCount)
        self.image = animationFrames[self.direction][self.animFrameCount]
        # sprite state
        self.movement = None
        self.coinCount = 0
    
    """
    The view rect is entirely determined by what the main sprite is doing.  Sometimes
    we move the view, sometimes we move the sprite - it just depends where the main
    sprite is on the map.
    """
    def getViewRect(self):
        # centre self.rect in the view
        px, py = (self.viewRect.width - self.rect.width) // 2, (self.viewRect.height - self.rect.height) // 2
        self.rect.topleft = (px, py)
        self.viewRect.topleft = (self.mapRect.left - px, self.mapRect.top - py)
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
    
    """
    Moves the player / view rect.  The control flow is as follows:
    > Check for deferred movement and apply if necessary.
    > Otherwise, check the requested movement falls within the boundary.
    > If it does, attempt to apply the requested movement.
    > If not valid, attempt to shuffle the player.
    > If still not valid, check for a change in direction.
    """
    def move(self, directionBits):
        useCurrentView, boundary = True, NO_BOUNDARY
        movement = getMovement(directionBits)
        if movement:
            # check for deferred movement first
            if movement == self.movement:
                level, direction, px, py = self.deferredMovement
                useCurrentView = self.wrapMovement(level, direction, px, py)
            else:
                # normal movement
                px, py, direction, diagonal = movement
                boundary = self.getBoundary(px, py)
                if boundary == NO_BOUNDARY:
                    # we're within the boundary, but is it valid?
                    newBaseRect = self.baseRect.move(px, py)
                    valid, level = self.rpgMap.isMoveValid(self.level, newBaseRect)
                    if valid:
                        #if diagonal:
                        #    self.movement = movement
                        #    self.deferMovement(level, direction, px, py)
                        #else:
                        useCurrentView = self.wrapMovement(level, direction, px, py)
                    else:
                        if diagonal:
                            valid = self.slide(movement)
                        else:
                            valid = self.shuffle(movement)
                        self.changeDirection(level, direction, valid)
        # return
        if useCurrentView:
            return boundary, self.viewRect
        return boundary, self.getViewRect()
    
    """
    Slides the player.
    """
    def slide(self, movement):
        px, py, direction, diagonal = movement
        # check if we can slide horizontally
        xBaseRect = self.baseRect.move(px, 0)
        valid, level = self.rpgMap.isMoveValid(self.level, xBaseRect)
        if valid:
            self.movement = movement
            self.deferMovement(level, direction, px, 0)
            return valid
        # check if we can slide vertically
        yBaseRect = self.baseRect.move(0, py)
        valid, level = self.rpgMap.isMoveValid(self.level, yBaseRect)                
        if valid:
            self.movement = movement
            self.deferMovement(level, direction, 0, py)
        return valid
        
    """
    Shuffles the player.  Eg. if the player is attempting to move up, but is
    blocked, we will 'shuffle' the player left/right if there is valid movement
    available to the left/right.  This helps to align the player with steps,
    archways, etc.
    """
    def shuffle(self, movement):
        px, py, direction, diagonal = movement
        # check if we can shuffle horizontally
        if px == 0:
            valid, level, shuffle = self.rpgMap.isVerticalValid(self.level, self.baseRect)
            if valid:
                self.movement = movement
                self.deferMovement(level, direction, px + shuffle * MOVE_UNIT, 0)
            return valid
        # check if we can shuffle vertically
        valid, level, shuffle = self.rpgMap.isHorizontalValid(self.level, self.baseRect)
        if valid:
            self.movement = movement
            self.deferMovement(level, direction, 0, py + shuffle * MOVE_UNIT)
        return valid
    
    """
    Applies a stationary change in direction if movement is not valid.
    """
    def changeDirection(self, level, direction, valid):
        if not valid and self.direction != direction:
            # we need to animate the sprite to show a change in direction
            # but we set px and py to zero so it doesn't move anywhere
            self.applyMovement(level, direction, 0, 0)
    
    """
    Calls applyMovement and performs some additional operations.
    """      
    def wrapMovement(self, level, direction, px, py):
        self.applyMovement(level, direction, px, py)
        self.movement = None
        return False
    
    """
    Stores the deferred movement and calls applyMovement with px, py = 0 for a
    'running on the spot' effect.
    """
    def deferMovement(self, level, direction, px, py):
        # store the deferred movement 
        self.deferredMovement = (level, direction, px, py)
        self.applyMovement(level, direction, 0, 0)
    
    """
    Applies valid movement.
    """
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
    
    """
    Checks the requested movement falls within the map boundary.  If not, returns
    the boundary edge that has been breached. 
    """ 
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
    
    """
    Processes collisions with other sprites in the given sprite collection.
    """
    def processCollisions(self, sprites):
        # if there are less than two sprites
        if len(sprites) < 2:
            return EMPTY_LIST
        toRemove = []
        for sprite in sprites:
            if sprite != self and sprite.level == self.level:
                # they're on the same level, but do their base rects intersect?
                if hasattr(sprite, "processCollision") and self.baseRect.colliderect(sprite.baseRect):
                    if sprite.processCollision(self):
                        toRemove.append(sprite)
        return toRemove
                    
    # overidden  
    def repairImage(self):
        direction, animFrameCount = self.imageInfo
        lastImage = self.animationFrames[direction][animFrameCount]
        lastImage.blit(self.animationFrames[direction + OFFSET][animFrameCount], (0, 0))

    def incrementCoinCount(self, n):
        self.coinCount += n
        print self.coinCount
    
class Ulmo(Player):
    
    framesImage = None
    
    def __init__(self, rpgMap):
        if self.framesImage is None:          
            imagePath = os.path.join(SPRITES_FOLDER, "ulmo-frames.png")
            self.framesImage = view.loadScaledImage(imagePath, None)
        animationFrames = view.processMovementFrames(self.framesImage)
        Player.__init__(self, rpgMap, animationFrames, (1, 4))
        
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
            
class Flames(StaticSprite):
    
    framesImage = None
    
    def __init__(self):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "flames.png")
            self.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(self.framesImage)
        StaticSprite.__init__(self, animationFrames, 6, (4, 2))

class Coin(StaticSprite):
    
    baseRectWidth = 8 * SCALAR    
    framesImage = None
    
    def __init__(self):
        if self.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "coin.png")
            self.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(self.framesImage)
        StaticSprite.__init__(self, animationFrames, 6, (2, 2))
        
    def processCollision(self, player):
        player.incrementCoinCount(1)
        return True

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
        