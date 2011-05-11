#!/usr/bin/env python

import events

from sprites import *
from view import UP, DOWN, LEFT, RIGHT, OFFSET

DUMMY_EVENT = events.DummyEvent()

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
An animated player controlled sprite.  This provides movement + masking by
extending MaskSprite, but all animation functionality is encapsulated here.
"""        
class Player(MaskSprite):
    
    def __init__(self, uid, registry, animationFrames, position = (0, 0)):
        MaskSprite.__init__(self, uid, registry, 6, position)
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
        self.coinCount = None
        self.keyCount = None
    
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
    def handleMovement(self, directionBits):
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
                boundary = self.getBoundaryEvent(px, py)
                if not boundary:
                    # we're within the boundary, but is it valid?
                    newBaseRect = self.baseRect.move(px, py)
                    valid, level = self.rpgMap.isMoveValid(self.level, newBaseRect)
                    if valid:
                        useCurrentView = self.wrapMovement(level, direction, px, py)
                    else:
                        if diagonal:
                            valid = self.slide(movement)
                        else:
                            valid = self.shuffle(movement)
                        # apply a stationary change of direction if required
                        if not valid and self.direction != direction:
                            self.setDirection(direction);
        # return
        if useCurrentView:
            return boundary, self.viewRect
        return boundary, self.getViewRect()
    
    """
    Slides the player. If the player is attempting to move diagonally, but is
    blocked, the vertical or horizontal component of their movement may still
    be valid.
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
        self.frameCount = (self.frameCount + 1) % self.frameSkip
        if (self.frameCount == 0):
            self.animFrameCount = (self.animFrameCount + 1) % self.numFrames    
        self.image = self.animationFrames[self.direction][self.animFrameCount]
        # move the sprite to its new location
        self.doMove(px, py)
        # keep this information for next time
        self.imageInfo = (self.direction, self.animFrameCount)
    
    """
    Sets the direction without moving anywhere.
    """
    def setDirection(self, direction):
        self.applyMovement(self.level, direction, 0, 0)
        
    """
    Checks the requested movement falls within the map boundary.  If not, returns
    a boundary event containing information on the breach. 
    """ 
    def getBoundaryEvent(self, px, py):
        testMapRect = self.mapRect.move(px, py)
        if self.rpgMap.mapRect.contains(testMapRect):
            # we're within the boundary
            return None
        boundary = self.getBoundary(testMapRect)
        if boundary in self.rpgMap.boundaryTriggers:
            tileRange = self.getTileRange(boundary)
            for trigger in self.rpgMap.boundaryTriggers[boundary]:
                testList = [i in trigger.range for i in tileRange]
                if all(testList):
                    return trigger.event
        return DUMMY_EVENT
    
    """
    Returns the boundary that has been breached.
    """
    def getBoundary(self, testMapRect):
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

    def getTileRange(self, boundary):
        x1, y1 = self.convertPixelPoint(self.baseRect.left, self.baseRect.top)
        x2, y2 = self.convertPixelPoint(self.baseRect.right - 1, self.baseRect.bottom - 1)
        print "(%s, %s) -> (%s, %s)" % (x1, y1, x2, y2)
        if boundary == UP or boundary == DOWN:
            return range(x1, x2 + 1)
        return range(y1, y2 + 1)
    
    def convertPixelPoint(self, px, py):
        return px // TILE_SIZE, py // TILE_SIZE
            
    """
    Processes events triggered via event tiles.
    """
    def processEvents(self):
        if self.level in self.rpgMap.tileTriggers:
            for trigger in self.rpgMap.tileTriggers[self.level]:
                if self.baseRect.colliderect(trigger.rect):
                    return trigger.event
        return None
    
    """
    Processes collisions with other sprites in the given sprite collection.
    """
    def processCollisions(self, sprites):
        # if there are less than two sprites then self is the only sprite
        if len(sprites) < 2:
            return
        for sprite in sprites:
            if sprite.isIntersecting(self):
                sprite.processCollision(self)

    """
    Processes interactions with other sprites in the given sprite collection.
    """
    def processActions(self, sprites):
        # if there are less than two sprites then self is the only sprite
        if len(sprites) < 2:
            return
        for sprite in sprites:
            if sprite.isIntersecting(self):
                sprite.processAction(self)
                    
    """
    Handles action input from the user.
    """
    def handleAction(self, sprites):
        self.processActions(sprites)
                    
    # overidden  
    def repairImage(self):
        direction, animFrameCount = self.imageInfo
        lastImage = self.animationFrames[direction][animFrameCount]
        lastImage.blit(self.animationFrames[direction + OFFSET][animFrameCount], (0, 0))

    def incrementCoinCount(self, n = 1):
        self.coinCount.incrementCoinCount(n)
        
    def incrementKeyCount(self, n = 1):
        self.keyCount.incrementKeyCount(n)
        
    def getKeyCount(self):
        return self.keyCount.count;

"""
Extends the player sprite by defining a set of frame images.
"""    
class Ulmo(Player):
    
    framesImage = None
    
    def __init__(self, registry):
        if Ulmo.framesImage is None:          
            imagePath = os.path.join(SPRITES_FOLDER, "ulmo-frames.png")
            Ulmo.framesImage = view.loadScaledImage(imagePath, None)
        animationFrames = view.processMovementFrames(Ulmo.framesImage)
        Player.__init__(self, "ulmo", registry, animationFrames, (1, 4))
        