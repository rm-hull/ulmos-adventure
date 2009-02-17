#!/usr/bin/env python

from pygame.transform import scale

from base import *

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

# process animation frames from the composite image
def processMovementFrames(framesImage, numFrames=4):
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
def processStaticFrames(framesImage, numFrames=4):
    framesRect = framesImage.get_rect()
    width = framesRect.width // numFrames
    height = framesRect.height
    # map of images for animation
    animationFrames = []
    for i in range(numFrames):
        img = framesImage.subsurface((i * width, 0), (width, height))
        animationFrames.append(createDuplicateSpriteImage(img))
    return animationFrames

def createBaseRectImage(baseRect):
    return createRectangle((baseRect.width, baseRect.height), RED)
    