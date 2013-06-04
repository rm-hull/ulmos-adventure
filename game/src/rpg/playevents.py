#! /usr/bin/env python

from view import DOWN

FALLING_EVENT = 0
TILE_EVENT = 1
BOUNDARY_EVENT = 2
LIFE_LOST_EVENT = 3

BOUNDARY_TRANSITION = 1
SCENE_TRANSITION = 2
LIFE_LOST_TRANSITION = 3
END_GAME_TRANSITION = 4

"""
Some play events have two parts:

1. The event itself, eg. a BoundaryEvent indicates that the player has breached a
map boundary.

2. A transition that describes what happens next, eg. a SceneTransition indicates
that we need to replace the current map with another map.

For example, a BoundaryEvent might contain a BoundaryTransition (when the player
walks off the edge of one map and onto another) a SceneTransition (when the
player walks out of a cave) or an EndGameTransition.

Other play events, eg. FallingEvent, do not contain transitions. 
"""
class PlayEvent:
    def __init__(self, type, transition = None):
        self.type = type
        self.transition = transition

"""
Defines a falling event that occurs when the player walks off a ledge.
"""            
class FallingEvent(PlayEvent):
    def __init__(self, downLevel):
        PlayEvent.__init__(self, FALLING_EVENT)
        self.downLevel = downLevel

"""
Defines an event that occurs when the player steps on a tile that has an event.
"""
class TileEvent(PlayEvent):
    def __init__(self, transition, x, y, level):
        PlayEvent.__init__(self, TILE_EVENT, transition)
        self.x, self.y = x, y
        self.level = level

"""
Defines an event that occurs when the player walks off the edge of the map.
"""        
class BoundaryEvent(PlayEvent):
    def __init__(self, transition, boundary, min, max = None):
        PlayEvent.__init__(self, BOUNDARY_EVENT, transition)
        self.boundary = boundary
        if max:
            self.range = range(min, max + 1)
        else:
            self.range = [min]

"""
Defines an event that occurs when the player loses a life and is also used to
indicate game over.  Note that although a LifeLostTransition does exist, this
event does NOT contain it.
"""
class LifeLostEvent(PlayEvent):
    def __init__(self, gameOver = False):
        PlayEvent.__init__(self, LIFE_LOST_EVENT)
        self.gameOver = gameOver
        
"""
Transition base class.
"""
class Transition:
    def __init__(self, type, mapName = None):
        self.type = type
        self.mapName = mapName

"""
Defines a transition for when we switch from one scene to another, eg. when the
player walks into a cave.
"""            
class SceneTransition(Transition):
    def __init__(self, mapName, x, y, level, direction, boundary = None):
        Transition.__init__(self, SCENE_TRANSITION, mapName)
        self.tilePosition = (x, y)
        self.level = level
        self.direction = direction
        self.boundary = boundary

"""
Defines a transition for when the player loses a life and the scene is reset.
Note that this is very similar to a scene transition.
"""        
class LifeLostTransition(Transition):
    def __init__(self, mapName, x, y, level):
        Transition.__init__(self, LIFE_LOST_TRANSITION, mapName)
        self.tilePosition = (x, y)
        self.level = level
        self.direction = DOWN
        self.boundary = None

"""
Defines a transition for when the player walks off the edge of one map and onto
another.
"""        
class BoundaryTransition(Transition):
    def __init__(self, mapName, boundary, modifier = 0):
        Transition.__init__(self, BOUNDARY_TRANSITION, mapName)
        self.boundary = boundary
        self.modifier = modifier

"""
Defines a transition for when the player reaches the end of the game. 
"""        
class EndGameTransition(Transition):
    def __init__(self):
        Transition.__init__(self, END_GAME_TRANSITION)
    
