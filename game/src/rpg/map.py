#! /usr/bin/env python

from __future__ import with_statement

from view import TILE_SIZE

import view

UPPER_LIMIT = 32
LOWER_LIMIT = -31

"""
Encapsulates the logic required for the main map.  You should not instantiate
this class directly - instead, use parser.loadRpgMap and the mapTiles will be
populated from the named map file.
"""
class RpgMap:
    
    def __init__(self, name, mapTiles):
        self.name = name
        self.mapTiles = mapTiles
        self.cols = len(self.mapTiles)
        self.rows = len(self.mapTiles[0])
        self.initialiseMapImage()

    def initialiseMapImage(self):
        self.mapImage = view.createRectangle((self.cols * view.TILE_SIZE,
                                              self.rows * view.TILE_SIZE),
                                              view.BLACK)
        for x in range(self.cols):
            for y in range(self.rows):
                mapTile = self.mapTiles[x][y]
                if mapTile:
                    tileImage = mapTile.createTileImage()
                    if tileImage:
                        self.mapImage.blit(tileImage, (x * view.TILE_SIZE, y * view.TILE_SIZE))
        self.mapRect = self.mapImage.get_rect()
    
    def getMapView(self, viewRect):
        return self.mapImage.subsurface(viewRect)
    
    """
    The map restricts movement via the following system.

    Each tile has 0 or more levels that determine if a sprite can move onto them.
    At its most basic, if the sprite is at level 1 they will be blocked if they
    attempt to move onto a level 2 tile. However, things get more interesting if
    steps are involved. For examples, consider the following representation of a
    two-level map with steps linking the two levels:
    
    [2]  [S2]  [2]  <- level 2
    [X] [S1.5] [X]  <- top of steps + wall on either side
    [1] [S1.5] [1]  <- bottom of steps + level 1 on either side
    [1]  [S1]  [1]  <- level 1
    
    Note that [X] represents a tile that is inaccessible, [1] and [2] are level 1
    and 2 tiles and [S*] are 'specials'.  All this information can be viewed/edited
    using the map editor.
    
    Movement is deemed to be valid if one of the following criteria is met - the
    phrase 'base tiles' is used here to mean all tiles that are touched by the base
    rect of the sprite:
    
    > All base tiles are at the same level as the sprite. Eg. [1] [1] would be ok,
      [1] [S1] would be ok, [1] [S1.5] would not.
        
    > All base tiles are 'specials' and the difference between the min and max
      level is less than one. In addition, the difference between all tile
      levels and the sprite level must also be less than one. Eg. [S1] [S1.5]
      would be ok, [S1.5] [S2] would be ok, [S1] [S2] would not.
    
    Note that base tiles can include anything from 1 to 4 tiles - I just used
    two-tile examples above for the sake of brevity.
    
    If movement is valid, the sprite level is made equal to the maximum tile level
    of the base tiles. This allows the sprite to move between one level and another.
    """
    def isMoveValid(self, level, baseRect):
        baseTiles = self.getRectTiles(baseRect)
        sameLevelCount = 0
        specialLevels = []
        # iterate through base tiles and gather information
        for tile in baseTiles:
            if tile:
                if level in tile.levels:
                    sameLevelCount += 1
                elif level in tile.specialLevels:
                    sameLevelCount += 1
                    specialLevels.append(level)                
                else:
                    specialLevel = tile.getSpecialLevel(level)
                    if specialLevel:
                        specialLevels.append(specialLevel)
        # test validity of the requested movement           
        if sameLevelCount == len(baseTiles):
            return True, level
        elif len(specialLevels) == len(baseTiles):
            minLevel, maxLevel = UPPER_LIMIT, LOWER_LIMIT
            for level in specialLevels:
                minLevel = min(level, minLevel)
                maxLevel = max(level, maxLevel)
            if maxLevel - minLevel < 1:
                return True, maxLevel
        return False, level
                    
    """
    The given spriteInfo must contain mapRect, level and z attributes.  Typically this
    object will be the sprite itself, but for ease of unit testing it can be anything.
    """
    def getMasks(self, spriteInfo):
        spriteTiles = self.getRectTiles(spriteInfo.mapRect)
        # baseY = (spriteRect.bottom - 1) // view.TILE_SIZE
        # masks is a map of lists, keyed on the associated tile points
        masks = {}
        for tile in spriteTiles:
            tileMasks = tile.getMasks(spriteInfo.level, spriteInfo.z)
            if tileMasks:
                masks[(tile.x, tile.y)] = tileMasks
        return masks
    
    def getRectTiles(self, rect):
        rectTiles = []
        x1, y1 = self.convertTopLeft(rect.left, rect.top)
        x2, y2 = self.convertBottomRight(rect.right - 1, rect.bottom - 1)
        for x in range (x1, x2 + 1):
            for y in range (y1, y2 + 1):
                rectTiles.append(self.mapTiles[x][y])
        return rectTiles

    def convertTopLeft(self, px, py):
        return max(0, px // TILE_SIZE), max(0, py // TILE_SIZE)
        
    def convertBottomRight(self, px, py):
        return min(self.cols - 1, px // TILE_SIZE), min(self.rows - 1, py // TILE_SIZE)

"""
A repository of named tile images.  Instances of this class are created and used
whenever a new map is loaded from disk.
"""
class TileSet:
    
    def __init__(self, tiles):
        self.tiles = tiles

    def getTile(self, name):
        if name in self.tiles:
            return self.tiles[name]
        return None
    
"""
Represents a single tile on an RpgMap.
"""
class MapTile:
    
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.levels = []
        self.specialLevels = []
        self.tiles = []
        self.masks = []
        
    def addLevel(self, level):
        self.levels.append(level)
        
    def addSpecialLevel(self, level):
        self.specialLevels.append(level)
        
    def addTile(self, tile):
        self.tiles.append(tile)
        
    def addMask(self, tileIndex, level, flat = True):
        self.masks.append(MaskInfo(tileIndex, level, flat, self.y))
        
    def createTileImage(self):
        if len(self.tiles) == 0:
            return None
        elif len(self.tiles) > 1:
            # if we're layering more than one image we don't want to draw on any of
            # the original images because that will affect every copy
            tileImage = view.createRectangle((TILE_SIZE, TILE_SIZE), view.BLACK)
            for image in self.tiles:
                tileImage.blit(image, (0, 0))
            return tileImage
        return self.tiles[0]
    
    def getSpecialLevel(self, level):
        nearestLevel = None
        difference = UPPER_LIMIT
        for sl in self.specialLevels:
            testDifference = abs(sl - level)
            if testDifference < difference:
                difference = testDifference
                nearestLevel = sl
        if difference < 1:
            return nearestLevel
        return None
    
    def getMasks(self, spriteLevel, spriteZ):
        if len(self.masks) == 0:
            return None
        masks = []
        for maskInfo in self.masks:
            if maskInfo.z > spriteZ:
                if maskInfo.flat and maskInfo.level == spriteLevel:
                    continue
                masks.append(self.tiles[maskInfo.tileIndex])
        if len(masks) > 0:
            return masks
        return None
        
    def __str__(self):
        result = "<MapTile:\
         [" + str(self.x) + "," + str(self.y) + "]\
         tiles=" + str(len(self.tiles)) + "\
         levels=" + str(self.levels) + "\
         specialLevels=" + str(self.specialLevels) + "\
         masks=" + str(self.masks) + "\
        >"       
        return result

"""
Encapsulates information required for masking. 
"""
class MaskInfo:
    def __init__(self, tileIndex, level, flat, y):
        self.level = level
        self.flat = flat
        self.tileIndex = tileIndex
        self.z = (y + 1) * TILE_SIZE + level * TILE_SIZE - 1
            