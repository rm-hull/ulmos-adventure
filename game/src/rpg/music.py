#! /usr/bin/env python

import os
import pygame

MUSIC_FOLDER = "music"

VOLUME_OFF = 0

DEFAULT_FADEOUT_MILLIS = 1000
LONG_FADEOUT_MILLIS = 6000

tracks = {"title": ("ulmo-title.ogg", 0.6),
          "main": ("ulmo-main.ogg", 0.4)}

def getTrackAndVolume(name):
    if name in tracks:
        filename, volume = tracks[name]
        return os.path.join(MUSIC_FOLDER, filename), volume
    return None, None

"""
Plays, fades out and mutes music as required. Originally I intended to have different music for
different areas, but this proved quite tricky due to the way that fadeout blocks.
"""
class MusicPlayer:
    
    def __init__(self):
        self.trackName = None
        self.musicOn = True
        self.musicEnabled = True if pygame.mixer.get_init() else False
        self.volume = VOLUME_OFF
        
    def playTrack(self, name):
        if self.musicEnabled:
            if name == self.trackName:
                return
            self.fadeoutCurrentTrack(name)
            track, volume = getTrackAndVolume(name)
            if track:
                self.volume = volume
                if self.musicOn:
                    pygame.mixer.music.set_volume(self.volume)
                try:
                    pygame.mixer.music.load(track)
                    pygame.mixer.music.play(-1)
                except pygame.error:
                    print "Cannot load track: ", os.path.abspath(track)
                    
    def longFadeoutCurrentTrack(self, name = None):
        self.fadeoutCurrentTrack(name, LONG_FADEOUT_MILLIS)
                        
    def fadeoutCurrentTrack(self, name = None, millis = DEFAULT_FADEOUT_MILLIS):
        if self.musicEnabled:
            self.trackName = name
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(millis)        
            
    def toggleMusic(self):
        if self.musicEnabled:
            if self.musicOn:
                self.musicOn = False
                pygame.mixer.music.set_volume(0)
                return
            self.musicOn = True
            pygame.mixer.music.set_volume(self.volume)
            print pygame.mixer.music.get_volume()
 

