#! /usr/bin/env python

from __future__ import with_statement

import os
import view
import map
import events

from pygame.locals import Rect
from view import UP, DOWN, LEFT, RIGHT

TILES_FOLDER = "tiles"
MAPS_FOLDER = "maps"
OPEN_SQ_BRACKET = "["
CLOSE_SQ_BRACKET = "]"
SPECIAL_LEVEL = "S"
VERTICAL_MASK = "V"
COLON = ":"
COMMA = ","
SPRITE = "sprite"
TRIGGER = "event"
PIPE = "|"
DASH = "-"

BOUNDARIES = {"up": UP, "down": DOWN, "left": LEFT, "right": RIGHT}

def getXY(xyStr, delimiter = COMMA):
    return [int(n) for n in xyStr.split(delimiter)]

def getTilePoints(xyList, delimiter = COMMA):
    tilePoints = []
    for xy in xyList:
        tilePoints.append(getXY(xy, delimiter))
    return tilePoints
    
def loadRpgMap(name):
    # tileData is keyed on an x,y tuple
    tileData = {}
    spriteData = []
    triggerData = []
    # parse map file - each line represents one map tile        
    mapPath = os.path.join(MAPS_FOLDER, name + ".map")
    print "loading: %s" % mapPath
    with open(mapPath) as mapFile:
        # eg. 10,4 [1] water:dark grass:l2 wood:lrs_supp:3
        maxX, maxY = 0, 0
        for line in mapFile:
            try:
                line = line.strip()
                if len(line) > 0:                        
                    bits = line.split()
                    if len(bits) > 0:
                        if bits[0] == SPRITE:
                            if len(bits) > 1:
                                spriteData.append(bits[1:])
                        elif bits[0] == TRIGGER:
                            if len(bits) > 1:
                                triggerData.append(bits[1:])
                        else:                          
                            tilePoint = bits[0]
                            #print "%s -> %s" % (tileRef, tileName)
                            x, y = getXY(tilePoint)
                            maxX, maxY = max(x, maxX), max(y, maxY)
                            if len(bits) > 1:
                                tileData[(x, y)] = bits[1:]
            except ValueError:
                pass
    # create map tiles
    mapTiles = createMapTiles(maxX + 1, maxY + 1, tileData)
    mapSprites = createMapSprites(spriteData, name)
    mapTriggers = createMapTriggers(triggerData)
    # create map and return
    return map.RpgMap(name, mapTiles, mapSprites, mapTriggers)

def createMapTiles(cols, rows, tileData):
    mapTiles = [[None] * (rows) for i in range(cols)]
    # iterate through the tile data and create the map tiles
    tileSets = {}     
    for tilePoint in tileData.keys():
        x, y = tilePoint[0], tilePoint[1]
        mapTile = map.MapTile(x, y)
        bits = tileData[(x, y)]
        # print bits
        startIndex = 0
        if bits[0][0] == OPEN_SQ_BRACKET and bits[0][-1] == CLOSE_SQ_BRACKET:
            # levels
            startIndex = 1
            levels = bits[0][1:-1].split(COMMA)
            for level in levels:
                if level[0] == SPECIAL_LEVEL:
                    mapTile.addSpecialLevel(float(level[1:]))
                else:
                    mapTile.addLevel(float(level))
        # tiles images
        for tileIndex, tiles in enumerate(bits[startIndex:]):
            tileBits = tiles.split(COLON)
            if len(tileBits) > 1:
                tileSetName = tileBits[0]
                if tileSetName in tileSets:
                    tileSet = tileSets[tileSetName]
                else:
                    # tileSet = TileSet(tileSetName)
                    tileSet = loadTileSet(tileSetName)
                    tileSets[tileSetName] = tileSet
                tileName = tileBits[1]
                mapTile.addTile(tileSet.getTile(tileName))
                # masks
                if len(tileBits) > 2:
                    maskLevel = tileBits[2]
                    # mapTile.addMaskTile(maskLevel, tileSet.getTile(tileName))
                    if maskLevel[0] == VERTICAL_MASK:
                        mapTile.addMask(tileIndex, int(maskLevel[1:]), False)
                    else:    
                        mapTile.addMask(tileIndex, int(maskLevel))
        mapTiles[x][y] = mapTile
    return mapTiles

def loadTileSet(name):
    # print "load tileset: %s" % (name)
    # tileSet = map.TileSet()
    tiles = {}
    # load tile set image
    imagePath = os.path.join(TILES_FOLDER, name + ".png")
    tilesImage = view.loadScaledImage(imagePath, view.TRANSPARENT_COLOUR)
    # parse metadata - each line represents one tile in the tile set
    metadataPath = os.path.join(TILES_FOLDER, name + "_metadata.txt")
    with open(metadataPath) as metadata:
        # eg. 1,5 lst1
        for line in metadata:
            try:
                line = line.strip()
                if len(line) > 0:                        
                    tilePoint, tileName = line.strip().split()
                    # print "%s -> %s" % (tileRef, tileName)
                    x, y = tilePoint.split(COMMA)
                    px, py = int(x) * view.TILE_SIZE, int(y) * view.TILE_SIZE
                    tileRect = Rect(px, py, view.TILE_SIZE, view.TILE_SIZE)
                    tileImage = tilesImage.subsurface(tileRect).copy()
                    tiles[tileName] = tileImage
                    # self.maskTiles[tileName] = view.createMaskTile(tileImage)
            except ValueError:
                pass
    # create tile set and return
    return map.TileSet(tiles)

def createMapSprites(spriteData, mapName):
    mapSprites = []
    typeCounts = {}
    for spriteBits in spriteData:
        if len(spriteBits) > 2:
            type = spriteBits[0]
            level = int(spriteBits[1])
            tilePoints = getTilePoints(spriteBits[2:])
            if type in typeCounts:
                typeCounts[type] += 1
            else:
                typeCounts[type] = 0
            typeCount = typeCounts[type]
            uid = mapName + COLON + type + COLON + str(typeCount)
            mapSprite = map.MapSprite(type, uid, level, tilePoints)
            mapSprites.append(mapSprite)
    return mapSprites
            
def createMapTriggers(triggerData):
    mapTriggers = []
    for triggerBits in triggerData:
        eventBits = None
        try:
            eventIndex = triggerBits.index(PIPE) + 1
            eventBits = triggerBits[eventIndex:]
            triggerBits = triggerBits[0:eventIndex]
        except (ValueError, IndexError):
            pass
        if eventBits:
            event = None
            eventType = eventBits[0]
            if eventType == "boundary":
                event = createBoundaryEvent(eventBits)
            elif eventType == "transition":
                event = createTransitionEvent(eventBits)
            if event and triggerBits:
                trigger = None
                triggerType = triggerBits[0]
                if triggerType == "boundary":
                    trigger = createBoundaryTrigger(triggerBits, event)
                elif triggerType == "tile":
                    trigger = createTileTrigger(triggerBits, event)
                if trigger:
                    mapTriggers.append(trigger)
    return mapTriggers
                            
def createBoundaryEvent(eventBits):
    if len(eventBits) < 3:
        return None
    mapName = eventBits[1]
    boundary = BOUNDARIES[eventBits[2]]
    if len(eventBits) > 3:
        modifier = int(eventBits[3])
        return events.BoundaryEvent(mapName, boundary, modifier)
    return events.BoundaryEvent(mapName, boundary)

def createTransitionEvent(eventBits):
    if len(eventBits) < 4:
        return None
    mapName = eventBits[1]
    x, y = getXY(eventBits[2])
    level = int(eventBits[3])
    if len(eventBits) > 4:
        boundary = BOUNDARIES[eventBits[4]]
        if len(eventBits) > 5:
            direction = BOUNDARIES[eventBits[5]]
            return events.TransitionEvent(mapName, x, y, level, boundary, direction)
        return events.TransitionEvent(mapName, x, y, level, boundary)
    return events.TransitionEvent(mapName, x, y, level)
    
def createBoundaryTrigger(triggerBits, event):
    if len(triggerBits) < 3:
        return None
    boundary = BOUNDARIES[triggerBits[1]]
    range = triggerBits[2]
    if DASH in range:
        min, max = getXY(range, DASH)
        return events.BoundaryTrigger(event, boundary, min, max)
    return events.BoundaryTrigger(event, boundary, int(range))

def createTileTrigger(triggerBits, event):
    if len(triggerBits) < 3:
        return None
    x, y = getXY(triggerBits[1])
    level = int(triggerBits[2])
    return events.TileTrigger(event, x, y, level)
    return None