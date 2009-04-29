#! /usr/bin/env python

from pygame.locals import Rect
from view import UP, DOWN, LEFT, RIGHT, TILE_SIZE

TILE_TRIGGER = 1
BOUNDARY_TRIGGER = 2

DUMMY_EVENT = 0
TRANSITION_EVENT = 1
BOUNDARY_EVENT = 2

EMPTY_LIST = []

def getTriggers_Demo():
    triggers = []
    event = BoundaryEvent(UP, "skulls", 4)
    triggers.append(BoundaryTrigger(event, UP, 4, 7))
    event = BoundaryEvent(UP, "demo", 2)
    triggers.append(BoundaryTrigger(event, UP, 0, 3))
    event = BoundaryEvent(DOWN, "demo", -2)
    triggers.append(BoundaryTrigger(event, DOWN, 4, 7))
    event = BoundaryEvent(LEFT, "demo", 0)
    triggers.append(BoundaryTrigger(event, LEFT, 0, 8))
    event = BoundaryEvent(RIGHT, "demo", 0)
    triggers.append(BoundaryTrigger(event, RIGHT, 0, 8))
    return triggers
    
def getTriggers_Skulls():
    triggers = []
    event = TransitionEvent("demo", 2, 0, 1)
    # event = BoundaryEvent(DOWN, "demo", -4)
    triggers.append(BoundaryTrigger(event, DOWN, 0, 8))
    return triggers
    
def getTriggers_Islands():
    triggers = []
    event = TransitionEvent("dungeon", 10, 6, 1)
    triggers.append(TileTrigger(event, 5, 12, 2))
    event = TransitionEvent("dungeon", 10, 10, 1)
    triggers.append(TileTrigger(event, 2, 9, 2))
    event = BoundaryEvent(UP, "dungeon", -7)
    triggers.append(BoundaryTrigger(event, UP, 8, 15))
    return triggers

def getTriggers_Dungeon():
    triggers = []
    event = BoundaryEvent(DOWN, "islands", 7)
    triggers.append(BoundaryTrigger(event, DOWN, 0, 7))
    return triggers

def getTriggers_Start():
    triggers = []
    event = BoundaryEvent(RIGHT, "bridge", 0)
    triggers.append(BoundaryTrigger(event, RIGHT, 10, 12))
    return triggers

def getTriggers_Bridge():
    triggers = []
    event = BoundaryEvent(LEFT, "start", 0)
    triggers.append(BoundaryTrigger(event, LEFT, 10, 12))
    event = TransitionEvent("caves", 11, 14, 1, UP)
    triggers.append(TileTrigger(event, 7, 7, 1))
    event = TransitionEvent("caves", 4, 14, 1, UP)
    triggers.append(TileTrigger(event, 3, 2, 3))
    return triggers

def getTriggers_Caves():
    triggers = []
    event = TransitionEvent("bridge", 3, 1, 3)
    triggers.append(BoundaryTrigger(event, DOWN, 4))
    event = TransitionEvent("bridge", 7, 6, 1)
    triggers.append(BoundaryTrigger(event, DOWN, 11))
    return triggers

eventInfo = {}
eventInfo["demo"] = getTriggers_Demo
eventInfo["skulls"] = getTriggers_Skulls
eventInfo["dungeon"] = getTriggers_Dungeon
eventInfo["islands"] = getTriggers_Islands
eventInfo["start"] = getTriggers_Start
eventInfo["bridge"] = getTriggers_Bridge
eventInfo["caves"] = getTriggers_Caves

def getTriggers(mapName):    
    if mapName in eventInfo:
        getTriggers = eventInfo[mapName]
        return getTriggers()
    return EMPTY_LIST

def getTileTriggers(mapName):
    tileTriggers = {}
    for trigger in getTriggers(mapName):
        if trigger.type == TILE_TRIGGER:
            if trigger.level in tileTriggers:
                tileTriggers[trigger.level].append(trigger)
            else:
                tileTriggers[trigger.level] = [trigger]
    return tileTriggers

def getBoundaryTriggers(mapName):
    boundaryTriggers = {}
    for trigger in getTriggers(mapName):
        if trigger.type == BOUNDARY_TRIGGER:
            if trigger.boundary in boundaryTriggers:
                boundaryTriggers[trigger.boundary].append(trigger)
            else:
                boundaryTriggers[trigger.boundary] = [trigger]
    return boundaryTriggers

class EventTrigger:
    def __init__(self, event, type):
        self.event = event
        self.type = type

class TileTrigger(EventTrigger):
    def __init__(self, event, x, y, level):
        EventTrigger.__init__(self, event, TILE_TRIGGER)
        self.rect = Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.level = level
        
class BoundaryTrigger(EventTrigger):
    def __init__(self, event, boundary, min, max = None):
        EventTrigger.__init__(self, event, BOUNDARY_TRIGGER)
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

class BoundaryEvent(Event):
    def __init__(self, boundary, mapName, modifier):
        Event.__init__(self, BOUNDARY_EVENT)
        self.boundary = boundary
        self.mapName = mapName
        self.modifier = modifier
   