#!/usr/bin/env python

import os
import pygame

SOUNDS_FOLDER = "sounds"

def getSound(name, volume):
    soundPath = os.path.join(SOUNDS_FOLDER, name)
    sound = pygame.mixer.Sound(soundPath)
    sound.set_volume(volume)
    return sound

pickupSound = getSound("pickup.wav", 1.0)
doorSound = getSound("door.wav", 1.0)
swooshSound = getSound("swoosh.wav", 0.4)
lifeLostSound = getSound("lifelost.wav", 1.0)
footstepSound = getSound("footstep.wav", 0.5)
waspSound = getSound("wasp.wav", 0.8)
beetleSound = getSound("beetle.wav", 0.3)

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
    
    def waspZooming(self, waspZoomingEvent):
        waspSound.play()
        
    def beetleCrawling(self, beetleCrawlingEvent):
        beetleSound.play()
