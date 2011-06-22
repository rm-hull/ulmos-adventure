#!/usr/bin/env python

from view import SCALAR, TILE_SIZE, NONE, UP, DOWN, LEFT, RIGHT

class MovementStrategy:
    
    def __init__(self, level, tilePoints):
        self.level = level
        self.tilePoints = tilePoints
        
    def getInitialTilePosition(self):
        return self.tilePoints[0][0], self.tilePoints[0][1], self.level

    def getMovement(self, currentPosition):
        pass

class NoMovement(MovementStrategy):

    def __init__(self, level, tilePoints, position = (0, 0)):
        MovementStrategy.__init__(self, level, tilePoints)
        
    def getMovement(self, currentPosition):
        return 0, 0, NONE
        
class RobotMovement(MovementStrategy):
    
    def __init__(self, level, tilePoints, position = (0, 0)):
        MovementStrategy.__init__(self, level, tilePoints)
        self.pathPoints = []
        for tilePoint in tilePoints:
            self.pathPoints.append((tilePoint[0] * TILE_SIZE + position[0],
                                    tilePoint[1] * TILE_SIZE + position[1]))
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

    def __init__(self, level, tilePoints, position = (0, 0)):
        MovementStrategy.__init__(self, level, tilePoints)
    
    def getMovement(self, currentPosition):
        return 0, 0, NONE
        