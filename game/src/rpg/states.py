#! /usr/bin/env python

from pygame.locals import *

from view import NONE, UP, DOWN, LEFT, RIGHT, SCALAR, TILE_SIZE
from sprites import MOVE_UNIT
from eventinfo import DUMMY_EVENT, TRANSITION_EVENT, BOUNDARY_EVENT

import pygame
import parser
import sprites
import view
import spriteinfo

ORIGIN = (0, 0)
#WIDTH = 256
#HEIGHT = 192
WIDTH = 384
HEIGHT = 256
X_MULT = WIDTH // 64
Y_MULT = HEIGHT // 64
DIMENSIONS = (WIDTH, HEIGHT)

# number of frames required to bring the player into view
# from an off-screen position
TICK_TARGETS = {UP: 24, DOWN: 24, LEFT: 14, RIGHT: 14}

# initialise
pygame.init()
screen = pygame.display.set_mode(DIMENSIONS)

"""def startGame():
    # create the map
    rpgMap = parser.loadRpgMap("demo")
    # rpgMap = parser.loadRpgMap("islands")
    # create the player sprite
    player = sprites.Ulmo(rpgMap)
    player.setPosition(1, 0, 1)
    # player.setPosition(2, 11, 2)
    # player.setPosition(12, 3, 1)
    return PlayState(player)"""

def startGame():
    # create the map
    rpgMap = parser.loadRpgMap("start")
    # create the player sprite
    player = sprites.Ulmo(rpgMap)
    # set the start position
    player.setPosition(9, 6, 2)
    # return the play state
    return PlayState(player)

class PlayState:
    
    def __init__(self, player):
        # must set position on the player before we create this state
        self.player = player
        self.rpgMap = player.rpgMap
        self.viewRect = self.player.getViewRect()
        # add the player to the visible group
        self.visibleSprites = sprites.RpgSprites(player)
        # create more sprites
        self.gameSprites = spriteinfo.getMapSprites(self.rpgMap.name)
             
    def execute(self, keyPresses):
        # have we triggered any events?
        eventState = self.handleEvents()
        if eventState:
            return eventState
        # have we collided with any sprites
        self.handleSpriteCollisions()
        directionBits = NONE
        if keyPresses[K_UP]:
            directionBits += UP
        if keyPresses[K_DOWN]:
            directionBits += DOWN
        if keyPresses[K_LEFT]:
            directionBits += LEFT
        if keyPresses[K_RIGHT]:
            directionBits += RIGHT
        # handle movement + check for boundaries
        boundaryState = self.handleMovement(directionBits)
        if boundaryState:
            return boundaryState
        # draw the map view to the screen
        self.drawMapView(screen)
        pygame.display.flip()
        return None
        
    def handleEvents(self):
        event = self.player.processEvents()
        if event and event.type > DUMMY_EVENT:
            return TransitionState(self.player, event)
        return None
    
    def handleSpriteCollisions(self):
        # have we collided with any sprites?
        toRemove = self.player.processCollisions(self.visibleSprites.sprites())
        if len(toRemove) > 0:
            self.gameSprites.remove(toRemove)
            self.visibleSprites.remove(toRemove)
    
    def handleMovement(self, directionBits):
        if directionBits > 0:
            event, self.viewRect = self.player.move(directionBits)
            if event:
                # we've hit a boundary - change states to swap the map
                print "event %s" % event
                if event.type == BOUNDARY_EVENT:
                    return BoundaryState(self.player, event)
                if event.type == TRANSITION_EVENT:
                    return TransitionState(self.player, event)
        return None
    
    def drawMapView(self, surface, increment = 1):
        surface.blit(self.rpgMap.getMapView(self.viewRect), ORIGIN)
        # if the sprite being updated is visible in the view it will be added to
        # the visibleSprites group as a side-effect 
        self.gameSprites.update(self.viewRect, self.visibleSprites, increment)
        self.visibleSprites.draw(surface)
    
    # method required by the ShowPlayer state
    def showPlayer(self, px, py):
        self.player.applyMovement(self.player.level,
                                  self.player.direction,
                                  px, py)
        self.viewRect = self.player.getViewRect()
        self.drawMapView(screen, 0)
                        
class TransitionState:
    
    tickTargets = {UP: 16, DOWN: 16, LEFT: 16, RIGHT: 16}
    
    def __init__(self, player, transitionEvent):
        self.player = player
        self.event = transitionEvent
        self.screenImage = screen.copy()
        self.blackRect = view.createRectangle(DIMENSIONS)
        self.nextState = None
        self.ticks = 0
             
    def execute(self, keyPresses):
        if self.ticks < 32:
            xBorder, yBorder = (self.ticks + 1) * X_MULT, (self.ticks + 1) * Y_MULT
            screen.blit(self.blackRect, ORIGIN)
            extract = self.screenImage.subsurface(xBorder, yBorder,
                                                  WIDTH - xBorder * 2,
                                                  HEIGHT - yBorder * 2)
            screen.blit(extract, (xBorder, yBorder))
            pygame.display.flip()
        elif self.ticks == 32:
            # load another map
            nextRpgMap = parser.loadRpgMap(self.event.mapName)
            self.player.rpgMap = nextRpgMap
            # set player position
            if self.event.direction:
                self.player.setDirection(self.event.direction)
            self.player.setPosition(self.event.mapPosition[0],
                                    self.event.mapPosition[1],
                                    self.event.mapLevel)
            if self.event.boundary:
                self.hidePlayer(nextRpgMap.mapRect)
            # create play state
            self.nextState = PlayState(self.player)
            # extract the next image from the state
            self.nextState.drawMapView(self.screenImage, 0)           
        elif self.ticks < 64:
            xBorder, yBorder = (64 - self.ticks) * X_MULT, (64 - self.ticks) * Y_MULT
            extract = self.screenImage.subsurface(xBorder, yBorder,
                                                  WIDTH - xBorder * 2,
                                                  HEIGHT - yBorder * 2)
            screen.blit(extract, (xBorder, yBorder))
            pygame.display.flip()
        else:
            if self.event.boundary:
                return ShowPlayerState(self.player, self.player.direction, self.nextState)
            return ShowPlayerState(self.player, self.player.direction, self.nextState, self.tickTargets)
            # return self.nextState
        self.ticks += 1
        return None

    def hidePlayer(self, mapRect):
        playerRect = self.player.mapRect
        px, py = playerRect.topleft
        # we position the player just off the screen and then use the ShowPlayer
        # state to bring the player into view                 
        if self.event.boundary == UP:
            py = mapRect.bottom
        elif self.event.boundary == DOWN:
            py = 0 - playerRect.height
        elif self.event.boundary == LEFT:
            px = mapRect.right
        else: # self.boundary == RIGHT
            px = 0 - playerRect.width             
        self.player.resetPosition(px, py)

class BoundaryState:
    
    def __init__(self, player, boundaryEvent):
        self.player = player
        self.mapName = boundaryEvent.mapName
        self.boundary = boundaryEvent.boundary
        self.modifier = boundaryEvent.modifier
        self.nextImage = view.createRectangle(DIMENSIONS)
        self.nextState = None
        self.ticks = 0
                     
    def execute(self, keyPresses):
        if self.ticks == 0:
            self.oldImage = screen.copy()
            # load another map
            nextRpgMap = parser.loadRpgMap(self.mapName)
            self.player.rpgMap = nextRpgMap
            # set the new position
            self.setPlayerPosition(nextRpgMap.mapRect, self.modifier)
            # create play state
            self.nextState = PlayState(self.player)
            # extract the next image from the state
            self.nextState.drawMapView(self.nextImage, 0)
        elif self.ticks < 32:
            xSlice, ySlice = self.ticks * X_MULT * 2, self.ticks * Y_MULT * 2
            if self.boundary == UP:
                screen.blit(self.oldImage.subsurface(0, 0, WIDTH, HEIGHT - ySlice), (0, ySlice))
                screen.blit(self.nextImage.subsurface(0, HEIGHT - ySlice, WIDTH, ySlice), ORIGIN)                
            elif self.boundary == DOWN:
                screen.blit(self.oldImage.subsurface(0, ySlice, WIDTH, HEIGHT - ySlice), ORIGIN)
                screen.blit(self.nextImage.subsurface(0, 0, WIDTH, ySlice), (0, HEIGHT - ySlice))                
            elif self.boundary == LEFT:
                screen.blit(self.oldImage.subsurface(0, 0, WIDTH - xSlice, HEIGHT), (xSlice, 0))
                screen.blit(self.nextImage.subsurface(WIDTH - xSlice, 0, xSlice, HEIGHT), ORIGIN)                
            else: # self.boundary == RIGHT
                screen.blit(self.oldImage.subsurface(xSlice, 0, WIDTH - xSlice, HEIGHT), ORIGIN)
                screen.blit(self.nextImage.subsurface(0, 0, xSlice, HEIGHT), (WIDTH - xSlice, 0))                
            pygame.display.flip()
        else:
            return ShowPlayerState(self.player, self.boundary, self.nextState)
            # return self.nextState
        self.ticks += 1
        return None
        
    def setPlayerPosition(self, mapRect, modifier):
        playerRect = self.player.mapRect
        px, py = [i + modifier * TILE_SIZE for i in playerRect.topleft]
        # we position the player just off the screen and then use the ShowPlayer
        # state to bring the player into view                 
        if self.boundary == UP:
            py = mapRect.bottom
        elif self.boundary == DOWN:
            py = 0 - playerRect.height
        elif self.boundary == LEFT:
            px = mapRect.right
        else: # self.boundary == RIGHT
            px = 0 - playerRect.width             
        self.player.resetPosition(px, py)

class ShowPlayerState:
    
    def __init__(self, player, boundary, nextState, tickTargets = TICK_TARGETS):
        self.player = player
        self.boundary = boundary
        self.nextState = nextState
        self.tickTargets = tickTargets
        self.ticks = 0
        
    def execute(self, keyPresses):
        if self.ticks > self.tickTargets[self.boundary]:
            return self.nextState
        px, py = 0, 0
        if self.boundary == UP:
            py = -MOVE_UNIT
        elif self.boundary == DOWN:
            py = MOVE_UNIT
        elif self.boundary == LEFT:
            px = -MOVE_UNIT
        else: # self.boundary == RIGHT
            px = MOVE_UNIT
        self.nextState.showPlayer(px, py)
        pygame.display.flip()
        self.ticks += 1
        return None
