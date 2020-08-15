#!/usr/bin/env python

print("Loading Luma.LCD Nokia 5110 Screen")
import math
import time
from input import *


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
font = ImageFont.truetype("assets/font2.ttf",10)
titlefont = ImageFont.truetype("assets/font.ttf",8)

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
if configure.pc:
	device = pygame(width = 84, height = 48, mode = "1")
else:
	serial = spi(port = SPI_PORT, device = SPI_DEVICE, gpio_DC = DC, gpio_RST = RST)
	device = pcd8544(serial)
	device.contrast(50)

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

	def __init__(self,draw, input):
		self.input = input
		self.auto = configure.auto
		self.interval = timer()
		self.interval.logtime()
		self.draw = draw
		self.definetitle()
		self.layout()
		self.graphcycle = 0
		self.decimal = 1
		self.selection = 0

		self.divider = 47

		self.A_Graph = graphlist((-40,85),(4,8),(self.divider,11),self.graphcycle)

		self.B_Graph = graphlist((300,1100),(4,21),(self.divider,11),self.graphcycle)

		self.C_Graph = graphlist((0,100),(4,34),(self.divider,11),self.graphcycle)

	def definetitle(self):
		self.string = "MULTISCAN"

	#  draws the title and sets the appropriate top bar length to fill the gap.
	def layout(self):

		self.title = LabelObj(self.string,titlefont,self.draw)
		self.titlesizex, self.titlesizey = self.title.getsize()
		self.barlength = (79 - (4+ self.titlesizex)) + 2

	# this function updates the graph for the screen
	def graphs(self):

		if self.selection == 0 or self.selection == 1:
			self.C_Graph.update(self.C_Data)
			self.C_Graph.render(self.draw)

		if self.selection == 0 or self.selection == 2:
			self.A_Graph.update(self.A_Data)
			self.A_Graph.render(self.draw)

		if self.selection == 0 or self.selection == 3:
			self.B_Graph.update(self.B_Data)
			self.B_Graph.render(self.draw)

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

		raw_a = str(self.A_Data)
		print("raw a is ", raw_a)
		adjusted_a = self.arrangelabel(raw_a)
		a_string = adjusted_a + self.sensors[configure.sensor1[0]][4]

		self.temLabel = LabelObj(a_string,font,self.draw)
		self.temLabel.push(self.titlex,7)


		raw_b = str(self.B_Data)
		adjusted_b = self.arrangelabel(raw_b)
		b_string = adjusted_b + " " + self.sensors[configure.sensor2[0]][4]

		self.baroLabel = LabelObj(b_string,font,self.draw)
		self.baroLabel.push(self.titlex,22)

		rawhumi = str(self.humi)
		adjustedhumi = self.arrangelabel(rawhumi)
		humistring = adjustedhumi + "%"

		self.humiLabel = LabelObj(humistring,font,self.draw)
		self.humiLabel.push(self.titlex,35)


	#push the image frame and contents to the draw object.
	def push(self,sensors):
		self.A_Data = sensors[configure.sensor1[0]][0]
		self.B_Data = sensors[configure.sensor2[0]][0]
		self.C_Data = sensors[configure.sensor3[0]][0]
		self.pres = sensors[1][0]
		self.humi = sensors[2][0]

		#Draw the background
		self.draw.rectangle((3,7,83,45),fill="white")

		#Top Bar - Needs to be scaled based on title string size.
		self.draw.rectangle((2,0,self.barlength,6), fill="black")

		self.title.push(self.barlength + 2,-1)
		self.sensors = sensors
		#self.sense()
		self.graphs()
		self.labels()

		status  = "mode_a"

		keys = self.input.read()

		if keys[0]:
			if self.input.is_down(0):
				print("Input1")
				self.selection = self.selection + 1
				if self.selection > 3:
					self.selection = 0

		if keys[1]:
			if self.input.is_down(1):
				print("Input2")
				status  = "mode_b"


		if keys[2]:
			if self.input.is_down(2):
				print("Input3")
				status = "settings"
				configure.last_status[0] = "mode_a"

		return status

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
		self.image = Image.open('assets/frame.ppm').convert('1')
		self.draw = ImageDraw.Draw(self.image)


		self.frame = MultiFrame(self.draw,self.input)
		#self.graph = graphlist


	def push(self,sensors):

		self.frame.push(sensors)
		self.input.read()
		self.pixdrw()
		return "mode_a"

	def pixdrw(self):

		im = self.image.convert("L")
		im = PIL.ImageOps.invert(im)
		im = im.convert("1")

		if configure.pc:
			device.display(self.image)
		else:
			device.display(im)
