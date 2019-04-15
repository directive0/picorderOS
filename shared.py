#!/usr/bin/python

#this file contains behaviours needed by most objects. I've broken them out for optimization.




# The following class is used to display text
class Label(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        #self.color = white
        self.fontSize = 33
        self.myfont = pygame.font.Font(titleFont, self.fontSize)
        
    def update(self, content, fontSize, nx, ny, fontType, color):
        self.x = nx
        self.y = ny
        self.content = content
        self.fontSize = fontSize
        self.myfont = pygame.font.Font(fontType, self.fontSize)
        self.color = color
        
    def draw(self, surface):
        label = self.myfont.render(self.content, 1, self.color)
        surface.blit(label, (self.x, self.y))

# the following class is used to display images
class Image(object):
    def __init__(self):
        self.x = 258
        self.y = 66
        #self.Img = blueInsignia
        
    def update(self, image, nx, ny):
        self.x = nx
        self.y = ny
        self.Img = image

        
    def draw(self, surface):
        surface.blit(self.Img, (self.x,self.y))
