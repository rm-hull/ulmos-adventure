#! /usr/bin/env python

from pygame.locals import *

from view import NONE, UP, DOWN, LEFT, RIGHT, SCALAR, TILE_SIZE

import pygame
import parser
import sprites
import view
import mapinfo
import eventinfo
import spriteinfo

ORIGIN = (0, 0)
DIMENSIONS = (256, 192)

# initialise
pygame.init()
screen = pygame.display.set_mode(DIMENSIONS)

def startGame():
    # create the map
    # rpgMap = parser.loadRpgMap("demo")
    rpgMap = parser.loadRpgMap("islands")
    # create the player sprite
    player = sprites.Ulmo(rpgMap)
    # player.setPosition(1, 0, 1)
    player.setPosition(2, 11, 2)
    return PlayState(player, rpgMap)

class PlayState:
    
    def __init__(self, player, rpgMap):
        # must set position on the player before we create this state
        self.player = player
        self.rpgMap = rpgMap
        self.viewRect = self.player.getViewRect()
        # add the player to the visible group
        self.visibleSprites = sprites.RpgSprites(self.player)
        # create more sprites
        self.gameSprites = spriteinfo.getMapSprites(rpgMap.name)
             
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
        if event:
            print "event: %s" % event
            if event.type == eventinfo.TRANSITION_EVENT:
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
            boundary, self.viewRect = self.player.move(directionBits)
            if boundary > sprites.NO_BOUNDARY:
                # we've hit a boundary - change states to swap the map
                print "boundary %s" % boundary
                return BoundaryState(self.player, self.rpgMap.name, boundary)
        return None
    
    def drawMapView(self, surface, increment = 1):
        surface.blit(self.rpgMap.getMapView(self.viewRect), ORIGIN)
        # if the sprite being updated is visible in the view it will be added to
        # the visibleSprites group as a side-effect 
        self.gameSprites.update(self.viewRect, self.visibleSprites, increment)
        self.visibleSprites.draw(surface)
                        
class TransitionState:
    
    def __init__(self, player, transitionEvent):
        self.player = player
        self.mapName = transitionEvent.mapName
        self.mapPosition = transitionEvent.mapPosition
        self.mapLevel = transitionEvent.mapLevel
        self.nextImage = None
        self.nextState = None
        self.ticks = 0
             
    def execute(self, keyPresses):
        if self.ticks < 32:
            multiplier = self.ticks + 1
            borderView = view.createBorderView(screen, multiplier * 4, multiplier * 3)
            screen.blit(borderView, ORIGIN)
            pygame.display.flip()
        elif self.ticks == 32:
            # load another map
            nextRpgMap = parser.loadRpgMap(self.mapName)
            self.player.rpgMap = nextRpgMap
            # set the new position
            self.player.setPosition(self.mapPosition[0], self.mapPosition[1], self.mapLevel)
            # create play state
            self.nextState = PlayState(self.player, nextRpgMap)
            # extract the next image from the state
            self.nextImage = view.createRectangle(DIMENSIONS)
            self.nextState.drawMapView(self.nextImage, 0)            
        elif self.ticks < 64:
            multiplier = 64 - self.ticks
            borderView = view.createBorderView(self.nextImage, multiplier * 4, multiplier * 3)
            screen.blit(borderView, ORIGIN)
            pygame.display.flip()
        else:
            return self.nextState
        self.ticks += 1
        return None

class BoundaryState:
    
    def __init__(self, player, mapName, boundary):
        self.player = player
        self.mapName = mapName
        self.boundary = boundary
        self.ticks = 0
             
    def execute(self, keyPresses):
        self.ticks += 1
        if self.ticks > 0:
            # load another map
            nextMapName, modifier = mapinfo.getNextMap(self.mapName, self.boundary, self.player.baseRect)
            nextRpgMap = parser.loadRpgMap(nextMapName)
            self.player.rpgMap = nextRpgMap
            # set the new position
            self.setPlayerPosition(nextRpgMap.mapRect, modifier)
            # return the play state
            return PlayState(self.player, nextRpgMap)
        
    def setPlayerPosition(self, mapRect, modifier):
        playerRect = self.player.mapRect
        px, py = [i + modifier * TILE_SIZE for i in playerRect.topleft]
        if self.boundary == UP:
            py = mapRect.bottom - playerRect.height - 1 * SCALAR
        elif self.boundary == DOWN:
            py = 1 * SCALAR
        elif self.boundary == LEFT:
            px = mapRect.right - playerRect.width - 1 * SCALAR
        elif self.boundary == RIGHT:
            px = 1 * SCALAR                
        self.player.resetPosition(px, py)
        