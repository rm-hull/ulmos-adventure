#! /usr/bin/env python

from pygame.locals import Rect
from view import TILE_SIZE

TILE_TRIGGER = 1
BOUNDARY_TRIGGER = 2

DUMMY_EVENT = 0
TRANSITION_EVENT = 1
BOUNDARY_EVENT = 2

EMPTY_LIST = []

class Trigger:
    def __init__(self, event, type):
        self.event = event
        self.type = type

class TileTrigger(Trigger):
    def __init__(self, event, x, y, level):
        Trigger.__init__(self, event, TILE_TRIGGER)
        self.rect = Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.level = level
        
class BoundaryTrigger(Trigger):
    def __init__(self, event, boundary, min, max = None):
        Trigger.__init__(self, event, BOUNDARY_TRIGGER)
        self.boundary = boundary
        if max:
            self.range = range(min, max + 1)
        else:
            self.range = [min]

class Event:
    def __init__(self, type):
        self.type = type

class DummyEvent(Event):
    def __init__(self):
        Event.__init__(self, DUMMY_EVENT)
            
class TransitionEvent(Event):
    def __init__(self, mapName, x, y, level, boundary = None, direction = None):
        Event.__init__(self, TRANSITION_EVENT)
        self.mapName = mapName
        self.mapPosition = (x, y)
        self.mapLevel = level
        self.boundary = boundary
        self.direction = direction
        # this is needed for replay events
        self.pixelPosition = None
        
    def setPixelPosition(self, px, py):
        self.pixelPosition = (px, py)

class BoundaryEvent(Event):
    def __init__(self, mapName, boundary, modifier = 0):
        Event.__init__(self, BOUNDARY_EVENT)
        self.mapName = mapName
        self.boundary = boundary
        self.modifier = modifier
