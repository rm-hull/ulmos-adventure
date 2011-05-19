#!/usr/bin/env python

import view

from view import DOWN

class SpriteFrames:
    
    def __init__(self, frameSkip):
        self.frameSkip = frameSkip
        self.frameCount = 0
        self.frameIndex = 0

    def advanceFrame(self, increment = 1):
        if increment:
            self.frameCount = (self.frameCount + increment) % self.frameSkip
            if self.frameCount == 0:
                self.frameIndex = (self.frameIndex + 1) % self.numFrames
        return self.getCurrentFrame()
    
    def getCurrentFrame(self):
        pass       
    
    def repairLastFrame(self):
        pass
    
class StaticFrames(SpriteFrames):
    
    def __init__(self, animationFrames, frameSkip):
        SpriteFrames.__init__(self, frameSkip)
        self.virginAnimationFrames = animationFrames
        self.animationFrames = view.copyStaticFrames(animationFrames)
        self.numFrames = len(self.animationFrames)
        self.lastFrameIndex = self.frameIndex

    def getCurrentFrame(self):
        return self.animationFrames[self.frameIndex]

    def repairLastFrame(self):
        lastImage = self.animationFrames[self.lastFrameIndex]
        lastImage.blit(self.virginAnimationFrames[self.lastFrameIndex], (0, 0))
        self.lastFrameIndex = self.frameIndex


class DirectionalFrames(SpriteFrames):
    
    def __init__(self, animationFrames, frameSkip):
        SpriteFrames.__init__(self, frameSkip)
        self.virginAnimationFrames = animationFrames
        self.animationFrames = view.copyMovementFrames(animationFrames)
        self.direction = DOWN
        self.numFrames = len(animationFrames[self.direction])
        self.lastDirection = self.direction
        self.lastFrameIndex = self.frameIndex

    def getCurrentFrame(self):
        return self.animationFrames[self.direction][self.frameIndex]

    def repairLastFrame(self):
        lastImage = self.animationFrames[self.lastDirection][self.lastFrameIndex]
        lastImage.blit(self.virginAnimationFrames[self.lastDirection][self.lastFrameIndex], (0, 0))
        self.lastDirection, self.lastFrameIndex = self.direction, self.frameIndex
        
