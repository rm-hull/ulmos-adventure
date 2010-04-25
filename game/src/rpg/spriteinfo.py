#! /usr/bin/env python

import pygame
import staticsprites
import registry

def createFlames(name, x, y, level, rpgMap = None):
    flamesInfo = registry.getInfo(name)
    if flamesInfo and flamesInfo.goneOut:
        return None
    if flamesInfo is None:
        flamesInfo = registry.FlamesInfo(name)
        registry.registerInfo(flamesInfo)
    flames = staticsprites.Flames(flamesInfo)
    flames.setPosition(x, y, level)
    return flames

def createCoin(name, x, y, level, rpgMap = None):
    coinInfo = registry.getInfo(name)
    if coinInfo and coinInfo.collected:
        return None
    if coinInfo is None:
        coinInfo = registry.CoinInfo(name)
        registry.registerInfo(coinInfo)
    coin = staticsprites.Coin(coinInfo)
    coin.setPosition(x, y, level)
    return coin

def createKey(name, x, y, level, rpgMap = None):
    keyInfo = registry.getInfo(name)
    if keyInfo and keyInfo.collected:
        return None
    if keyInfo is None:
        keyInfo = registry.KeyInfo(name)
        registry.registerInfo(keyInfo)        
    key = staticsprites.Key(keyInfo)
    key.setPosition(x, y, level)
    return key

def createDoor(name, x, y, level, rpgMap = None):
    doorInfo = registry.getInfo(name)
    if doorInfo and doorInfo.open:
        rpgMap.addLevel(x, y + 1, level)
        return None
    if doorInfo is None:
        doorInfo = registry.DoorInfo(name)
        registry.registerInfo(doorInfo)        
    door = staticsprites.Door(rpgMap, doorInfo)
    door.setPosition(x, y, level)
    return door

createSpriteMethods = {}
createSpriteMethods["flames"] = createFlames
createSpriteMethods["coin"] = createCoin
createSpriteMethods["key"] = createKey
createSpriteMethods["door"] = createDoor

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
