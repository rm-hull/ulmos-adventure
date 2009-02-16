#! /usr/bin/env python

from __future__ import with_statement

import os
import view
import map

from pygame.locals import Rect

TILES_FOLDER = "tiles"
MAPS_FOLDER = "maps"
OPEN_SQ_BRACKET = "["
CLOSE_SQ_BRACKET = "]"
SPECIAL_LEVEL = "S"
VERTICAL_MASK = "V"
COLON = ":"
COMMA = ","

def loadRpgMap(name):
    # tileData is keyed on an x,y tuple
    tileData = {}
    # parse map file - each line represents one map tile        
    mapPath = os.path.join(MAPS_FOLDER, name + ".map")
    with open(mapPath) as mapFile:
        # eg. 10,4 [1] water:dark grass:l2 wood:lrs_supp:3
        maxX, maxY = 0, 0
        for line in mapFile:
            try:
                line = line.strip()
                if len(line) > 0:                        
                    bits = line.split()
                    if len(bits) > 0:                            
                        tilePoint = bits[0]
                        #print "%s -> %s" % (tileRef, tileName)
                        x, y = [int(n) for n in tilePoint.split(COMMA)]
                        maxX, maxY = max(x, maxX), max(y, maxY)
                        if len(bits) > 1:
                            tileData[(x, y)] = bits[1:]
            except ValueError:
                pass
    # create map tiles
    mapTiles = createMapTiles(maxX + 1, maxY + 1, tileData)
    # create map and return
    return map.RpgMap(name, mapTiles)

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
        tileIndex = 0
        for tiles in bits[startIndex:]:
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
                tileIndex += 1
        mapTiles[x][y] = mapTile
    return mapTiles

def loadTileSet(name):
    print "load tileset: %s" % (name)
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
