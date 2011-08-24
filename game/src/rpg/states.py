#! /usr/bin/env python

from pygame.locals import *

from events import SCENE_TRANSITION, REPLAY_TRANSITION, BOUNDARY_TRANSITION, GAME_OVER_TRANSITION
from view import NONE, UP, DOWN, LEFT, RIGHT, TILE_SIZE, VIEW_WIDTH, VIEW_HEIGHT
from sprites import MOVE_UNIT

from fixedsprites import FixedCoin, CoinCount, KeyCount, Lives
from registry import Registry
from player import Ulmo

import pygame
import parser
import sprites
import view
import spritebuilder
import events
import font

ORIGIN = (0, 0)
X_MULT = VIEW_WIDTH // 64
Y_MULT = VIEW_HEIGHT // 64
DIMENSIONS = (VIEW_WIDTH, VIEW_HEIGHT)

# number of frames required to bring the player into view from an off-screen position
BOUNDARY_TICKS = {UP: 24, DOWN: 24, LEFT: 14, RIGHT: 14}
DOORWAY_TICKS = {UP: 16, DOWN: 16, LEFT: 16, RIGHT: 16}

screen = pygame.display.set_mode(DIMENSIONS)

fixedSprites = None
player = None
registry = None

def startGame():
    # create fixed sprites
    global fixedSprites
    fixedSprites = pygame.sprite.Group()
    fixedCoin = FixedCoin((27, 3))
    coinCount = CoinCount(0, (38, 3))
    keyCount = KeyCount(0, (VIEW_WIDTH - 3, 3))
    lives = Lives(2, (3, 3))
    fixedSprites.add(fixedCoin, lives, coinCount, keyCount)
    
    # create player
    global player
    player = Ulmo()
    player.coinCount = coinCount
    player.keyCount = keyCount
    player.lives = lives
    # create the map
    player.rpgMap = parser.loadRpgMap("central")
    # set the start position
    player.setTilePosition(30, 21, 3)
    #player.setTilePosition(6, 22, 2)

    # create registry
    global registry
    registry = Registry()
    
    # return the play state
    return PlayState()

def hidePlayer(boundary, mapRect, modifier = None):
    playerRect = player.mapRect
    px, py = playerRect.topleft
    if modifier:
        px, py = [i + modifier * TILE_SIZE for i in playerRect.topleft]
    # we position the player just off the screen and then use the ShowPlayer
    # state to bring the player into view                 
    if boundary == UP:
        py = mapRect.bottom
    elif boundary == DOWN:
        py = 0 - playerRect.height
    elif boundary == LEFT:
        px = mapRect.right
    else: # boundary == RIGHT
        px = 0 - playerRect.width             
    player.setPixelPosition(px, py)

class PlayState:
    
    def __init__(self, lastTransition = None):
        # we need this if the player loses a life
        self.lastTransition = lastTransition
        if lastTransition == None:
            self.lastTransition = self.createReplayTransition()
        # must set the player map + position before we create this state
        player.updateViewRect()
        # add the player to the visible group
        self.visibleSprites = sprites.RpgSprites(player)
        # create more sprites
        self.gameSprites = spritebuilder.createSpritesForMap(player.rpgMap, registry)
             
    def execute(self, keyPresses):
        transition = self.getNextTransition(keyPresses)
        if transition:
            print "transition: %s" % transition.__class__.__name__
            if transition.type == BOUNDARY_TRANSITION:
                return BoundaryTransitionState(transition)
            if transition.type == SCENE_TRANSITION:
                return SceneTransitionState(transition)
            if transition.type == REPLAY_TRANSITION:
                return SceneTransitionState(transition)
            if transition.type == GAME_OVER_TRANSITION:
                return GameOverState(transition)
        # draw the map view to the screen
        self.drawMapView(screen)
        pygame.display.flip()
        return None
    
    def getNextTransition(self, keyPresses):
        # have we triggered any events?
        transition = self.handleEvents()
        if transition:
            return transition
        # have we collided with any sprites?
        transition = self.handleCollisions()
        if transition:
            return transition
        # have we hit any boundaries?
        transition = self.handleInput(keyPresses)
        if transition:
            return transition
        return None
            
    def handleEvents(self):
        event = player.processEvents()
        if event:
            return event.transition
        return None
    
    def handleCollisions(self):
        # the processCollision method returns True to indicate that the player lost a life
        if player.processCollisions(self.visibleSprites.sprites()):
            if player.gameOver():
                return events.GameOverTransition()
            return self.lastTransition
        return None
    
    def handleInput(self, keyPresses):
        directionBits, action = self.processKeyPresses(keyPresses)
        if directionBits > 0:
            self.viewRect = player.handleMovement(directionBits)
            boundaryEvent = player.getBoundaryEvent()
            if boundaryEvent:
                # we've hit a boundary - return the associated transition
                return boundaryEvent.transition
        if action:
            player.handleAction(self.visibleSprites.sprites())
        return None
    
    def processKeyPresses(self, keyPresses):
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
        return directionBits, action
    
    def drawMapView(self, surface, increment = 1):
        surface.blit(player.getMapView(), ORIGIN)
        # if the sprite being updated is in view it will be added to visibleSprites as a side-effect
        self.gameSprites.update(player, self.gameSprites, self.visibleSprites, increment)
        self.visibleSprites.draw(surface)
        if increment:
            fixedSprites.draw(surface)
    
    def createReplayTransition(self):
        transition = events.ReplayTransition(player.rpgMap.name,
                                             player.mapRect.left,
                                             player.mapRect.top,
                                             player.level,
                                             player.spriteFrames.direction)
        transition.firstMap = True
        return transition
        
    # method required by the ShowPlayer state
    def showPlayer(self, px, py):
        player.wrapMovement(player.level,
                            player.spriteFrames.direction,
                            px, py)
        self.drawMapView(screen, 0)

class SceneTransitionState:
    
    def __init__(self, transition):
        self.transition = transition
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
            # load the next map
            nextRpgMap = parser.loadRpgMap(self.transition.mapName)
            player.rpgMap = nextRpgMap
            # set player position
            if self.transition.type == REPLAY_TRANSITION:
                player.setPixelPosition(self.transition.pixelPosition[0],
                                        self.transition.pixelPosition[1],
                                        self.transition.level)
                # player is already hidden
            else: # self.transition.type == SCENE_TRANSITION    
                player.setTilePosition(self.transition.tilePosition[0],
                                       self.transition.tilePosition[1],
                                       self.transition.level)
                if self.transition.boundary:
                    hidePlayer(self.transition.boundary, nextRpgMap.mapRect)
            # setting the direction will also apply masks
            player.setDirection(self.transition.direction)
            # create play state
            self.nextState = PlayState(self.transition)
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
            if self.transition.firstMap:
                return self.nextState
            direction = player.spriteFrames.direction
            if self.transition.boundary:
                return ShowPlayerState(direction, self.nextState, BOUNDARY_TICKS[direction])
            return ShowPlayerState(direction, self.nextState, DOORWAY_TICKS[direction])
        self.ticks += 1
        return None

class BoundaryTransitionState:
    
    def __init__(self, transition):
        self.transition = transition
        self.boundary = transition.boundary
        self.nextImage = view.createRectangle(DIMENSIONS)
        self.nextState = None
        self.ticks = 0
                     
    def execute(self, keyPresses):
        if self.ticks == 0:
            self.oldImage = screen.copy()
            # load another map
            nextRpgMap = parser.loadRpgMap(self.transition.mapName)
            player.rpgMap = nextRpgMap
            player.spriteFrames.direction = self.boundary
            # set the new position
            hidePlayer(self.boundary, nextRpgMap.mapRect, self.transition.modifier)
            # create play state
            self.nextState = PlayState(self.createReplayTransition())
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
            return ShowPlayerState(self.boundary, self.nextState, BOUNDARY_TICKS[self.boundary])
            # return self.nextState
        self.ticks += 1
        return None
    
    def createReplayTransition(self):
        return events.ReplayTransition(self.transition.mapName,
                                       player.mapRect.left,
                                       player.mapRect.top,
                                       player.level,
                                       player.spriteFrames.direction,
                                       self.boundary)

class GameOverState:
    
    def __init__(self, transition):
        self.transition = transition
        self.screenImage = screen.copy()
        self.blackRect = view.createRectangle(DIMENSIONS)
        self.nextState = None
        self.ticks = 0
        gameFont = font.GameFont()
        self.topLine1 = gameFont.getTextImage("BRAVE ADVENTURER")
        self.topLine2 = gameFont.getTextImage("YOU ARE DEAD")
        self.lowLine1 = gameFont.getTextImage("PRESS ANY KEY")
        self.lowLine2 = gameFont.getTextImage("TO PLAY AGAIN")
             
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
            x, y = (VIEW_WIDTH - self.topLine1.get_width()) // 2, 32 * view.SCALAR
            screen.blit(self.topLine1, (x, y))
            x, y = (VIEW_WIDTH - self.topLine2.get_width()) // 2, 44 * view.SCALAR
            screen.blit(self.topLine2, (x, y))
            pygame.display.flip()
        elif self.ticks == 64:
            x, y = (VIEW_WIDTH - self.lowLine1.get_width()) // 2, VIEW_HEIGHT - 42 * view.SCALAR
            screen.blit(self.lowLine1, (x, y))
            x, y = (VIEW_WIDTH - self.lowLine2.get_width()) // 2, VIEW_HEIGHT - 30 * view.SCALAR
            screen.blit(self.lowLine2, (x, y))
            pygame.display.flip()
        elif self.ticks > 64:
            keysPressed = [key for key in keyPresses if key]
            if len(keysPressed) > 0:
                return startGame()
        self.ticks += 1
        
class ShowPlayerState:
    
    def __init__(self, boundary, nextState, tickTarget):
        self.boundary = boundary
        self.nextState = nextState
        self.tickTarget = tickTarget
        self.ticks = 0
        
    def execute(self, keyPresses):
        if self.ticks > self.tickTarget:
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
