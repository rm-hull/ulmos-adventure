#! /usr/bin/env python

import os
import pygame
import parser
import sprites
import view
import spritebuilder
import font
import playevents

from pygame.locals import K_SPACE, Rect

from sprites import VELOCITY, MOVE_UNIT
from view import UP, DOWN, LEFT, RIGHT, SCALAR, VIEW_WIDTH, VIEW_HEIGHT

from eventbus import EventBus
from registry import RegistryHandler, Registry
from player import Ulmo
from sounds import SoundHandler
from events import MapTransitionEvent, EndGameEvent
from fixedsprites import FixedCoin, CoinCount, KeyCount, Lives, CheckpointIcon
from rpg.view import TILE_SIZE

FRAMES_PER_SEC = 60 // VELOCITY

THIRTY_TWO = 32 // VELOCITY
SIXTY_FOUR = 64 // VELOCITY

ORIGIN = (0, 0)
X_MULT = VIEW_WIDTH // SIXTY_FOUR
Y_X_RATIO = float(VIEW_HEIGHT) / VIEW_WIDTH
DIMENSIONS = (VIEW_WIDTH, VIEW_HEIGHT)

# number of frames required to bring the player into view from an off-screen position
BOUNDARY_TICKS = {UP: 24 // VELOCITY,
                  DOWN: 24 // VELOCITY,
                  LEFT: 14 // VELOCITY,
                  RIGHT: 14 // VELOCITY}
DOORWAY_TICKS = {UP: 16 // VELOCITY,
                 DOWN: 16 // VELOCITY,
                 LEFT: 16 // VELOCITY,
                 RIGHT: 16 // VELOCITY}

pygame.display.set_caption("Ulmo's Adventure")
screen = pygame.display.set_mode(DIMENSIONS)

blackRect = view.createRectangle(DIMENSIONS)

gameFont = font.GameFont()
titleFont = font.TitleFont()

# globals
eventBus = None
soundHandler = None
registryHandler = None
fixedSprites = None
player = None

def showTitle():
    global eventBus
    eventBus = EventBus()

    global soundHandler
    soundHandler = SoundHandler()
    eventBus.addCoinCollectedListener(soundHandler)
    eventBus.addKeyCollectedListener(soundHandler)
    eventBus.addDoorOpeningListener(soundHandler)
    eventBus.addPlayerFootstepListener(soundHandler)
    eventBus.addMapTransitionListener(soundHandler)
    eventBus.addEndGameListener(soundHandler)
    eventBus.addLifeLostListener(soundHandler)
    eventBus.addWaspZoomingListener(soundHandler)
    eventBus.addBeetleCrawlingListener(soundHandler)
    eventBus.addCheckpointReachedListener(soundHandler)
    eventBus.addPlayerFallingListener(soundHandler)

    global registryHandler
    registryHandler = RegistryHandler()
    eventBus.addCoinCollectedListener(registryHandler)
    eventBus.addKeyCollectedListener(registryHandler)
    eventBus.addDoorOpenedListener(registryHandler)
    eventBus.addBoatStoppedListener(registryHandler)
    eventBus.addCheckpointReachedListener(registryHandler)
    
    # return the title state
    return TitleState()

def startGame(cont = False, registry = None):
    registry = getRegistry(cont, registry)
    
    # create fixed sprites
    global fixedSprites
    fixedSprites = pygame.sprite.Group()
    fixedCoin = FixedCoin((27, 3))
    coinCount = CoinCount(registry.coinCount, (38, 3))
    keyCount = KeyCount(registry.keyCount, (0, 3))
    lives = Lives(2, (3, 3))
    checkpointIcon = CheckpointIcon((-11, -11))
    fixedSprites.add(fixedCoin, lives, coinCount, keyCount, checkpointIcon)
    
    # create player
    global player
    player = Ulmo()
    player.coinCount = coinCount
    player.keyCount = keyCount
    player.lives = lives
    player.checkpointIcon = checkpointIcon
    # create the map
    rpgMap = parser.loadRpgMap(registry.mapName)
    player.setup("ulmo", rpgMap, eventBus)
    # set the start position
    player.setTilePosition(registry.playerPosition[0],
                           registry.playerPosition[1],
                           registry.playerLevel)

    # return the play state
    return PlayState()

def getRegistry(cont, registry):
    if cont:
        registryHandler.switchToSnapshot()
        return registryHandler.registry
    if not registry:
        #registry = Registry("unit", (4, 6), 1)
        #registry = Registry("central", (6, 22), 2)
        #registry = Registry("east", (13, 8), 3)
        registry = Registry("start", (6, 27), 1)
        #registry = Registry("start", (14, 7), 4)
        #registry = Registry("wasps", (12, 10), 5)
    registryHandler.setRegistry(registry)
    return registry
    
def hidePlayer(boundary, mapRect, modifier = None):
    playerRect = player.mapRect
    px, py = playerRect.topleft
    if modifier:
        px, py = [i + modifier * view.TILE_SIZE for i in playerRect.topleft]
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

def sceneZoomIn(screenImage, ticks):
    xBorder = (ticks + 1) * X_MULT
    yBorder = xBorder * Y_X_RATIO
    screen.blit(blackRect, ORIGIN)
    extract = Rect(xBorder, yBorder, VIEW_WIDTH - xBorder * 2, VIEW_HEIGHT - yBorder * 2)
    screen.blit(screenImage, (xBorder, yBorder), extract)
    pygame.display.flip()

def sceneZoomOut(screenImage, ticks):
    xBorder = (THIRTY_TWO - (ticks + 1)) * X_MULT
    yBorder = xBorder * Y_X_RATIO
    extract = Rect(xBorder, yBorder, VIEW_WIDTH - xBorder * 2, VIEW_HEIGHT - yBorder * 2)
    screen.blit(screenImage, (xBorder, yBorder), extract)
    pygame.display.flip()
    
class TitleState:
    
    def __init__(self):
        imagePath = os.path.join("images", "horizon.png")
        self.backgroundImage = view.loadScaledImage(imagePath)
        imagePath = os.path.join("images", "title.png")
        self.titleImage = view.loadScaledImage(imagePath, view.TRANSPARENT_COLOUR)
        self.playLine = titleFont.getTextImage("PRESS SPACE TO PLAY")
        self.titleTicks = self.getTitleTicks()
        self.startRegistry = Registry("start", (-2, 27), 1)
        self.playState = None
        self.ticks = 0
        
    def getTitleTicks(self):
        return (self.backgroundImage.get_height() - VIEW_HEIGHT) * 2 // SCALAR // VELOCITY
             
    def execute(self, keyPresses):
        if self.ticks < self.titleTicks:
            if (self.ticks % 2) == 0:
                x, y = 0, self.ticks * MOVE_UNIT // 2
                screen.blit(self.backgroundImage, ORIGIN, Rect(x, y, VIEW_WIDTH, VIEW_HEIGHT))        
                pygame.display.flip()
        elif self.ticks == self.titleTicks + THIRTY_TWO:
            x, y = (VIEW_WIDTH - self.titleImage.get_width()) // 2, 26 * SCALAR
            screen.blit(self.titleImage, (x, y))
            pygame.display.flip()
        elif self.ticks == self.titleTicks + SIXTY_FOUR:
            self.playState = startGame(False, self.startRegistry)
            x, y = (VIEW_WIDTH - self.playLine.get_width()) // 2, 88 * SCALAR
            screen.blit(self.playLine, (x, y))
            pygame.display.flip()
        elif self.ticks > self.titleTicks + SIXTY_FOUR:
            if keyPresses[K_SPACE]:
                return StartState(self.playState)
        self.ticks += 1

class StartState:
    
    def __init__(self, playState):
        self.screenImage = screen.copy()
        self.nextImage = view.createRectangle(DIMENSIONS)
        self.playState = playState
        self.viewRect = player.viewRect.copy()
        self.viewRect.top = 0
        self.ticks = 0
        
    def execute(self, keyPresses):
        if self.ticks < VIEW_HEIGHT // MOVE_UNIT:
            player.relativeView(self.viewRect)
            self.playState.drawMapView(self.nextImage, self.viewRect)
            self.screenWipeUp((self.ticks + 1) * MOVE_UNIT)
        else:
            self.viewRect.move_ip(0, MOVE_UNIT)
            player.relativeView(self.viewRect)
            self.playState.drawMapView(screen, self.viewRect)
            if self.viewRect.top == player.viewRect.top:
                #return self.playState
                return ShowBoatState(self.playState, (6, 27))
        pygame.display.flip()
        self.ticks += 1

    def screenWipeUp(self, sliceHeight):
        screen.blit(self.screenImage, ORIGIN, Rect(0, sliceHeight, VIEW_WIDTH, VIEW_HEIGHT - sliceHeight))
        screen.blit(self.nextImage, (0, VIEW_HEIGHT - sliceHeight), Rect(0, 0, VIEW_WIDTH, sliceHeight))
                                    
class PlayState:
    
    def __init__(self):
        # must set the player map + position before we create this state
        player.updateViewRect()
        # add the player to the visible group
        self.visibleSprites = sprites.RpgSprites(player)
        # create more sprites
        self.gameSprites = spritebuilder.createSpritesForMap(player.rpgMap, eventBus, registryHandler.registry)
             
    def execute(self, keyPresses):
        event = player.handleInteractions(keyPresses, self.gameSprites, self.visibleSprites)
        if event:
            return self.handleEvent(event)
        # draw the player map view to the screen
        self.drawPlayerMapView(screen)
        pygame.display.flip()
        
    def handleEvent(self, event):
        if event.type == playevents.LIFE_LOST_EVENT:
            if event.gameOver:
                return GameOverState()
            return SceneTransitionState(self.lifeLostTransition())
        transition = event.transition 
        if transition:
            if transition.type == playevents.BOUNDARY_TRANSITION:
                return BoundaryTransitionState(transition)
            if transition.type == playevents.SCENE_TRANSITION:
                return SceneTransitionState(transition)
            if transition.type == playevents.END_GAME_TRANSITION:
                return EndGameState()
        # this should never happen!
        return None
    
    def drawPlayerMapView(self, surface):
        self.drawMapView(surface, player.viewRect)
        fixedSprites.draw(surface)
           
    def drawMapView(self, surface, viewRect, increment = 1, trigger = 0):
        surface.blit(player.rpgMap.mapImage, ORIGIN, viewRect)
        # if the sprite being updated is in view it will be added to visibleSprites as a side-effect
        self.gameSprites.update(player, self.visibleSprites, viewRect, increment, trigger)
        self.visibleSprites.draw(surface)
    
    def lifeLostTransition(self):
        registryHandler.switchToSnapshot()
        registry = registryHandler.registry
        player.setCoinCount(registry.coinCount)
        player.setKeyCount(registry.keyCount)
        return playevents.LifeLostTransition(registry.mapName,
                                             registry.playerPosition[0],
                                             registry.playerPosition[1],
                                             registry.playerLevel)
        
class SceneTransitionState:
    
    def __init__(self, transition):
        self.transition = transition
        self.screenImage = screen.copy()
        self.playState = None
        self.ticks = 0
             
    def execute(self, keyPresses):
        if self.ticks < THIRTY_TWO:
            if self.ticks == 0 and self.transition.type == playevents.SCENE_TRANSITION:
                eventBus.dispatchMapTransitionEvent(MapTransitionEvent())
            sceneZoomIn(self.screenImage, self.ticks)
        elif self.ticks < SIXTY_FOUR:
            if self.ticks == THIRTY_TWO:
                self.initPlayState()
            sceneZoomOut(self.screenImage, self.ticks - THIRTY_TWO)
        else:
            if self.transition.type == playevents.LIFE_LOST_TRANSITION:
                return self.playState
            # else just a regular scene transition
            direction = player.spriteFrames.direction
            if self.transition.boundary:
                return ShowPlayerState(direction, self.playState, BOUNDARY_TICKS[direction])
            return ShowPlayerState(direction, self.playState, DOORWAY_TICKS[direction])
        self.ticks += 1
        
    def initPlayState(self):
        # load the next map
        nextRpgMap = parser.loadRpgMap(self.transition.mapName)
        player.rpgMap = nextRpgMap
        # set player position
        player.setTilePosition(self.transition.tilePosition[0],
                               self.transition.tilePosition[1],
                               self.transition.level)
        # hide player if required
        if self.transition.boundary:
            hidePlayer(self.transition.boundary, nextRpgMap.mapRect)
        # create play state
        self.playState = PlayState()
        # setting the direction will also apply masks
        player.setDirection(self.transition.direction)
        # extract the next image from the play state
        self.playState.drawMapView(self.screenImage, player.viewRect, 0)           
            
class BoundaryTransitionState:
    
    def __init__(self, transition):
        self.transition = transition
        self.boundary = transition.boundary
        self.screenImage = screen.copy()
        self.nextImage = view.createRectangle(DIMENSIONS)
        self.playState = None
        self.ticks = 0
                     
    def execute(self, keyPresses):
        if self.ticks < THIRTY_TWO:
            if self.ticks == 0:
                eventBus.dispatchMapTransitionEvent(MapTransitionEvent())
                self.initPlayState()
            sliceWidth = self.ticks * X_MULT * 2
            sliceHeight = sliceWidth * Y_X_RATIO
            if self.boundary == UP:
                self.screenWipeDown(sliceHeight)
            elif self.boundary == DOWN:
                self.screenWipeUp(sliceHeight)
            elif self.boundary == LEFT:
                self.screenWipeRight(sliceWidth)
            else: # self.boundary == RIGHT
                self.screenWipeLeft(sliceWidth)
            pygame.display.flip()
        else:
            return ShowPlayerState(self.boundary, self.playState, BOUNDARY_TICKS[self.boundary])
        self.ticks += 1
        
    def initPlayState(self):
        # load the next map
        nextRpgMap = parser.loadRpgMap(self.transition.mapName)
        player.rpgMap = nextRpgMap
        player.spriteFrames.direction = self.boundary
        # set the new position
        hidePlayer(self.boundary, nextRpgMap.mapRect, self.transition.modifier)
        # create play state
        self.playState = PlayState()
        # extract the next image from the play state
        self.playState.drawMapView(self.nextImage, player.viewRect, 0)

    def screenWipeUp(self, sliceHeight):
        screen.blit(self.screenImage, ORIGIN, Rect(0, sliceHeight, VIEW_WIDTH, VIEW_HEIGHT - sliceHeight))
        screen.blit(self.nextImage, (0, VIEW_HEIGHT - sliceHeight), Rect(0, 0, VIEW_WIDTH, sliceHeight))                
        
    def screenWipeDown(self, sliceHeight):
        screen.blit(self.screenImage, (0, sliceHeight), Rect(0, 0, VIEW_WIDTH, VIEW_HEIGHT - sliceHeight))
        screen.blit(self.nextImage, ORIGIN, Rect(0, VIEW_HEIGHT - sliceHeight, VIEW_WIDTH, sliceHeight))                
    
    def screenWipeLeft(self, sliceWidth):
        screen.blit(self.screenImage, ORIGIN, Rect(sliceWidth, 0, VIEW_WIDTH - sliceWidth, VIEW_HEIGHT))
        screen.blit(self.nextImage, (VIEW_WIDTH - sliceWidth, 0), Rect(0, 0, sliceWidth, VIEW_HEIGHT))                
    
    def screenWipeRight(self, sliceWidth):
        screen.blit(self.screenImage, (sliceWidth, 0), Rect(0, 0, VIEW_WIDTH - sliceWidth, VIEW_HEIGHT))
        screen.blit(self.nextImage, ORIGIN, Rect(VIEW_WIDTH - sliceWidth, 0, sliceWidth, VIEW_HEIGHT))                

class GameOverState:
    
    def __init__(self):
        self.screenImage = screen.copy()
        self.topLine1 = gameFont.getTextImage("BRAVE ADVENTURER")
        self.topLine2 = gameFont.getTextImage("YOU ARE DEAD")
        self.topLine3 = gameFont.getTextImage("CONTINUE... 10")
        self.lowLine1 = gameFont.getTextImage("PRESS SPACE")
        self.lowLine2 = gameFont.getTextImage("TO PLAY AGAIN")
        self.blackRect = view.createRectangle(self.topLine3.get_size(), view.BLACK)
        self.continueOffered = True if registryHandler.snapshot.checkpoint else False
        self.countdown = None
        self.countdownTopleft = None
        self.ticks = 0
             
    def execute(self, keyPresses):
        if self.countdown:
            if (self.ticks - SIXTY_FOUR) % FRAMES_PER_SEC == 0:
                self.updateCountdown()                
        if self.ticks < THIRTY_TWO:
            sceneZoomIn(self.screenImage, self.ticks)
        elif self.ticks == THIRTY_TWO:
            x, y = (VIEW_WIDTH - self.topLine1.get_width()) // 2, 32 * SCALAR
            screen.blit(self.topLine1, (x, y))
            x, y = (VIEW_WIDTH - self.topLine2.get_width()) // 2, 44 * SCALAR
            screen.blit(self.topLine2, (x, y))
            if self.continueOffered:
                x, y = (VIEW_WIDTH - self.topLine3.get_width()) // 2, 56 * SCALAR
                screen.blit(self.topLine3, (x, y))
                # set the countdown topleft for later
                self.countdownTopleft = (x, y)
            pygame.display.flip()
        elif self.ticks == SIXTY_FOUR:
            x, y = (VIEW_WIDTH - self.lowLine1.get_width()) // 2, VIEW_HEIGHT - 42 * SCALAR
            screen.blit(self.lowLine1, (x, y))
            x, y = (VIEW_WIDTH - self.lowLine2.get_width()) // 2, VIEW_HEIGHT - 30 * SCALAR
            screen.blit(self.lowLine2, (x, y))
            pygame.display.flip()
            if self.continueOffered:
                self.countdown = 10
        elif self.ticks > SIXTY_FOUR:
            if keyPresses[K_SPACE]:
                if self.countdown:
                    return startGame(True)
                return startGame()
        self.ticks += 1
        
    def updateCountdown(self):
        self.countdown = self.countdown - 1
        countdownLine = gameFont.getTextImage("CONTINUE... " + str(self.countdown))
        screen.blit(self.blackRect, self.countdownTopleft)
        if self.countdown > 0:
            screen.blit(countdownLine, self.countdownTopleft)
        else:
            self.countdown = None
        pygame.display.flip()

class EndGameState:
    
    def __init__(self):
        self.screenImage = screen.copy()
        self.topLine1 = gameFont.getTextImage("YOUR ADVENTURE IS")
        self.topLine2 = gameFont.getTextImage("AT AN END... FOR NOW!")
        self.topLine3 = gameFont.getTextImage("YOU FOUND " + str(player.getCoinCount()) + "/10 COINS");
        self.lowLine1 = gameFont.getTextImage("PRESS SPACE")
        self.lowLine2 = gameFont.getTextImage("TO PLAY AGAIN")
        self.ticks = 0
             
    def execute(self, keyPresses):
        if self.ticks < THIRTY_TWO:
            if self.ticks == 0:
                eventBus.dispatchEndGameEvent(EndGameEvent())
            sceneZoomIn(self.screenImage, self.ticks)
        elif self.ticks == THIRTY_TWO:
            x, y = (VIEW_WIDTH - self.topLine1.get_width()) // 2, 32 * SCALAR
            screen.blit(self.topLine1, (x, y))
            x, y = (VIEW_WIDTH - self.topLine2.get_width()) // 2, 44 * SCALAR
            screen.blit(self.topLine2, (x, y))
            x, y = (VIEW_WIDTH - self.topLine3.get_width()) // 2, 56 * SCALAR
            screen.blit(self.topLine3, (x, y))
            pygame.display.flip()
        elif self.ticks == SIXTY_FOUR:
            x, y = (VIEW_WIDTH - self.lowLine1.get_width()) // 2, VIEW_HEIGHT - 42 * SCALAR
            screen.blit(self.lowLine1, (x, y))
            x, y = (VIEW_WIDTH - self.lowLine2.get_width()) // 2, VIEW_HEIGHT - 30 * SCALAR
            screen.blit(self.lowLine2, (x, y))
            pygame.display.flip()
        elif self.ticks > SIXTY_FOUR:
            if keyPresses[K_SPACE]:
                return startGame()
        self.ticks += 1
        
class ShowPlayerState:
    
    def __init__(self, boundary, nextPlayState, tickTarget):
        self.boundary = boundary
        self.playState = nextPlayState
        self.tickTarget = tickTarget
        self.ticks = 0
        
    def execute(self, keyPresses):
        if self.ticks > self.tickTarget:
            return self.playState
        px, py = 0, 0
        if self.boundary == UP:
            py = -MOVE_UNIT
        elif self.boundary == DOWN:
            py = MOVE_UNIT
        elif self.boundary == LEFT:
            px = -MOVE_UNIT
        else: # self.boundary == RIGHT
            px = MOVE_UNIT
        self.showPlayer(px, py)
        self.ticks += 1

    def showPlayer(self, px, py):
        player.wrapMovement(player.level,
                            player.spriteFrames.direction,
                            px, py)
        self.playState.drawMapView(screen, player.viewRect)
        pygame.display.flip()

class ShowBoatState:
    
    def __init__(self, nextPlayState, targetPosition):
        self.playState = nextPlayState
        self.targetPosition = targetPosition
        startPosition = registryHandler.getPlayerPosition()
        px = (targetPosition[0] - startPosition[0]) * TILE_SIZE
        self.targetMapRect = player.mapRect.move(px, 0)
        self.ticks = 0
        
    def execute(self, keyPresses):
        # bit of messing around here - we don't want to return the play state
        # until the boat has fired its boat stopped event
        if registryHandler.getMetadata("start:boat:0"):
            registryHandler.setPlayerPosition(self.targetPosition)
            registryHandler.takeSnapshot()
            return self.playState
        if player.mapRect.left == self.targetMapRect.left:
            self.showPlayer(0, 0)
        else:
            self.showPlayer(MOVE_UNIT, 0)
        self.ticks += 1
        
    def showPlayer(self, px, py):
        if self.ticks % 2:
            player.wrapMovement(player.level,
                                player.spriteFrames.direction,
                                px, py, 0)
        self.playState.drawMapView(screen, player.viewRect, trigger = 1)
        pygame.display.flip()
