#!/usr/bin/env python

from base.view import *

from pygame.transform import scale

SCALAR = 2

TILE_SIZE = 16 * SCALAR

# 0, 51, 102, 153, 204, 255
TRANSPARENT_COLOUR = GREEN
TRANSPARENT_COLOUR_WITH_ALPHA = (0, 255, 0, 255)

UP = 1
DOWN = 2
LEFT = 4
RIGHT = 8

OFFSET = 16

DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

SPRITES_FOLDER = "sprites"

def createMaskTile(originalImage = None):
    dimensions = (TILE_SIZE, TILE_SIZE)
    if originalImage == None:
        return createRectangle(dimensions, TRANSPARENT_COLOUR)
    else:        
        # we don't use the normal transparent colour here because we're creating a
        # transparent mask so we need to preserve the green pixels
        maskImage = createRectangle(dimensions, RED)
        maskImage.set_colorkey(RED, RLEACCEL)
        for px in range(originalImage.get_width()):
            for py in range(originalImage.get_height()):
                point = (px, py)
                # print "(%d, %d) : %s" % (px, py, originalImage.get_at((px, py)))
                if originalImage.get_at(point) == TRANSPARENT_COLOUR_WITH_ALPHA:
                    pass
                else:
                    maskImage.set_at(point, TRANSPARENT_COLOUR)
        return maskImage
            
def loadScaledImage(imagePath, colourKey = None, scalar=SCALAR):
    img = loadImage(imagePath, colourKey)
    return scale(img, (img.get_width() * scalar, img.get_height() * scalar))
        
def createDuplicateSpriteImage(spriteImage):
    # transparency is set on the duplicate - this allows us to draw over
    # the duplicate image with areas that are actually transparent
    # img = spriteImage.convert(spriteImage.image)
    img = createRectangle((spriteImage.get_width(), spriteImage.get_height()))
    img.blit(spriteImage, (0, 0))
    img.set_colorkey(TRANSPARENT_COLOUR, RLEACCEL)
    return img

def createBaseRectImage(baseRect):
    return createRectangle((baseRect.width, baseRect.height), RED)

# process animation frames from the composite image
def loadAnimationFrames(framesImage, numFrames=4):
    # work out width + height
    framesRect = framesImage.get_rect()
    width = framesRect.width // numFrames
    height = framesRect.height // len(DIRECTIONS)
    # map of image lists for animation keyed on direction
    animationFrames = {}
    for row in range(len(DIRECTIONS)):
        frames, originalFrames = [], []
        rowOffsetY = row * height
        for i in range(numFrames):
            img = framesImage.subsurface((i * width, rowOffsetY), (width, height))
            originalFrames.append(img)
            frames.append(createDuplicateSpriteImage(img))
        direction = DIRECTIONS[row]
        animationFrames[direction] = frames
        animationFrames[direction + OFFSET] = originalFrames
    return animationFrames

# process animation frames from the composite image
def loadStaticFrames(framesImage, numFrames=4):
    framesRect = framesImage.get_rect()
    width = framesRect.width // numFrames
    height = framesRect.height
    # map of image lists for animation
    animationFrames = {}
    frames, originalFrames = [], []
    for i in range(numFrames):
        img = framesImage.subsurface((i * width, 0), (width, height))
        originalFrames.append(img)
        frames.append(createDuplicateSpriteImage(img))
        animationFrames[0] = frames
        animationFrames[1] = originalFrames
    return animationFrames
    