
import pygame
from main import *

# The following lists are for my colour standards.
red = (255,0,0)
green = (106,255,69)
blue = (99,157,255)
yellow = (255,221,5)
black = (0,0,0)
white = (255,255,255)

# The following lists/objects are for UI elements.
titleFont = "assets/babs.otf"
titleFont = "assets/babs.otf"
blueInsignia = pygame.image.load('assets/insigniablue.png')
backplane = pygame.image.load('assets/background.png')
backgraph = pygame.image.load('assets/backgraph.png')
slider = pygame.image.load('assets/slider.png')
sliderb = pygame.image.load('assets/slider2.png')
status = "startup"


# If testing on PC use these imports:
from gpiodummy import *
from getcpu import *
from screens import *
from graph import *

# The following class is used to display text
class Label(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.color = white
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
        self.Img = blueInsignia
        
    def update(self, image, nx, ny):
        self.x = nx
        self.y = ny
        self.Img = image

        
    def draw(self, surface):
        surface.blit(self.Img, (self.x,self.y))



# the following function plots the environment sensors to an onscreen graph

def graphScreen(surface,humidGraph,tempGraph,pressGraph,moire,tock,graphinit,buttons,csvfile,rot):
      status = "graphgo"   
      drawinterval = 1 #64
      senseinterval = 10
      #337
      
      # Because the graph screen is slow to update it needs to pop a reading onto screen as soon as it is initiated I draw a value once and wait for the interval to lapse for the next draw. Once the interval has lapsed pop another value on screen.

      moire.animate()   
      
      if (graphinit.get() == 0) or (tock.timelapsed() >= drawinterval):  
          #Sets a black screen ready for our UI elements      
          surface.fill(black)
    
          #draws Background gridplane
          graphback = Image()
          graphback.update(backgraph, 0, 0)
          graphback.draw(surface) 
      
          #instantiates 3 labels for our readout
          templabel = Label()
          humidlabel = Label()
          presslabel = Label()
          intervallabel = Label()
          intervallabelshadow = Label()
          
          
          slider1 = Image()
          slider2 = Image()
          slider3 = Image()


          #gets our data
          senseData = sensorget()
          csvfile.logvalues(senseData)
          
          #parses dictionary of data from sensor/weather.
      
          #converts humid data to float
          humidData = float(senseData['humidity'])
          #scales the data to the limits of our screen
          humidgraph = translate(humidData, 0, 100, 204, 17)
          #grabs a simple 61 wide tuple for our values
          humidbuffer = humidGraph.grablist()

          #puts a new sensor value at the end 
          humidbuffer.append(humidgraph)
          #pop the oldest value off
          humidbuffer.pop(0)
      
          #preps the list by adding the X coordinate to every sensor value
          humidcords = humidGraph.graphprep(humidbuffer)
            
          #repeat for each sensor

          tempData = float(senseData['temp'])
          tempgraph = translate(tempData, -40, 120, 204, 17)
          tempbuffer = tempGraph.grablist()
          tempbuffer.append(tempgraph)
          tempbuffer.pop(0)
          tempcords = tempGraph.graphprep(tempbuffer)
      
          pressData = float(senseData['pressure'])
          pressgraph = translate(pressData, 260, 1260, 204, 17)
          pressbuffer = pressGraph.grablist()
          pressbuffer.append(pressgraph)
          pressbuffer.pop(0)
          presscords = pressGraph.graphprep(pressbuffer)
          
          tempcontent = str(int(tempData))
          templabel.update(tempcontent + "\xb0" + " c",30,35,205,titleFont,red)
          presscontent = str(int(pressData))
          presslabel.update(presscontent + " hpa",30,114,205,titleFont,yellow)
          humidcontent = str(int(humidData))
          humidlabel.update(humidcontent + " %",30,246,205,titleFont,green)
          #templabel.update(tempData + "\xb0",16,15,212,titleFont,yellow)
          
          setting = str(float(drawinterval))
          intervaltext = (setting + ' sec')
          interx= (22)
          intery= (21)
         # intervallabel.update("~"+setting + " Hrs",30,22,167,titleFont,white)
          #intervallabelshadow.update(setting + " Hrs",30,24,169,titleFont,(100,100,100))
          intervallabel.update(intervaltext,30,interx,intery,titleFont,white)
          intervallabelshadow.update(intervaltext, 30, interx + 2, intery + 2 ,titleFont,(100,100,100))
          
          tempslide = translate(senseData['temp'], -40, 120, 194, 7)
          pressslide = translate(senseData['pressure'], 260, 1260, 194, 7)
          humidslide = translate(senseData['humidity'], 0, 100, 194, 7)
          
          slider1.update(sliderb, 283, tempslide)
          slider2.update(sliderb, 283, pressslide)  
          slider3.update(sliderb, 283, humidslide)

              
          #draw the lines

          pygame.draw.lines(surface, red, False, tempcords, 3)
          pygame.draw.lines(surface, green, False, humidcords, 3)
          pygame.draw.lines(surface, yellow, False, presscords, 3)
          
          templabel.draw(surface)
          presslabel.draw(surface)
          humidlabel.draw(surface)
          intervallabelshadow.draw(surface)          
          intervallabel.draw(surface)

          #draws UI to frame buffer


          slider1.draw(surface)
          slider2.draw(surface)
          slider3.draw(surface)
          
          if (rot.read() == True):
              surface.blit(pygame.transform.rotate(surface, 180), (0, 0))
          
          pygame.display.flip()
          
          if (graphinit.get() == 0):
              graphinit.logstart()
          
          if (tock.timelapsed() >= 10):
              tock.logtime()

      #status = "graphgo"    
      #returns state to main loop
      
      status = butswitch(status,graphinit,moire,rot,buttons)
      
      #button_readings = buttons.read()

      
      
      #returns state to main loop
      return status
