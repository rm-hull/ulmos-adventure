#! /usr/bin/env python

import pygame

import rpg.sprites as sprites

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

spriteInfo = {}
spriteInfo["skulls"] = getGameSprites_Skulls
spriteInfo["dungeon"] = getGameSprites_Dungeon

def getMapSprites(mapName):
    if mapName in spriteInfo:
        spriteMethod = spriteInfo[mapName]
        return spriteMethod()
    return pygame.sprite.Group()
