#!/usr/bin/env python


import math
import time

import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

# Load up the image library stuff to help draw bitmaps to push to the screen
import PIL.ImageOps
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# load the module supporting our sensors
from bme import *

# load the module that draws graphs
from graph import *

# load the module that monitors physical button presses
from gpiocontrol import *

# Load default font.
font = ImageFont.truetype("font2.ttf",10)
titlefont = ImageFont.truetype("font.ttf",8)

# Raspberry Pi hardware SPI config:
DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black hardware SPI config:
# DC = 'P9_15'
# RST = 'P9_12'
# SPI_PORT = 1
# SPI_DEVICE = 0

# Hardware SPI usage:
disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))

# Initialize library.
disp.begin(contrast=60)

# Clear display.
disp.clear()
disp.display()


# Controls text objects drawn to the LCD
class LabelObj(object):
    def __init__(self,string,font,draw):
        self.font = font
        self.draw = draw
        self.string = string

    def push(self,locx,locy):
        self.draw.text((locx, locy), self.string, font = self.font, fill=0)

    def getsize(self):
        size = self.draw.textsize(self.string, font=self.font)
        return size


# Controls the LCARS frame, measures the label and makes sure the top frame bar has the right spacing.
class MultiFrame(object):

    def __init__(self,draw):
        self.interval = timer()
        self.interval.logtime()
        self.draw = draw
        self.definetitle()
        self.layout()
        self.graphcycle = 0
        self.decimal = 1
        
        self.tempGraph = graphlist((-40,85),(4,8),(50,11),self.graphcycle)
        #tempGraph.auto
        
        self.baroGraph = graphlist((300,1100),(4,21),(50,11),self.graphcycle)
        #baroGraph.auto
        
        self.humidGraph = graphlist((0,100),(4,34),(50,11),self.graphcycle)
        #humidGraph.auto
        
        print(self.humidGraph.giveperiod())

    def definetitle(self):
        self.string = "MULTI(MET)"

    #  draws the title and sets the appropriate top bar length to fill the gap.
    def layout(self):
        
        self.title = LabelObj(self.string,titlefont,self.draw)
        self.titlesizex, self.titlesizey = self.title.getsize()
        self.barlength = (79 - (4+ self.titlesizex)) + 2
    
    # this function grabs the sensor values and puts them in an object for us to use.
    def sense(self):
        self.sensors = GetSensors()
        self.temp,self.pres,self.humi = self.sensors
        
    # this function updates the graph for the screen
    def graphs(self):

        self.humidGraph.update(self.humi)
        self.humidGraph.render(self.draw, self.auto)
        
        self.tempGraph.update(self.temp)
        self.tempGraph.render(self.draw, self.auto)
        
        self.baroGraph.update(self.pres)
        self.baroGraph.render(self.draw, self.auto)

    # this function takes a value and sheds the second digit after the decimal place
    def arrangelabel(self,data):
        data2 = data.split(".")
        dataa = data2[0]
        datab = data2[1]

        datadecimal = datab[0:self.decimal]
        
        datareturn = dataa + "." + datadecimal
        
        return datareturn
        
    # this function defines the labels for the screen
    def labels(self):
        
        self.titlex = 57
        
        degreesymbol =  u'\N{DEGREE SIGN}'
        rawtemp = str(self.temp)
        adjustedtemp = self.arrangelabel(rawtemp)
        tempstring = adjustedtemp + degreesymbol

        self.temLabel = LabelObj(tempstring,font,self.draw)
        self.temLabel.push(self.titlex,7)
        
        
        rawbaro = str(self.pres)
        adjustedbaro = self.arrangelabel(rawbaro)
        barostring = adjustedbaro
        
        self.baroLabel = LabelObj(barostring,font,self.draw)
        self.baroLabel.push(self.titlex,22)
        
        rawhumi = str(self.humi)
        adjustedhumi = self.arrangelabel(rawhumi)
        humistring = adjustedhumi + "%"
        
        self.humiLabel = LabelObj(humistring,font,self.draw)
        self.humiLabel.push(self.titlex,35)

 
    # this function checks for button presses and provides a means to the class of using these events.
    def input(self, buttons):
        self.buttonstate = buttons
        
        if self.buttonstate["geobut"] == 1:
            self.auto = True
        else:
            self.auto = False
        
    #push the image frame and contents to the draw object.
    def push(self):
        
        #Draw the background
        self.draw.rectangle((3,7,83,45),fill=255)
        
        #Top Bar - Needs to be scaled based on title string size.
        self.draw.rectangle((2,0,self.barlength,6), fill=0)
        
        self.title.push(self.barlength + 2,-1)
        
        self.sense()
        self.graphs()
        self.labels()
        
# governs the screen drawing of the entire program. Everything flows through Screen.
# Screen instantiates a draw object and passes it the image background.
# Screen monitors button presses and passes flags for interface updates to the draw object.

class Screen(object):

    def __init__(self):
        
        #---------------------------IMAGE LIBRARY STUFF------------------------------#
        # Create image buffer.
        # Load the background LCARS frame
        image = Image.open('frame.ppm').convert('1')



        # instantiates an image and uses it in a draw object.
        self.image = Image.open('frame.ppm').convert('1')
        self.draw = ImageDraw.Draw(self.image)
        
        
        self.frame = MultiFrame(self.draw)
        self.graph = graphlist
        self.buttonstate = buttonget()

    def push(self):
        
        # check on the state of buttons
        buttons = buttonget()
        
        self.frame.input(buttons)
        self.frame.push()
        
        self.pixdrw()

    def pixdrw(self):

        #invert_image = PIL.ImageOps.invert(self.image)
        disp.image(self.image)
        disp.display()

# Instantiate the multi screen
Screen1 = Screen() 



while True:
    Screen1.push()

