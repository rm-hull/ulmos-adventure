#! /usr/bin/env python

from pygame.locals import *

from view import UP, DOWN, LEFT, RIGHT, SCALAR
from rpg.view import TILE_SIZE

import pygame
import rpg.parser as parser
import rpg.sprites as sprites
import rpg.mapinfo as mapinfo
import rpg.spriteinfo as spriteinfo

ORIGIN = (0, 0)

# initialise
pygame.init()
screen = pygame.display.set_mode((256, 192))

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
        directionBits, boundary = 0, sprites.NO_BOUNDARY
        if keyPresses[K_UP]:
            directionBits += UP
        if keyPresses[K_DOWN]:
            directionBits += DOWN
        if keyPresses[K_LEFT]:
            directionBits += LEFT
        if keyPresses[K_RIGHT]:
            directionBits += RIGHT
        if directionBits > 0:
            boundary, self.viewRect = self.player.move(directionBits)
        if boundary > sprites.NO_BOUNDARY:
            # we've hit a boundary - change states to swap the map
            print "boundary %s" % boundary
            return BoundaryState(self.player, self.rpgMap.name, boundary)
        # update
        screen.blit(self.rpgMap.getMapView(self.viewRect), ORIGIN)
        # if the sprite being updated is visible in the view it will be added to
        # the visibleSprites group as a side-effect 
        self.gameSprites.update(self.viewRect, self.visibleSprites)
        toRemove = self.player.processCollisions(self.visibleSprites.sprites())
        if len(toRemove) > 0:
            self.gameSprites.remove(toRemove)
            self.visibleSprites.remove(toRemove)
        self.visibleSprites.draw(screen)
        pygame.display.flip()
        
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
        