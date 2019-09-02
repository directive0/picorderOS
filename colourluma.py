#!/usr/bin/env python


import math
import time
from input import *

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

class SelectableLabel(LabelObj):


	def __init__(self, oper, special = 0):

		# special determines the behaviour of the label for each type of oper
		# the class is supplied. There may be multiple types of int or boolean based
		# configuration parameters so this variable helps make new options
		self.special = special

		# coordinates
		self.x = 0
		self.y = 0

		# basic graphical parameters
		self.color = white
		self.fontSize = 33
		self.myfont = pygame.font.Font(titleFont, self.fontSize)
		text = "Basic Item"
		self.size = self.myfont.size(text)
		self.scaler = 3
		self.selected = False
		self.indicator = Image()
		self.content = "default"

		# this variable is a reference to a list stored in "objects.py"
		# containing either a boolean or an integer
		self.oper = oper

	def update(self, content, fontSize, nx, ny, fontType, color):
		self.x = nx
		self.y = ny
		self.content = content
		self.fontSize = fontSize
		self.myfont = pygame.font.Font(fontType, self.fontSize)
		self.color = color
		self.indicator.update(sliderb, nx - 23, ny+1)

	def toggle(self):

		# if the parameter supplied is a boolean
		if isinstance(self.oper[0], bool):
			#toggle its state
			self.oper[0] = not self.oper[0]

		#if the parameter supplied is an integer
		elif isinstance(self.oper[0], int):

			# increment the integer.
			self.oper[0] += 1

			# if the integer is larger than the pool
			if self.special == 1 and self.oper[0] > configure.max_sensors[0]-1:
				self.oper[0] = 0

			if self.special == 2 and self.oper[0] > (len(themes) - 1):
				self.oper[0] = 0

		return self.oper[0]

	def draw(self, surface):
		if self.selected:
			self.indicator.draw(surface)

		label = self.myfont.render(self.content, 1, self.color)


		status_text = "dummy"
		if self.special == 0:
			status_text = str(self.oper[0])
		elif self.special == 1:
			status_text = configure.sensor_info[self.oper[0]][3]
		elif self.special == 2:
			status_text = themenames[self.oper[0]]

		pos = resolution[0] - (self.get_size(status_text) + 37)
		state = self.myfont.render(status_text, 1, self.color)


		surface.blit(label, (self.x, self.y))
		surface.blit(state, (pos, self.y))


class SettingsFrame(object):
	def __init__(self,input):
		# Sets the topleft origin of the graph
		self.graphx = 23
		self.graphy = 24

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 71

		# sets the background image for the display
		self.back = Image.open('assets/lcarsframe.png')

		self.selection = 0

		self.input = Inputs()

		self.auto = configure.auto[0]
		self.interval = timer()
		self.interval.logtime()
		#self.draw = draw
		self.titlex = 23
		self.titley = 6
		self.labely = 102

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47

		# device needs to show multiple settings
		# first the sensor palette configuration

		self.titlelabel = Label()
		self.titlelabel.update("Control Panel",25,17,15,titleFont,orange)


		self.option1 = SelectableLabel(configure.sensor1, special = 1)
		self.option1.update("Graph 1: ",20,self.left_margin,47,titleFont,red)

		self.option2 = SelectableLabel(configure.sensor2, special = 1)
		self.option2.update("Graph 2: ", 20, self.left_margin, 68, titleFont, green)

		self.option3 = SelectableLabel(configure.sensor3, special = 1)
		self.option3.update("Graph 3: ", 20, self.left_margin, 90, titleFont, yellow)

		self.option4 = SelectableLabel(configure.theme, special = 2)
		self.option4.update("Theme:  ", 20, self.left_margin, 111, titleFont, orange)

		self.option5 = SelectableLabel(configure.auto)
		self.option5.update("Auto Range: ", 20, self.left_margin, 132, titleFont, orange)

		self.option6 = SelectableLabel(configure.leds)
		self.option6.update("LEDs: ", 20, self.left_margin, 154, titleFont, orange)

		self.option7 = SelectableLabel(configure.moire)
		self.option7.update("Moire: ", 20, self.left_margin, 176, titleFont, orange)

		self.options = [self.option1,self.option2, self.option3, self.option4, self.option5, self.option6, self.option7]


# Controls the LCARS frame, measures the label and makes sure the top frame bar has the right spacing.
class MultiFrame(object):

	def __init__(self,input):
		# Sets the topleft origin of the graph
		self.graphx = 23
		self.graphy = 24

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 71

		# sets the background image for the display
		self.back = Image.open('assets/lcarsframe.png')

		self.selection = 0

		self.input = Inputs()

		self.auto = configure.auto[0]
		self.interval = timer()
		self.interval.logtime()
		#self.draw = draw
		self.titlex = 23
		self.titley = 6
		self.labely = 102

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47

		#self.A_Label = LabelObj("default",titlefont,self.draw, colour = lcars_orange)

		# graphlist((lower,upperrange),(x1,y1),(span),cycle?)
		self.A_Graph = graphlist((-40,85),(self.graphx,self.graphy),(self.gspanx,self.gspany),self.graphcycle, colour = lcars_orange, width = 1)
		#A_Graph.auto

		self.B_Graph = graphlist((300,1100),(self.graphx,self.graphy),(self.gspanx,self.gspany),self.graphcycle, colour = lcars_blue, width = 1)
		#B_Graph.auto

		self.C_Graph = graphlist((0,100),(self.graphx,self.graphy),(self.gspanx,self.gspany),self.graphcycle, colour = lcars_pinker, width = 1)
		#C_Graph.auto

		#self.cam = ThermalGrid(23,24,135,71,surface)
		#print(self.C_Graph.giveperiod())

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

		self.C_Graph.update(self.C_Data)
		self.C_Graph.render(self.draw)

		self.B_Graph.update(self.B_Data)
		self.B_Graph.render(self.draw)

		self.A_Graph.update(self.A_Data)
		self.A_Graph.render(self.draw)

	# this function takes a value and sheds the second digit after the decimal place
	def arrangelabel(self,data):
		datareturn = format(float(data), '.0f')
		return datareturn

	def datatext(self):
		pass


	# this function defines the labels for the screen
	def labels(self,sensors):

		#degreesymbol =  u'\N{DEGREE SIGN}'

		rawtemp = str(self.A_Data)
		adjustedtemp = self.arrangelabel(rawtemp)
		tempstring = adjustedtemp + sensors[0][4]

		self.A_Label = LabelObj(tempstring,font,self.draw,colour = lcars_orange)
		self.A_Label.push(23,self.labely)


		rawbaro = str(self.B_Data)
		adjustedbaro = self.arrangelabel(rawbaro)
		barostring = adjustedbaro + " " + sensors[1][4]

		self.B_Label = LabelObj(barostring,font,self.draw, colour = lcars_blue)
		self.B_Label.center(self.labely,23,135)
		#self.baroLabel.push(57,100)

		rawhumi = str(self.C_Data)
		adjustedhumi = self.arrangelabel(rawhumi)
		humistring = adjustedhumi + sensors[2][4]

		self.C_DataLabel = LabelObj(humistring,font,self.draw, colour = lcars_pinker)
		#self.C_DataLabel.push(117,100)
		self.C_DataLabel.r_align(156,self.labely)

	#push the image frame and contents to the draw object.
	def push(self,sensors,draw):
		self.draw = draw
		#self.draw.paste((0,0),self.back)

		self.C_Data = sensors[configure.sensor3[0]][0]
		self.B_Data = sensors[configure.sensor2[0]][0]
		self.A_Data = sensors[configure.sensor1[0]][0]
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

		# returns mode_a so we will stay on this screen
		# should change it button pressed.
		status  = "mode_a"

		keys = self.input.read()

		if keys[0]:
			if self.input.is_down(0):
				print("Input1")

		if keys[1]:
			if self.input.is_down(1):
				print("Input2")
				status  = "mode_b"


		if keys[2]:
			if self.input.is_down(2):
				print("Input3")

		return status
# governs the screen drawing of the entire program. Everything flows through Screen.
# Screen instantiates a draw object and passes it the image background.
# Screen monitors button presses and passes flags for interface updates to the draw object.

class ThermalFrame(object):
	def __init__(self,input):
		pass


class ColourScreen(object):

	def __init__(self):

		# instantiates an image and uses it in a draw object.
		self.image = Image.open('assets/lcarsframe.png')#.convert('1')


		self.status = "mode_a"

		# Creates a local reference for our input object.
		self.input = Inputs()

		self.multi_frame = MultiFrame(self.input)
		self.settings_frame = SettingsFrame(self.input)
		self.thermal_frame = ThermalFrame(self.input)

	def graph_screen(self,sensors):
		self.newimage = self.image.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.multi_frame.push(sensors,self.draw)
		self.pixdrw()
		return self.status

	def thermal_screen(self,sensors):
		self.newimage = self.image.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.thermal_frame.push(sensors,self.draw)
		self.pixdrw()
		return self.status

	def settings(self,sensors):
		self.newimage = self.image.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.settings_frame.push(sensors,self.draw)
		self.pixdrw()
		return self.status

	def pixdrw(self):
		thisimage = self.newimage.convert(mode = "RGB")
		device.display(thisimage)
