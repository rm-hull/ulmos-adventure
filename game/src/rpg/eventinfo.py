#! /usr/bin/env python

from pygame.locals import Rect
from view import TILE_SIZE

DEFAULT_EVENT = 0
TRANSITION_EVENT = 1

def getEventTriggers_Dungeon():
    return []
    
def getEventTriggers_Islands():
    mapEventTriggers = {}
    eventTriggers = []
    eventTrigger = TransitionEventTrigger(2, 9)
    eventTrigger.setTransition("dungeon", 10, 12)
    eventTriggers.append(eventTrigger)
    mapEventTriggers[2] = eventTriggers
    return mapEventTriggers

eventInfo = {}
# eventInfo["skulls"] = getEventTriggers_Skulls
eventInfo["dungeon"] = getEventTriggers_Dungeon
eventInfo["islands"] = getEventTriggers_Islands
    
def getEventTriggers(mapName):
    if mapName in eventInfo:
        eventMethod = eventInfo[mapName]
        return eventMethod()
    return {}

class EventTrigger:
    
    def __init__(self, x, y):
        self.rect = Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.type = DEFAULT_EVENT
        
class TransitionEventTrigger(EventTrigger):
    
    def __init__(self, x, y):
        EventTrigger.__init__(self, x, y)
        self.type = TRANSITION_EVENT
        
    def setTransition(self, mapName, x, y):
        self.mapName = mapName
        self.mapPosition = (x, y)
        