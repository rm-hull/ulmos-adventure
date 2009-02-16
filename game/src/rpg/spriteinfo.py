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

def getGameSprites_Islands():
    gameSprites = pygame.sprite.Group()
    flames = sprites.Flames()
    flames.setPosition(5, 8, 2)
    gameSprites.add(flames)
    return gameSprites

spriteInfo = {}
spriteInfo["skulls"] = getGameSprites_Skulls
spriteInfo["islands"] = getGameSprites_Islands

def getMapSprites(mapName):
    if mapName in spriteInfo:
        spriteMethod = spriteInfo[mapName]
        return spriteMethod()
    return pygame.sprite.Group()
