#! /usr/bin/env python

import pygame
import sprites
import registry

def getGameSprites_Skulls():
    gameSprites = pygame.sprite.Group()
    flames1 = sprites.Flames()
    flames1.setPosition(8, 7, 2)
    flames2 = sprites.Flames()
    flames2.setPosition(5, 6, 2)
    flames3 = sprites.Flames()
    flames3.setPosition(6, 8, 2)
    flames4 = sprites.Flames()
    flames4.setPosition(10, 6, 2)
    gameSprites.add(flames1, flames2, flames3, flames4)
    return gameSprites

def getGameSprites_Dungeon():
    gameSprites = pygame.sprite.Group()
    flames1 = sprites.Flames()
    flames1.setPosition(3, 11, 2)
    flames2 = sprites.Flames()
    flames2.setPosition(11, 5, 2)
    gameSprites.add(flames1, flames2)
    return gameSprites

def getGameSprites_Islands():
    gameSprites = pygame.sprite.Group()
    flames1 = sprites.Flames()
    flames1.setPosition(10, 1, 2)
    flames2 = sprites.Flames()
    flames2.setPosition(12, 1, 2)
    coin1 = sprites.Coin()
    coin1.setPosition(2, 10, 2)
    #coin2 = sprites.Coin()
    #coin2.setPosition(10, 9, 3)
    door = sprites.Door()
    door.setPosition(10, 9, 3)
    gameSprites.add(flames1, flames2, coin1, door)
    return gameSprites

def addCoin(gameSprites, name, x, y, level):
    coinInfo = registry.getInfo(name)
    if coinInfo and coinInfo.available:
        coin = sprites.Coin(coinInfo)
        coin.setPosition(x, y, level)
        gameSprites.add(coin)

def addKey(gameSprites, name, x, y, level):
    keyInfo = registry.getInfo(name)
    if keyInfo and keyInfo.available:
        key = sprites.Key(keyInfo)
        key.setPosition(x, y, level)
        gameSprites.add(key)
    
def getGameSprites_Start():
    gameSprites = pygame.sprite.Group()
    addCoin(gameSprites, "start.coin.1", 7, 4, 2)
    addCoin(gameSprites, "start.coin.2", 24, 5, 3)
    # addCoin(gameSprites, "start.coin.3", 30, 5, 3)
    addKey(gameSprites, "start.key.1", 30, 5, 3)
    door = sprites.Door()
    door.setPosition(19, 2, 3)
    gameSprites.add(door)
    return gameSprites

def getGameSprites_Caves():
    gameSprites = pygame.sprite.Group()
    flames1 = sprites.Flames()
    flames1.setPosition(3, 4, 2)
    flames2 = sprites.Flames()
    flames2.setPosition(12, 1, 2)
    flames3 = sprites.Flames()
    flames3.setPosition(9, 10, 2)
    gameSprites.add(flames1, flames2, flames3)
    return gameSprites

def getGameSprites_East():
    gameSprites = pygame.sprite.Group()
    addKey(gameSprites, "east.key.1", 4, 13, 1)
    return gameSprites

spriteInfo = {}
spriteInfo["skulls"] = getGameSprites_Skulls
spriteInfo["dungeon"] = getGameSprites_Dungeon
spriteInfo["islands"] = getGameSprites_Islands
spriteInfo["start"] = getGameSprites_Start
spriteInfo["caves"] = getGameSprites_Caves
spriteInfo["east"] = getGameSprites_East

def getMapSprites(mapName):
    if mapName in spriteInfo:
        spriteMethod = spriteInfo[mapName]
        return spriteMethod()
    return pygame.sprite.Group()
