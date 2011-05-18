#! /usr/bin/env python

from pygame.locals import Rect
from view import TILE_SIZE

TILE_TRIGGER = 1
BOUNDARY_TRIGGER = 2

DUMMY_EVENT = 0
TRANSITION_EVENT = 1
REPLAY_EVENT = 2
BOUNDARY_EVENT = 3

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

"""
Describes a transition event that can occur when the player hits a tile/boundary trigger.
"""            
class TransitionEvent(Event):
    def __init__(self, mapName, x, y, level, direction, boundary = None):
        Event.__init__(self, TRANSITION_EVENT)
        self.mapName = mapName
        self.tilePosition = (x, y)
        self.level = level
        self.direction = direction
        self.boundary = boundary
        self.firstMap = False

"""
Very similar to transition event, but describes a replay event that occurs when
the player loses a life and the scene is reset.
"""        
class ReplayEvent(Event):
    def __init__(self, mapName, px, py, level, direction, boundary = None):
        Event.__init__(self, REPLAY_EVENT)
        self.mapName = mapName
        self.pixelPosition = (px, py)
        self.level = level
        self.direction = direction
        self.boundary = boundary
        self.firstMap = False

"""
Describes a boundary event that occurs when the player walks off the edge of
one map and onto another.
"""        
class BoundaryEvent(Event):
    def __init__(self, mapName, boundary, modifier = 0):
        Event.__init__(self, BOUNDARY_EVENT)
        self.mapName = mapName
        self.boundary = boundary
        self.modifier = modifier
