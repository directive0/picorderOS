#!/usr/bin/env python


import math
import time

#import Adafruit_Nokia_LCD as LCD
#import Adafruit_GPIO.SPI as SPI
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from luma.emulator.device import pygame

# Load up the image library stuff to help draw bitmaps to push to the screen
import PIL.ImageOps
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# load the module that draws graphs
from pilgraph import *
from amg8833_pil import *


# Load default font.
font = ImageFont.truetype("assets/babs.otf",13)
titlefont = ImageFont.truetype("assets/babs.otf",16)

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
	device = pygame(width = 160, height = 128, mode = "RGB")
else:
	serial = spi(port = SPI_PORT, device = SPI_DEVICE, gpio_DC = DC, gpio_RST = RST)
	device = st7735(serial, width = 160, height = 128, mode = "RGB")
# Initialize library.
#disp.begin(contrast=50)

# Clear display.
#disp.clear()
#disp.display()

# The following are for LCARS colours from LCARScom.net
lcars_orange = (255,153,0)
lcars_pink = (204,153,204)
lcars_blue = (153,153,204)
lcars_red = (204,102,102)
lcars_peach = (255,204,153)
lcars_bluer = (153,153,255)
lcars_orpeach = (255,153,102)
lcars_pinker = (204,102,153)

fore_col = 0
back_col = 1

# Controls text objects drawn to the LCD
class LabelObj(object):
	def __init__(self,string,font,draw, colour = lcars_blue):
		self.font = font
		self.draw = draw
		self.string = string
		self.colour = colour

	def center(self,y,x,w):
		size = self.font.getsize(self.string)
		xmid = x + w/2
		#ymid = y + h/2
		textposx = xmid - (size[0]/2)
		#textposy = ymid - (size[1]/2) + self.scaler
		self.push(textposx,y)

	def r_align(self,x,y):
		size = self.font.getsize(self.string)
		self.push(x-size[0],y)

	# def update(self, string = self.string, colour = self.colour):
	# 	self.string = string
	# 	self.colour = colour
	# 	pass

	def push(self,locx,locy):
		self.draw.text((locx, locy), self.string, font = self.font, fill= self.colour)

	def getsize(self):
		size = self.draw.textsize(self.string, font=self.font)
		return size


# Controls the LCARS frame, measures the label and makes sure the top frame bar has the right spacing.
class MultiFrame(object):

	def __init__(self):#,draw):
		self.graphx = 23
		self.graphy = 24
		self.gspanx = 133
		self.gspany = 71
		self.back = Image.open('assets/lcarsframe.png')
		self.auto = True
		self.interval = timer()
		self.interval.logtime()
		#self.draw = draw
		self.titlex = 23
		self.titley = 6
		self.labely = 102

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47

		#self.temLabel = LabelObj("default",titlefont,self.draw, colour = lcars_orange)

		# graphlist((lower,upperrange),(x1,y1),(span),cycle?)
		self.tempGraph = graphlist((-40,85),(self.graphx,self.graphy),(self.gspanx,self.gspany),self.graphcycle, colour = lcars_orange, width = 1)
		#tempGraph.auto

		self.baroGraph = graphlist((300,1100),(self.graphx,self.graphy),(self.gspanx,self.gspany),self.graphcycle, colour = lcars_blue, width = 1)
		#baroGraph.auto

		self.humidGraph = graphlist((0,100),(self.graphx,self.graphy),(self.gspanx,self.gspany),self.graphcycle, colour = lcars_pinker, width = 1)
		#humidGraph.auto

		#self.cam = ThermalGrid(23,24,135,71,surface)
		#print(self.humidGraph.giveperiod())

	def definetitle(self):
		self.string = "MULTI-GRAPH"

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

		self.baroGraph.update(self.pres)
		self.baroGraph.render(self.draw, self.auto)

		self.tempGraph.update(self.temp)
		self.tempGraph.render(self.draw, self.auto)

	# this function takes a value and sheds the second digit after the decimal place
	def arrangelabel(self,data):

		datareturn = format(float(data), '.0f')
		return datareturn

	def datatext(self):
		pass


	# this function defines the labels for the screen
	def labels(self,sensors):

		#degreesymbol =  u'\N{DEGREE SIGN}'
		rawtemp = str(self.temp)
		adjustedtemp = self.arrangelabel(rawtemp)
		tempstring = adjustedtemp + sensors[0][4]

		self.temLabel = LabelObj(tempstring,font,self.draw,colour = lcars_orange)
		self.temLabel.push(23,self.labely)


		rawbaro = str(self.pres)
		adjustedbaro = self.arrangelabel(rawbaro)
		barostring = adjustedbaro + " " + sensors[1][4]

		self.baroLabel = LabelObj(barostring,font,self.draw, colour = lcars_blue)
		self.baroLabel.center(self.labely,23,135)
		#self.baroLabel.push(57,100)

		rawhumi = str(self.humi)
		adjustedhumi = self.arrangelabel(rawhumi)
		humistring = adjustedhumi + sensors[2][4]

		self.humiLabel = LabelObj(humistring,font,self.draw, colour = lcars_pinker)
		#self.humiLabel.push(117,100)
		self.humiLabel.r_align(156,self.labely)

	#push the image frame and contents to the draw object.
	def push(self,sensors,draw):
		self.draw = draw
		#self.draw.paste((0,0),self.back)


		self.humi = sensors[2][0]
		self.pres = sensors[1][0]
		self.temp = sensors[0][0]
		#Draw the background
		#self.draw.rectangle((15,8,150,120),fill="black")
		#self.draw.paste(self.back)

		#Top Bar - Needs to be scaled based on title string size.
		#self.draw.rectangle((2,0,self.barlength,6), fill="black")
		self.definetitle()
		self.layout()
		self.title.push(self.titlex,self.titley)

		self.sense()
		self.graphs()
		self.labels(sensors)

# governs the screen drawing of the entire program. Everything flows through Screen.
# Screen instantiates a draw object and passes it the image background.
# Screen monitors button presses and passes flags for interface updates to the draw object.

class ThermalFrame(object):
	pass


class ColourScreen(object):

	def __init__(self):

		#---------------------------IMAGE LIBRARY STUFF------------------------------#

		# instantiates an image and uses it in a draw object.
		self.image = Image.open('assets/lcarsframe.png')#.convert('1')


		self.cam = ThermalGrid(23,24,135,71)
		self.frame = MultiFrame()#self.draw)

		#self.cam = ThermalGrid(32,32,256,168,surface)
		#self.graph = graphlist


	def push(self,sensors):

		self.newimage = self.image.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		self.frame.push(sensors,self.draw)


		self.pixdrw()

	def pixdrw(self):
		#self.draw = ImageDraw.Draw(self.image)
		#self.cam.update(self.draw)
		thisimage = self.newimage.convert(mode = "RGB")
		device.display(thisimage)
		#invert_image = PIL.ImageOps.invert(self.image)
		#disp.image(self.image)
		#disp.display()
