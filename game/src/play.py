#! /usr/bin/env python

from pygame.locals import KEYDOWN, K_ESCAPE, K_x, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE, QUIT

import pygame

"""
If using an older Raspberry Pi distro, you might need to run the following commands to get working sound:

sudo apt-get install alsa-utils
sudo modprobe snd_bcm2835
"""

# initialise pygame before we import anything else
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()

import rpg.states

def initWiimote():
    try:
        println "Press 1+2 on the Wii-mote to connect"
        wii = cwiid.WiiRemote()
        wii.rpt_mode = cwiid.RPT_BTN
        println "Detected controller:" wii
        rumble()
    exception RuntimeError:
        println "No wiimote found, continuing without..."

def getPressed():
    keyPresses = []
    if wii:
        buttons = wii.state['buttons']
        if (buttons & cwiid.BTN_RIGHT):
            keyPresses.add(K_RIGHT)
        if (buttons & cwiid.BTN_LEFT):
            keyPresses.add(K_LEFT)
        if (buttons & cwiid.BTN_UP):
            keyPresses.add(K_UP)
        if (buttons & cwiid.BTN_DOWN):
            keyPresses.add(K_DOWN)
        if (buttons & cwiid.BTN_A):
            keyPresses.add(K_SPACE)
    else:
        keyPressespygame.key.get_pressed()

def playMain():
    # get the first state
    currentState = rpg.states.showTitle()
    # start the main loop
    clock = pygame.time.Clock()
    while True:
        clock.tick(rpg.states.FRAMES_PER_SEC)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            if event.type == KEYDOWN and event.key == K_x:
                # mute sound handler
                rpg.states.soundHandler.toggleSound()
        # detect key presses
        keyPresses = getPresses()
        # delegate key presses to the current state
        newState = currentState.execute(keyPresses)
        # flush sounds
        rpg.states.soundHandler.flush()
        # change state if necessary
        if newState:
            currentState = newState

# this calls the testMain function when this script is executed
if __name__ == '__main__':
    initWiimote()
    playMain()
