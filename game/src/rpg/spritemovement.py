#!/usr/bin/env python

from view import NONE, UP, DOWN, LEFT, RIGHT, SCALAR, TILE_SIZE, VIEW_WIDTH, VIEW_HEIGHT

from pygame.locals import Rect

DIRECTION = "direction"

"""
Metadata is used to provide a loose coupling between the sprite movement and
the sprite frames.  Anything the sprite frames might be interested in, eg. the
direction, can be passed through.
""" 
NO_METADATA = {}

UP_METADATA = {DIRECTION: UP}
DOWN_METADATA = {DIRECTION: DOWN}
LEFT_METADATA = {DIRECTION: LEFT}
RIGHT_METADATA = {DIRECTION: RIGHT}

ZOOM_MOVEMENT = {UP: (0, -2 * SCALAR, UP_METADATA),
                 DOWN: (0, 2 * SCALAR, DOWN_METADATA),
                 LEFT: (-2 * SCALAR, 0, LEFT_METADATA),
                 RIGHT: (2 * SCALAR, 0, RIGHT_METADATA)}

class MovementStrategy:
    
    def __init__(self, sprite, level, tilePoints):
        # initialise the sprite
        sprite.setTilePosition(tilePoints[0][0], tilePoints[0][1], level)
        sprite.movement = self
        # keep these for later
        self.sprite = sprite
        self.level = level
        self.tilePoints = tilePoints
        
    def getMovement(self, currentPosition):
        pass

class NoMovement(MovementStrategy):

    def __init__(self, sprite, level, tilePoints, player):
        MovementStrategy.__init__(self, sprite, level, tilePoints)
        
    def getMovement(self, currentPosition):
        return 0, 0, NO_METADATA
        
class RobotMovement(MovementStrategy):
    
    def __init__(self, sprite, level, tilePoints, player):
        MovementStrategy.__init__(self, sprite, level, tilePoints)
        self.pathPoints = []
        for tilePoint in tilePoints:
            self.pathPoints.append((tilePoint[0] * TILE_SIZE + sprite.position[0],
                                    tilePoint[1] * TILE_SIZE + sprite.position[1]))
        self.numPoints = len(tilePoints)
        self.currentPathPoint = self.pathPoints[0]
        self.pathPointIndex = 0
            
    def getMovement(self, currentPosition):
        x = self.currentPathPoint[0] - currentPosition[0]
        y = self.currentPathPoint[1] - currentPosition[1]
        if x == 0 and y == 0:
            self.pathPointIndex = (self.pathPointIndex + 1) % self.numPoints
            self.currentPathPoint = self.pathPoints[self.pathPointIndex]
            x = self.currentPathPoint[0] - currentPosition[0]
            y = self.currentPathPoint[1] - currentPosition[1]
        px, py, metadata = 0, 0, NO_METADATA
        if x > 0:
            px, metadata = 1 * SCALAR, RIGHT_METADATA
        elif x < 0:
            px, metadata = -1 * SCALAR, LEFT_METADATA
        if y > 0:
            py, metadata = 1 * SCALAR, DOWN_METADATA
        elif y < 0:
            py, metadata = -1 * SCALAR, UP_METADATA
        return px, py, metadata

class ZoomMovement(MovementStrategy):
    
    def __init__(self, sprite, level, tilePoints, player):
        MovementStrategy.__init__(self, sprite, level, tilePoints)
        self.player = player
        spriteRect = self.sprite.baseRect
        self.upRect = Rect(spriteRect.left, spriteRect.top - VIEW_HEIGHT, spriteRect.width, VIEW_HEIGHT)
        self.downRect = Rect(spriteRect.left, spriteRect.bottom, spriteRect.width, VIEW_HEIGHT)
        self.leftRect = Rect(spriteRect.left - VIEW_WIDTH, spriteRect.top, VIEW_WIDTH, spriteRect.height)
        self.rightRect = Rect(spriteRect.right, spriteRect.top, VIEW_WIDTH, spriteRect.height)
        self.countdown = 8;
        self.direction = None # this is also used to detect if the sprite has 'seen' the player
    
    def getMovement(self, currentPosition):
        if self.countdown == 0:
            print "zooming"
            return ZOOM_MOVEMENT[self.direction]
        if self.sprite.inView and self.level == self.player.level and not self.direction:
            metadata = NO_METADATA
            if self.leftRect.colliderect(self.player.baseRect):
                self.direction, metadata = LEFT, LEFT_METADATA
            elif self.rightRect.colliderect(self.player.baseRect):
                self.direction, metadata = RIGHT, RIGHT_METADATA
            elif self.upRect.colliderect(self.player.baseRect):
                self.direction, metadata = UP, UP_METADATA
            elif self.downRect.colliderect(self.player.baseRect):
                self.direction, metadata = DOWN, DOWN_METADATA
            return 0, 0, metadata
        if self.direction:
            self.countdown -= 1
        return 0, 0, NO_METADATA
        