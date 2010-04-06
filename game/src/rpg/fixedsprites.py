#!/usr/bin/env python

from sprites import *

from view import VIEW_WIDTH

"""
Defines a sprite that is fixed on the game display.  Note that this class of
sprites does not extend RpgSprite. 
"""
class FixedSprite(pygame.sprite.Sprite):

    def __init__(self, image, position = (0, 0)):
        # pygame.sprite.Sprite.__init__(self, self.containers)
        pygame.sprite.Sprite.__init__(self)
        # properties common to all FixedSprites
        self.position = [i * SCALAR for i in position]
        self.setImage(image)
        
    def setImage(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.move_ip(self.position[0], self.position[1])
        

class FixedCoin(FixedSprite):

    initialImage = None
    
    def __init__(self, position = (0, 0)):
        if self.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "small-coin.png")
            self.initialImage = view.loadScaledImage(imagePath, None)
        FixedSprite.__init__(self,
                             view.createDuplicateSpriteImage(self.initialImage),
                             position)

class CoinCount(FixedSprite):
    
    initialImage = None
    
    def __init__(self, position = (0, 0)):
        if self.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "numbers.png")
            self.initialImage = view.loadScaledImage(imagePath, None)
        self.numbers = view.processStaticFrames(self.initialImage, 10)        
        FixedSprite.__init__(self, self.numbers[0], position)
        self.count = 0;
        
    def incrementCount(self, increment = 1):
        self.count += increment
        self.newImage()
        
    def newImage(self):
        countString = str(self.count)
        dimensions = (len(countString) * 8 * SCALAR, 8 * SCALAR)
        newImage = view.createTransparentRect(dimensions)
        newImage.set_colorkey(view.TRANSPARENT_COLOUR, view.RLEACCEL)
        px = 0;
        for n in countString:
            newImage.blit(self.numbers[int(n)], (px, 0))
            px += 8 * SCALAR
        self.setImage(newImage)

class KeyCount(FixedSprite):
    
    initialImage = None
    
    def __init__(self, position = (0, 0)):
        FixedSprite.__init__(self, view.createTransparentRect((0, 8)), position)
        if self.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "small-key.png")
            self.initialImage = view.loadScaledImage(imagePath, None)
        self.keyImage = view.createDuplicateSpriteImage(self.initialImage)
        self.count = 0;
        
    def incrementCount(self, increment = 1):
        self.count += increment
        self.newImage()
        
    def newImage(self):        
        # countString = str(self.count)
        dimensions = (self.count * 8 * SCALAR, 8 * SCALAR)
        newImage = view.createTransparentRect(dimensions)
        px = 0;
        for n in range(self.count):
            newImage.blit(self.keyImage, (px, 0))
            px += 8 * SCALAR
        self.setImage(newImage)
        self.rect.left = VIEW_WIDTH - (3 + self.count * 8) * SCALAR
   