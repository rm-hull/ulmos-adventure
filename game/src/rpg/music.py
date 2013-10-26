#! /usr/bin/env python

import os
import pygame

MUSIC_FOLDER = "music"

MUSIC_VOLUME = 0.4

DEFAULT_FADEOUT_MILLIS = 1000
LONG_FADEOUT_MILLIS = 4000

tracks = {"title": "ulmo-title.ogg",
          "main": "ulmo-main.ogg",
          "cave": None}

def getTrackPath(name):
    if name in tracks and tracks[name]:
        return os.path.join(MUSIC_FOLDER, tracks[name])
    return None

"""
Listens for specific events and builds up a set of sounds that are played back
when flush is called.
"""
class MusicHandler:
    
    def __init__(self):
        self.trackName = None
        self.musicOn = True
        self.musicEnabled = False
        if pygame.mixer.get_init():
            self.musicEnabled = True
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
        
    def playTrack(self, name):
        if self.musicEnabled:
            if name == self.trackName:
                return
            self.fadeoutCurrentTrack(name)
            trackPath = getTrackPath(name)
            if trackPath:
                try:
                    pygame.mixer.music.load(trackPath)
                    pygame.mixer.music.play(-1)
                except pygame.error:
                    print "Cannot load track: ", os.path.abspath(trackPath)
                    
    def longFadeoutCurrentTrack(self, name = None):
        self.fadeoutCurrentTrack(name, LONG_FADEOUT_MILLIS)
                        
    def fadeoutCurrentTrack(self, name = None, millis = DEFAULT_FADEOUT_MILLIS):
        self.trackName = name
        if self.musicEnabled:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(millis)        
            
    def toggleMusic(self):
        if self.musicEnabled:
            if self.musicOn:
                self.musicOn = False
                pygame.mixer.music.set_volume(0)
                return
            self.musicOn = True
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
 

