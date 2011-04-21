#! /usr/bin/env python

from staticsprites import Flames, Coin, Key, Door

import pygame

spriteClasses = {}
spriteClasses["flames"] = Flames
spriteClasses["coin"] = Coin
spriteClasses["key"] = Key
spriteClasses["door"] = Door

def createSprite(rpgMap, registry, mapSprite):
    spriteMetadata = registry.getMetadata(mapSprite.uid);
    if spriteMetadata:
        spriteMetadata.applyMapActions(rpgMap)
        if spriteMetadata.isInactive():
            return None
    if mapSprite.type in spriteClasses:
        spriteClass = spriteClasses[mapSprite.type]
        sprite = spriteClass(mapSprite.uid, rpgMap, registry)
        sprite.setPosition(mapSprite.x, mapSprite.y, mapSprite.level)
        return sprite
    return None

def createSpritesForMap(rpgMap, registry):
    gameSprites = pygame.sprite.Group()
    if rpgMap.mapSprites:
        for mapSprite in rpgMap.mapSprites:
            sprite = createSprite(rpgMap, registry, mapSprite)
            if sprite:
                gameSprites.add(sprite)
    return gameSprites
