#! /usr/bin/env python

from pygame.locals import *

from view import NONE, UP, DOWN, LEFT, RIGHT, TILE_SIZE, VIEW_WIDTH, VIEW_HEIGHT
from sprites import MOVE_UNIT
from events import DUMMY_EVENT, TRANSITION_EVENT, BOUNDARY_EVENT

import pygame
import parser
import sprites
import fixedsprites
import player
import view
import registry
import spritebuilder

ORIGIN = (0, 0)
X_MULT = VIEW_WIDTH // 64
Y_MULT = VIEW_HEIGHT // 64
DIMENSIONS = (VIEW_WIDTH, VIEW_HEIGHT)

# number of frames required to bring the player into view from an off-screen position
TICK_TARGETS = {UP: 24, DOWN: 24, LEFT: 14, RIGHT: 14}

# initialise pygame
pygame.init()
screen = pygame.display.set_mode(DIMENSIONS)

# create fixed sprites
fixedSprites = pygame.sprite.Group()
fixedCoin = fixedsprites.FixedCoin((3, 3))
coinCount = fixedsprites.CoinCount(0, (14, 3))
keyCount = fixedsprites.KeyCount(0, (VIEW_WIDTH - 3, 3))
fixedSprites.add(fixedCoin, coinCount, keyCount)

# create registry
registry = registry.Registry()

# create player
player = player.Ulmo(registry)
player.coinCount = coinCount
player.keyCount = keyCount

def startGame():
    # create the map
    player.rpgMap = parser.loadRpgMap("start")
    # set the start position
    player.setPosition(30, 5, 3)
    # return the play state
    return PlayState()

class PlayState:
    
    def __init__(self):
        # must set the player map + position before we create this state
        self.rpgMap = player.rpgMap
        self.viewRect = player.getViewRect()
        # add the player to the visible group
        self.visibleSprites = sprites.RpgSprites(player)
        # create more sprites
        self.gameSprites = spritebuilder.createSpritesForMap(self.rpgMap, registry)
             
    def execute(self, keyPresses):
        # have we triggered any events?
        eventState = self.handleEvents()
        if eventState:
            return eventState
        # have we collided with any sprites
        self.handleSpriteCollisions()
        directionBits = NONE
        action = False
        if keyPresses[K_UP]:
            directionBits += UP
        if keyPresses[K_DOWN]:
            directionBits += DOWN
        if keyPresses[K_LEFT]:
            directionBits += LEFT
        if keyPresses[K_RIGHT]:
            directionBits += RIGHT
        if keyPresses[K_SPACE]:
            action = True
        # handle movement + check for boundaries/transitions
        nextState = self.handleMovement(directionBits)
        if nextState:
            return nextState
        # handle actions
        self.handleAction(action)
        # draw the map view to the screen
        self.drawMapView(screen)
        pygame.display.flip()
        return None
        
    def handleEvents(self):
        event = player.processEvents()
        if event and event.type > DUMMY_EVENT:
            return TransitionState(event)
        return None
    
    def handleSpriteCollisions(self):
        # have we collided with any sprites?
        player.processCollisions(self.visibleSprites.sprites())
    
    def handleMovement(self, directionBits):
        if directionBits > 0:
            event, self.viewRect = player.handleMovement(directionBits)
            if event:
                # we've hit a boundary - change states to swap the map
                print "event %s" % event
                if event.type == BOUNDARY_EVENT:
                    return BoundaryState(event)
                if event.type == TRANSITION_EVENT:
                    return TransitionState(event)
        return None
    
    def handleAction(self, action):
        if action:
            player.handleAction(self.visibleSprites.sprites())
    
    def drawMapView(self, surface, increment = 1):
        surface.blit(self.rpgMap.getMapView(self.viewRect), ORIGIN)
        # if the sprite being updated is visible in the view it will be added to
        # the visibleSprites group as a side-effect
        self.gameSprites.update(self.viewRect, self.gameSprites, self.visibleSprites, increment)
        self.visibleSprites.draw(surface)
        if increment:
            fixedSprites.draw(surface)
    
    # method required by the ShowPlayer state
    def showPlayer(self, px, py):
        player.applyMovement(player.level,
                             player.direction,
                             px, py)
        self.viewRect = player.getViewRect()
        self.drawMapView(screen, 0)
                        
class TransitionState:
    
    tickTargets = {UP: 16, DOWN: 16, LEFT: 16, RIGHT: 16}
    
    def __init__(self, transitionEvent):
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
                                                  VIEW_WIDTH - xBorder * 2,
                                                  VIEW_HEIGHT - yBorder * 2)
            screen.blit(extract, (xBorder, yBorder))
            pygame.display.flip()
        elif self.ticks == 32:
            # load another map
            nextRpgMap = parser.loadRpgMap(self.event.mapName)
            player.rpgMap = nextRpgMap
            # set player position
            if self.event.direction:
                player.setDirection(self.event.direction)
            player.setPosition(self.event.mapPosition[0],
                                    self.event.mapPosition[1],
                                    self.event.mapLevel)
            if self.event.boundary:
                self.hidePlayer(nextRpgMap.mapRect)
            # create play state
            self.nextState = PlayState()
            # extract the next image from the state
            self.nextState.drawMapView(self.screenImage, 0)           
        elif self.ticks < 64:
            xBorder, yBorder = (64 - self.ticks) * X_MULT, (64 - self.ticks) * Y_MULT
            extract = self.screenImage.subsurface(xBorder, yBorder,
                                                  VIEW_WIDTH - xBorder * 2,
                                                  VIEW_HEIGHT - yBorder * 2)
            screen.blit(extract, (xBorder, yBorder))
            pygame.display.flip()
        else:
            if self.event.boundary:
                return ShowPlayerState(player.direction, self.nextState)
            return ShowPlayerState(player.direction, self.nextState, self.tickTargets)
            # return self.nextState
        self.ticks += 1
        return None

    def hidePlayer(self, mapRect):
        playerRect = player.mapRect
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
        player.resetPosition(px, py)

class BoundaryState:
    
    def __init__(self, boundaryEvent):
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
            player.rpgMap = nextRpgMap
            # set the new position
            self.setPlayerPosition(nextRpgMap.mapRect, self.modifier)
            # create play state
            self.nextState = PlayState()
            # extract the next image from the state
            self.nextState.drawMapView(self.nextImage, 0)
        elif self.ticks < 32:
            xSlice, ySlice = self.ticks * X_MULT * 2, self.ticks * Y_MULT * 2
            if self.boundary == UP:
                screen.blit(self.oldImage.subsurface(0, 0, VIEW_WIDTH, VIEW_HEIGHT - ySlice), (0, ySlice))
                screen.blit(self.nextImage.subsurface(0, VIEW_HEIGHT - ySlice, VIEW_WIDTH, ySlice), ORIGIN)                
            elif self.boundary == DOWN:
                screen.blit(self.oldImage.subsurface(0, ySlice, VIEW_WIDTH, VIEW_HEIGHT - ySlice), ORIGIN)
                screen.blit(self.nextImage.subsurface(0, 0, VIEW_WIDTH, ySlice), (0, VIEW_HEIGHT - ySlice))                
            elif self.boundary == LEFT:
                screen.blit(self.oldImage.subsurface(0, 0, VIEW_WIDTH - xSlice, VIEW_HEIGHT), (xSlice, 0))
                screen.blit(self.nextImage.subsurface(VIEW_WIDTH - xSlice, 0, xSlice, VIEW_HEIGHT), ORIGIN)                
            else: # self.boundary == RIGHT
                screen.blit(self.oldImage.subsurface(xSlice, 0, VIEW_WIDTH - xSlice, VIEW_HEIGHT), ORIGIN)
                screen.blit(self.nextImage.subsurface(0, 0, xSlice, VIEW_HEIGHT), (VIEW_WIDTH - xSlice, 0))                
            pygame.display.flip()
        else:
            return ShowPlayerState(self.boundary, self.nextState)
            # return self.nextState
        self.ticks += 1
        return None
        
    def setPlayerPosition(self, mapRect, modifier):
        playerRect = player.mapRect
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
        player.resetPosition(px, py)

class ShowPlayerState:
    
    def __init__(self, boundary, nextState, tickTargets = TICK_TARGETS):
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
