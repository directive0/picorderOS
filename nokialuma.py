#!/usr/bin/env python


import math
import time
from input import *

#import Adafruit_Nokia_LCD as LCD
#import Adafruit_GPIO.SPI as SPI
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import pcd8544
from luma.emulator.device import pygame

# Load up the image library stuff to help draw bitmaps to push to the screen
import PIL.ImageOps
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# load the module that draws graphs
from pilgraph import *


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
#disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))
if configure.pc:
	device = pygame(width = 84, height = 48, mode = "1")
else:
	serial = spi(port = SPI_PORT, device = SPI_DEVICE, gpio_DC = DC, gpio_RST = RST)
	device = pcd8544(serial)
	device.contrast(50)

# Initialize library.
#disp.begin(contrast=50)

# Clear display.
#disp.clear()
#disp.display()

fore_col = 0
back_col = 1

# Controls text objects drawn to the LCD
class LabelObj(object):
	def __init__(self,string,font,draw):
		self.font = font
		self.draw = draw
		self.string = string

	def push(self,locx,locy):
		self.draw.text((locx, locy), self.string, font = self.font, fill= fore_col)

	def getsize(self):
		size = self.draw.textsize(self.string, font=self.font)
		return size


# Controls the LCARS frame, measures the label and makes sure the top frame bar has the right spacing.
class MultiFrame(object):

	def __init__(self,draw):
		self.auto = configure.auto
		self.interval = timer()
		self.interval.logtime()
		self.draw = draw
		self.definetitle()
		self.layout()
		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47

		# graphlist((lower,upperrange),(x1,y1),(span),cycle?)
		self.tempGraph = graphlist((-40,85),(4,8),(self.divider,11),self.graphcycle)
		#tempGraph.auto

		self.baroGraph = graphlist((300,1100),(4,21),(self.divider,11),self.graphcycle)
		#baroGraph.auto

		self.humidGraph = graphlist((0,100),(4,34),(self.divider,11),self.graphcycle)
		#humidGraph.auto

		#print(self.humidGraph.giveperiod())

	def definetitle(self):
		self.string = "MULTISCAN"

	#  draws the title and sets the appropriate top bar length to fill the gap.
	def layout(self):

		self.title = LabelObj(self.string,titlefont,self.draw)
		self.titlesizex, self.titlesizey = self.title.getsize()
		self.barlength = (79 - (4+ self.titlesizex)) + 2

	# this function grabs the sensor values and puts them in an object for us to use.
	def sense(self):
		pass

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

		self.titlex = self.divider + 7

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


	#push the image frame and contents to the draw object.
	def push(self,sensors):
		self.temp = sensors[0][0]
		self.pres = sensors[1][0]
		self.humi = sensors[2][0]

		#Draw the background
		self.draw.rectangle((3,7,83,45),fill="white")

		#Top Bar - Needs to be scaled based on title string size.
		self.draw.rectangle((2,0,self.barlength,6), fill="black")

		self.title.push(self.barlength + 2,-1)

		self.sense()
		self.graphs()
		self.labels()

# governs the screen drawing of the entire program. Everything flows through Screen.
# Screen instantiates a draw object and passes it the image background.
# Screen monitors button presses and passes flags for interface updates to the draw object.

class NokiaScreen(object):

	def __init__(self):


		self.input = Inputs()
		#---------------------------IMAGE LIBRARY STUFF------------------------------#
		# Create image buffer.
		# Load the background LCARS frame
		#image = Image.open('frame.ppm')#.convert('1')



		# instantiates an image and uses it in a draw object.
		self.image = Image.open('frame.ppm').convert('1')
		self.draw = ImageDraw.Draw(self.image)


		self.frame = MultiFrame(self.draw)
		#self.graph = graphlist


	def push(self,sensors):



		self.frame.push(sensors)
		self.input.read()
		self.pixdrw()

	def pixdrw(self):
		#pass
		#with canvas(device) as draw:
		#invert_image = PIL.ImageOps.invert(self.image)
		im = self.image.convert("L")
		im = PIL.ImageOps.invert(im)
		im = im.convert("1")

		if configure.pc:
			device.display(self.image)
		else:
			device.display(im)

		#invert_image = PIL.ImageOps.invert(self.image)
		#disp.image(self.image)
		#disp.display()
