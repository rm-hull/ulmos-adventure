#! /usr/bin/env python

import pygame

from othersprites import Beetle, Wasp
from staticsprites import Flames, Coin, Key, Door
from spritemovement import NoMovement, RobotMovement, ZoomMovement

# map of sprite classes keyed on type
spriteClasses = {}
spriteClasses["flames"] = Flames
spriteClasses["coin"] = Coin
spriteClasses["key"] = Key
spriteClasses["door"] = Door
spriteClasses["beetle"] = Beetle
spriteClasses["wasp"] = Wasp

movementClasses = {}
movementClasses["none"] = NoMovement
movementClasses["robot"] = RobotMovement
movementClasses["zoom"] = ZoomMovement

"""
Returns a sprite instance based on the given mapSprite.  If the registry
indicates that the sprite has been removed from the map, this method returns
None.
"""
def createSprite(rpgMap, registry, mapSprite):
    spriteMetadata = registry.getMetadata(mapSprite.uid);
    if spriteMetadata:
        # allow any interactions with the map, eg. an open door
        spriteMetadata.applyMapActions(rpgMap)
        if spriteMetadata.isRemovedFromMap():
            return None
    if mapSprite.type in spriteClasses:
        spriteClass = spriteClasses[mapSprite.type]
        sprite = spriteClass(rpgMap)
        sprite.setUniqueIdentifier(mapSprite.uid, registry)
        return sprite
    print "sprite type not found: %s" % mapSprite.type 
    return None

"""
Returns a movement strategy instance based on the movement type contained in
the given mapSprite.
"""
def createSpriteMovement(player, sprite, mapSprite):
    if mapSprite.movement in movementClasses:
        movementClass = movementClasses[mapSprite.movement]
        movement = movementClass(sprite, mapSprite.level, mapSprite.tilePoints, player)
        return movement
    print "movement type not found: %s" % mapSprite.movement
    return None

"""
Returns a sprite group for the given map.  This excludes any sprites that are
removed from the map.
"""
def createSpritesForMap(rpgMap, registry, player):
    gameSprites = pygame.sprite.Group()
    if rpgMap.mapSprites:
        for mapSprite in rpgMap.mapSprites:
            sprite = createSprite(rpgMap, registry, mapSprite)
            if sprite:
                movement = createSpriteMovement(player, sprite, mapSprite)
                if movement:
                    gameSprites.add(sprite)
    return gameSprites
