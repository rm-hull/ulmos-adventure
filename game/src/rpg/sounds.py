#!/usr/bin/env python

import os
import pygame

SOUNDS_FOLDER = "sounds"

pickupSoundPath = os.path.join(SOUNDS_FOLDER, "pickup.wav")
pickupSound = pygame.mixer.Sound(pickupSoundPath)
pickupSound.set_volume(1.0)

doorSoundPath = os.path.join(SOUNDS_FOLDER, "door.wav")
doorSound = pygame.mixer.Sound(doorSoundPath)
doorSound.set_volume(1.0)

swooshSoundPath = os.path.join(SOUNDS_FOLDER, "swoosh.wav")
swooshSound = pygame.mixer.Sound(swooshSoundPath)
swooshSound.set_volume(0.4)

lifeLostSoundPath = os.path.join(SOUNDS_FOLDER, "lifelost.wav")
lifeLostSound = pygame.mixer.Sound(lifeLostSoundPath)
lifeLostSound.set_volume(1.0)

footstepSoundPath = os.path.join(SOUNDS_FOLDER, "footstep.wav")
footstepSound = pygame.mixer.Sound(footstepSoundPath)
footstepSound.set_volume(0.5)

waspSoundPath = os.path.join(SOUNDS_FOLDER, "wasp.wav")
waspSound = pygame.mixer.Sound(waspSoundPath)
waspSound.set_volume(0.8)

class SoundHandler:
    
    def coinCollected(self, coinCollectedEvent):
        pickupSound.play()
        
    def keyCollected(self, keyCollectedEvent):
        pickupSound.play()
        
    def doorOpening(self, doorOpeningEvent):
        doorSound.play()
        
    def playerFootstep(self, playerFootstepEvent):
        footstepSound.play()
        
    def mapTransition(self, mapTransitionEvent):
        swooshSound.play()
        
    def lifeLost(self, lifeLostEvent):
        lifeLostSound.play()
    
    def waspZoom(self, waspZoomEvent):
        waspSound.play()