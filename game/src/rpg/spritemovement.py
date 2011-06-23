#!/usr/bin/env python

from view import NONE, UP, DOWN, LEFT, RIGHT, SCALAR, TILE_SIZE, VIEW_WIDTH, VIEW_HEIGHT

from pygame.locals import Rect

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
        # self.state = "waiting"
        spriteRect = self.sprite.baseRect
        self.upRect = Rect(spriteRect.left, spriteRect.top - VIEW_HEIGHT, spriteRect.width, VIEW_HEIGHT)
        self.downRect = Rect(spriteRect.left, spriteRect.bottom, spriteRect.width, VIEW_HEIGHT)
        self.leftRect = Rect(spriteRect.left - VIEW_WIDTH, spriteRect.top, VIEW_WIDTH, spriteRect.height)
        self.rightRect = Rect(spriteRect.right, spriteRect.top, VIEW_WIDTH, spriteRect.height)
    
    def getMovement(self, currentPosition):
        if self.level == self.player.level:
            if self.leftRect.colliderect(self.player.baseRect):
                return 0, 0, LEFT
            if self.rightRect.colliderect(self.player.baseRect):
                return 0, 0, RIGHT
            if self.upRect.colliderect(self.player.baseRect):
                return 0, 0, UP
            if self.downRect.colliderect(self.player.baseRect):
                return 0, 0, DOWN
        return 0, 0, NONE
        