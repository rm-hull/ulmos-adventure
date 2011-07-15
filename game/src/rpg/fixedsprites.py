#!/usr/bin/env python

from sprites import *

from view import VIEW_WIDTH

"""
Defines a sprite that is fixed on the game display.  Note that this class of
sprite does not extend RpgSprite. 
"""
class FixedSprite(pygame.sprite.Sprite):

    def __init__(self, position = (0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.position = [i * SCALAR for i in position]
        
    def setImage(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.move_ip(self.position[0], self.position[1])
        
class FixedCoin(FixedSprite):

    initialImage = None
    
    def __init__(self, position = (0, 0)):
        if FixedCoin.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "small-coin.png")
            FixedCoin.initialImage = view.loadScaledImage(imagePath, None)
        FixedSprite.__init__(self, position)
        self.setImage(view.createDuplicateSpriteImage(FixedCoin.initialImage))

class CoinCount(FixedSprite):
    
    initialImage = None
    
    def __init__(self, count = 0, position = (0, 0)):
        if CoinCount.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "numbers.png")
            CoinCount.initialImage = view.loadScaledImage(imagePath, None)
        self.numbers = view.processStaticFrames(CoinCount.initialImage, 10)        
        FixedSprite.__init__(self, position)
        self.count = count;
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
        
    def incrementCount(self, n = 1):
        self.count += n
        self.newImage()
        print "coins:", self.count

class KeyCount(FixedSprite):
    
    initialImage = None
    
    def __init__(self, count = 0, position = (0, 0)):
        if KeyCount.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "small-key.png")
            KeyCount.initialImage = view.loadScaledImage(imagePath, None)
        self.keyImage = view.createDuplicateSpriteImage(KeyCount.initialImage)
        FixedSprite.__init__(self, position)
        self.count = count
        self.newImage()
        
    def newImage(self):
        dimensions = (self.count * 8 * SCALAR, 8 * SCALAR)
        newImage = view.createTransparentRect(dimensions)
        px = 0;
        for n in range(self.count):
            newImage.blit(self.keyImage, (px, 0))
            px += 8 * SCALAR
        self.setImage(newImage)
        self.rect.left = VIEW_WIDTH - (3 + self.count * 8) * SCALAR

    def incrementCount(self, n = 1):
        self.count += n
        self.newImage()
        print "keys:", self.count

class Lives(FixedSprite):
    
    initialImage = None
    
    def __init__(self, count = 0, position = (0, 0)):
        if Lives.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "life.png")
            Lives.initialImage = view.loadScaledImage(imagePath, None)
        self.livesImage = view.createDuplicateSpriteImage(Lives.initialImage)
        FixedSprite.__init__(self, position)
        self.count = count
        self.newImage()
        
    def newImage(self):
        dimensions = (self.count * 8 * SCALAR, 8 * SCALAR)
        newImage = view.createTransparentRect(dimensions)
        px = 0;
        for n in range(self.count):
            newImage.blit(self.livesImage, (px, 0))
            px += 8 * SCALAR
        self.setImage(newImage)

    def incrementCount(self, n = 1):
        self.count += n
        # temporary hack 
        if (self.count < 0):
            return
        self.newImage()
        print "lives:", self.count
        
    def noneLeft(self):
        return self.count < 0
   