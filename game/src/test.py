#! /usr/bin/env python

from pygame.locals import *

import pygame
import rpg.states

FRAMES_PER_SEC = 60

def testMain():
    # get the first state
    currentState = rpg.states.startGame()
    # start the main loop
    clock = pygame.time.Clock()    
    while True:
        clock.tick(FRAMES_PER_SEC)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
        # detect key presses    
        keyPresses = pygame.key.get_pressed()
        # delegate key presses to the cuurent state
        newState = currentState.execute(keyPresses)
        # change state if necessary
        if newState:
            currentState = newState

# this calls the 'main' function when this script is executed
if __name__ == '__main__': testMain()
