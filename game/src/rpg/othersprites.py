#!/usr/bin/env python

from sprites import *
from spriteframes import DirectionalFrames, DIRECTION
from view import UP, DOWN, LEFT, RIGHT, VIEW_WIDTH, VIEW_HEIGHT

"""
Metadata is used to provide a loose coupling between the sprite movement and
the sprite frames.  Anything the sprite frames might be interested in, eg. the
direction, can be passed through.
""" 
UP_METADATA = {DIRECTION: UP}
DOWN_METADATA = {DIRECTION: DOWN}
LEFT_METADATA = {DIRECTION: LEFT}
RIGHT_METADATA = {DIRECTION: RIGHT}

MOVEMENT = {UP: (0, -MOVE_UNIT, UP_METADATA),
            DOWN: (0, MOVE_UNIT, DOWN_METADATA),
            LEFT: (-MOVE_UNIT, 0, LEFT_METADATA),
            RIGHT: (MOVE_UNIT, 0, RIGHT_METADATA)}

ZOOM_MOVEMENT = {UP: (0, -2 * MOVE_UNIT, UP_METADATA),
                 DOWN: (0, 2 * MOVE_UNIT, DOWN_METADATA),
                 LEFT: (-2 * MOVE_UNIT, 0, LEFT_METADATA),
                 RIGHT: (2 * MOVE_UNIT, 0, RIGHT_METADATA)}

waspSoundPath = os.path.join(SOUNDS_FOLDER, "wasp.wav")
waspSound = pygame.mixer.Sound(waspSoundPath)

class Beetle(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (9 * SCALAR, 12 * SCALAR)    

    def __init__(self, rpgMap):
        if Beetle.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "beetle-frames.png")
            Beetle.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processMovementFrames(Beetle.framesImage, 2)
        spriteFrames = DirectionalFrames(animationFrames, 12)
        OtherSprite.__init__(self, rpgMap, spriteFrames)

    def processCollision(self, player):
        print "life lost!"
        player.loseLife()
        return True
    
    # initialises a 'robot' movement strategy - moving along the given list of tiles
    def initMovement(self, level, tilePoints, player):
        OtherSprite.initMovement(self, level, tilePoints, player)
        self.pathPoints = []
        for tilePoint in tilePoints:
            self.pathPoints.append((tilePoint[0] * TILE_SIZE + self.position[0],
                                    tilePoint[1] * TILE_SIZE + self.position[1]))
        self.numPoints = len(tilePoints)
        self.currentPathPoint = self.pathPoints[0]
        self.pathPointIndex = 0
            
    def getMovement(self):
        currentPosition = self.mapRect.topleft
        x = self.currentPathPoint[0] - currentPosition[0]
        y = self.currentPathPoint[1] - currentPosition[1]
        if x == 0 and y == 0:
            self.pathPointIndex = (self.pathPointIndex + 1) % self.numPoints
            self.currentPathPoint = self.pathPoints[self.pathPointIndex]
            x = self.currentPathPoint[0] - currentPosition[0]
            y = self.currentPathPoint[1] - currentPosition[1]
        if x < 0:
            return MOVEMENT[LEFT]
        if x > 0:
            return MOVEMENT[RIGHT]
        if y < 0:
            return MOVEMENT[UP]
        if y > 0:
            return MOVEMENT[DOWN]
        # otherwise there is nowhere to move to
        return NO_MOVEMENT

class Wasp(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (9 * SCALAR, 12 * SCALAR)    

    def __init__(self, rpgMap):
        if Wasp.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "wasp-frames.png")
            Wasp.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processMovementFrames(Wasp.framesImage, 2)
        spriteFrames = DirectionalFrames(animationFrames, 4)
        OtherSprite.__init__(self, rpgMap, spriteFrames)
        
    def processCollision(self, player):
        print "life lost!"
        player.loseLife()
        return True
    
    # initialises a 'zoom' movement strategy - zooming towards the player vertically/horizontally
    def initMovement(self, level, tilePoints, player):
        OtherSprite.initMovement(self, level, tilePoints, player)
        self.upRect = Rect(self.baseRect.left, self.baseRect.top - VIEW_HEIGHT, self.baseRect.width, VIEW_HEIGHT)
        self.downRect = Rect(self.baseRect.left, self.baseRect.bottom, self.baseRect.width, VIEW_HEIGHT)
        self.leftRect = Rect(self.baseRect.left - VIEW_WIDTH, self.baseRect.top, VIEW_WIDTH, self.baseRect.height)
        self.rightRect = Rect(self.baseRect.right, self.baseRect.top, VIEW_WIDTH, self.baseRect.height)
        self.countdown = 8;
        self.zooming = False
        self.direction = None # this is also used to detect if the sprite has 'seen' the player
    
    def getMovement(self):
        if self.zooming:
            print "zooming"
            return ZOOM_MOVEMENT[self.direction]
        if self.inView and self.level == self.player.level and not self.direction:
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
        # if direction is set, the sprite has 'seen' the player - countdown begins
        if self.direction:
            self.countdown -= 1
            if self.countdown == 0:
                self.zooming = True
                waspSound.play()
        return NO_MOVEMENT
    