#! /usr/bin/env python

import pygame
import sprites
import staticsprites
import registry

def addCoin(gameSprites, name, x, y, level):
    coinInfo = registry.getInfo(name)
    if coinInfo and coinInfo.available:
        coin = staticsprites.Coin(coinInfo)
        coin.setPosition(x, y, level)
        gameSprites.add(coin)

def addKey(gameSprites, name, x, y, level):
    keyInfo = registry.getInfo(name)
    if keyInfo and keyInfo.available:
        key = staticsprites.Key(keyInfo)
        key.setPosition(x, y, level)
        gameSprites.add(key)

def addDoor(gameSprites, name, x, y, level, rpgMap):
    doorInfo = registry.getInfo(name)
    if doorInfo:
        if doorInfo.closed:
            door = staticsprites.Door(rpgMap, doorInfo)
            door.setPosition(x, y, level)
            gameSprites.add(door)
        else:
            rpgMap.addLevel(x, y + 1, level)
    
def getGameSprites_Start(rpgMap):
    gameSprites = pygame.sprite.Group()
    addCoin(gameSprites, "start.coin.1", 7, 4, 2)
    addCoin(gameSprites, "start.coin.2", 30, 5, 3)
    # addKey(gameSprites, "east.key", 30, 5, 3)
    addDoor(gameSprites, "start.door", 19, 2, 3, rpgMap)
    return gameSprites

def getGameSprites_Caves(rpgMap):
    gameSprites = pygame.sprite.Group()
    flames1 = staticsprites.Flames()
    flames1.setPosition(3, 4, 2)
    flames2 = staticsprites.Flames()
    flames2.setPosition(12, 1, 2)
    flames3 = staticsprites.Flames()
    flames3.setPosition(9, 10, 2)
    gameSprites.add(flames1, flames2, flames3)
    return gameSprites

def getGameSprites_East(rpgMap):
    gameSprites = pygame.sprite.Group()
    addKey(gameSprites, "east.key", 4, 13, 1)
    return gameSprites

spriteInfo = {}
spriteInfo["start"] = getGameSprites_Start
spriteInfo["caves"] = getGameSprites_Caves
spriteInfo["east"] = getGameSprites_East

def getMapSprites(rpgMap):
    if rpgMap.name in spriteInfo:
        spriteMethod = spriteInfo[rpgMap.name]
        return spriteMethod(rpgMap)
    return pygame.sprite.Group()
