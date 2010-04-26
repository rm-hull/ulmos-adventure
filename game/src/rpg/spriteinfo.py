#! /usr/bin/env python

import pygame
import registry
import staticsprites

"""
Standard method for creating registered sprites.  Most types of sprite should be
able to use this.
"""
def createSprite(name, x, y, level, spriteInfoClass):
    spriteInfo = registry.getInfo(name)
    if spriteInfo and spriteInfo.isInactive():
        return None
    if spriteInfo is None:
        spriteInfo = spriteInfoClass(name)
        registry.registerInfo(spriteInfo)
    sprite = spriteInfo.getSprite()
    sprite.setPosition(x, y, level)
    return sprite
    
def createFlames(name, x, y, level, rpgMap = None):
    return createSprite(name, x, y, level, registry.FlamesInfo)

def createCoin(name, x, y, level, rpgMap = None):
    return createSprite(name, x, y, level, registry.CoinInfo)

def createKey(name, x, y, level, rpgMap = None):
    return createSprite(name, x, y, level, registry.KeyInfo)

"""
Door sprites require a specialised method since opening them changes the state
of the parent map.
"""
def createDoor(name, x, y, level, rpgMap):
    doorInfo = registry.getInfo(name)
    if doorInfo and doorInfo.open:
        rpgMap.addLevel(x, y + 1, level)
        return None
    if doorInfo is None:
        doorInfo = registry.DoorInfo(name)
        registry.registerInfo(doorInfo)        
    door = staticsprites.Door(doorInfo, rpgMap)
    door.setPosition(x, y, level)
    return door

createSpriteMethods = {}
createSpriteMethods["flames"] = createFlames
createSpriteMethods["coin"] = createCoin
createSpriteMethods["key"] = createKey
createSpriteMethods["door"] = createDoor

"""
Returns a group of registered sprites for the given map.
"""
def getMapSprites(rpgMap):
    gameSprites = pygame.sprite.Group()
    if rpgMap.mapSprites:
        for mapSprite in rpgMap.mapSprites:
            if mapSprite.type in createSpriteMethods:
                createSprite = createSpriteMethods[mapSprite.type]
                sprite = createSprite(mapSprite.name,
                                      mapSprite.x,
                                      mapSprite.y,
                                      mapSprite.level,
                                      rpgMap)
                if sprite:
                    gameSprites.add(sprite)
    return gameSprites
