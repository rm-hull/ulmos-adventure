#! /usr/bin/env python

from view import UP, DOWN, LEFT, RIGHT, TILE_SIZE

MAP_NOT_FOUND = (None, 0)

mapInfo = {}

mapInfo["demo"] = {UP: {(0, 4): ("demo", 2), (4, 8): ("skulls", 4)}, 
                   DOWN: {(0, 8): ("demo", 0)},
                   LEFT: {(0, 8): ("demo", 0)},
                   RIGHT: {(0, 8): ("demo", 0)}}

mapInfo["skulls"] = {DOWN: {(4, 12): ("demo", -4)}}

def getNextMap(currentMapName, boundary, baseRect):
    if currentMapName in mapInfo:
        if boundary in mapInfo[currentMapName]:
            tileRange = getTileRange(boundary, baseRect)
            # print tileRange
            boundaryInfo = mapInfo[currentMapName][boundary]
            for mapTuple in boundaryInfo.keys():
                mapRange = range(mapTuple[0], mapTuple[1])
                # print mapRange
                testList = [i in mapRange for i in tileRange]
                # print testList
                if False in testList:
                    pass
                else:
                    return boundaryInfo[mapTuple]
    return MAP_NOT_FOUND

def getTileRange(boundary, baseRect):
    x1, y1 = convertPixelPoint(baseRect.left, baseRect.top)
    x2, y2 = convertPixelPoint(baseRect.right, baseRect.bottom)
    print "(%s, %s) -> (%s, %s)" % (x1, y1, x2, y2)
    tileRange = None
    if boundary == UP or boundary == DOWN:
        tileRange = range(x1, x2 + 1)
    else:
        tileRange = range(y1, y2 + 1)
    return tileRange

def convertPixelPoint(px, py):
    return px // TILE_SIZE, py // TILE_SIZE
    