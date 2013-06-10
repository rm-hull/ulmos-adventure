#! /usr/bin/env python

from pygame.locals import KEYDOWN, K_ESCAPE, K_x, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE, QUIT
import time
import pygame
import cwiid

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
        print "Press 1+2 on the Wii-mote to connect"
        wii = cwiid.Wiimote()
        wii.rpt_mode = cwiid.RPT_BTN
        print "Detected controller:", wii
        wii.rumble = 1
        time.sleep(1)
        wii.rumble = 0
        return wii;
    except RuntimeError:
        print "No wiimote found, continuing without..."

def getPressed():
    if wii:
        buttons = wii.state['buttons']
        return {
            K_RIGHT: (buttons & cwiid.BTN_RIGHT),
            K_LEFT:  (buttons & cwiid.BTN_LEFT),
            K_UP:    (buttons & cwiid.BTN_UP),
            K_DOWN:  (buttons & cwiid.BTN_DOWN),
            K_SPACE: (buttons & cwiid.BTN_A)
        }
    else:
        return pygame.key.get_pressed()

    return keyPresses

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
        keyPresses = getPressed()
        # delegate key presses to the current state
        newState = currentState.execute(keyPresses)
        # flush sounds
        rpg.states.soundHandler.flush()
        # change state if necessary
        if newState:
            currentState = newState

# this calls the testMain function when this script is executed
if __name__ == '__main__':
    wii = initWiimote()
    playMain()
