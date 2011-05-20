#! /usr/bin/env python

import pygame

from othersprites import Baddie
from staticsprites import Flames, Coin, Key, Door

# map of sprite classes keyed on type
spriteClasses = {}
spriteClasses["flames"] = Flames
spriteClasses["coin"] = Coin
spriteClasses["key"] = Key
spriteClasses["door"] = Door
spriteClasses["baddie"] = Baddie

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
        sprite = spriteClass(mapSprite.uid, registry, rpgMap)
        sprite.setMovement(mapSprite.tilePoints, mapSprite.level)
        return sprite
    return None

"""
Returns a sprite group for the given map.  This excludes any sprites that are
removed from the map.
"""
def createSpritesForMap(rpgMap, registry):
    gameSprites = pygame.sprite.Group()
    if rpgMap.mapSprites:
        for mapSprite in rpgMap.mapSprites:
            sprite = createSprite(rpgMap, registry, mapSprite)
            if sprite:
                gameSprites.add(sprite)
    return gameSprites
