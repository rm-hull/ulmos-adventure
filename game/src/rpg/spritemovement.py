#!/usr/bin/env python

from view import NONE, UP, DOWN, LEFT, RIGHT, SCALAR, TILE_SIZE, VIEW_WIDTH, VIEW_HEIGHT

from pygame.locals import Rect

ZOOM_MOVEMENT = {UP: (0, -2 * SCALAR, UP),
                 DOWN: (0, 2 * SCALAR, DOWN),
                 LEFT: (-2 * SCALAR, 0, LEFT),
                 RIGHT: (2 * SCALAR, 0, RIGHT) }

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
        return 0, 0, NONE
        
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
        px, py, direction = 0, 0, NONE
        if x > 0:
            px, direction = 1 * SCALAR, RIGHT
        elif x < 0:
            px, direction = -1 * SCALAR, LEFT
        if y > 0:
            py, direction = 1 * SCALAR, DOWN
        elif y < 0:
            py, direction = -1 * SCALAR, UP
        return px, py, direction

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
        self.direction = NONE
    
    def getMovement(self, currentPosition):
        if self.countdown == 0:
            print "zooming"
            return ZOOM_MOVEMENT[self.direction]
        if self.sprite.inView and self.direction == NONE and self.level == self.player.level:
            if self.leftRect.colliderect(self.player.baseRect):
                self.direction = LEFT
            if self.rightRect.colliderect(self.player.baseRect):
                self.direction = RIGHT
            if self.upRect.colliderect(self.player.baseRect):
                self.direction = UP
            if self.downRect.colliderect(self.player.baseRect):
                self.direction = DOWN
            return 0, 0, self.direction
        if self.direction != NONE:
            self.countdown -= 1
        return 0, 0, NONE
        