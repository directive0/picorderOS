#!/usr/bin/env python
# This module controls the st7735 type screens
print("Loading Luma.LCD st7735 Screen")
import math
import time

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from luma.emulator.device import pygame as pyscreen

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
bigfont = ImageFont.truetype("assets/babs.otf",20)

# Raspberry Pi hardware SPI config:
DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0

TRANSITION = [False]


if configure.pc:
	device = pyscreen(width = 160, height = 128, mode = "RGB")
else:
	serial = spi(port = SPI_PORT, device = SPI_DEVICE, gpio_DC = DC, gpio_RST = RST, bus_speed_hz=24000000)
	device = st7735(serial, width = 160, height = 128, mode = "RGB")


# The following are for LCARS colours from LCARScom.net
lcars_orange = (255,153,0)
lcars_pink = (204,153,204)
lcars_blue = (153,153,204)
lcars_red = (204,102,102)
lcars_peach = (255,204,153)
lcars_bluer = (153,153,255)
lcars_orpeach = (255,153,102)
lcars_pinker = (204,102,153)

theme1 =  [lcars_orange,lcars_blue,lcars_pinker]

fore_col = 0
back_col = 1

# Controls text objects drawn to the LCD
class LabelObj(object):
	def __init__(self,string,font, colour = lcars_blue):
		self.font = font
		#self.draw = draw
		self.string = string
		self.colour = colour

	def center(self,y,x,w,draw):
		size = self.font.getsize(self.string)
		xmid = x + w/2
		#ymid = y + h/2
		textposx = xmid - (size[0]/2)
		#textposy = ymid - (size[1]/2) + self.scaler
		self.push(textposx,y,draw)

	def r_align(self,x,y,draw):
		size = self.font.getsize(self.string)
		self.push(x-size[0],y,draw)

	# Draws the label onto the provided draw buffer.
	def push(self,locx,locy,draw):
		self.draw = draw
		self.draw.text((locx, locy), self.string, font = self.font, fill= self.colour)

	def getsize(self):
		size = self.draw.textsize(self.string, font=self.font)
		return size

class SelectableLabel(LabelObj):


	def __init__(self,font,draw,oper,colour = lcars_blue, special = 0):
		self.font = font
		self.draw = draw
		self.colour = colour

		# special determines the behaviour of the label for each type of oper
		# the class is supplied. There may be multiple types of int or boolean based
		# configuration parameters so this variable helps make new options
		self.special = special

		# coordinates
		self.x = 0
		self.y = 0

		# basic graphical parameters
		self.fontSize = 33

		# self.myfont = pygame.font.Font(titleFont, self.fontSize)
		# text = "Basic Item"
		# self.size = self.myfont.size(text)

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
	def __init__(self):

		self.pages = [["Sensor 1",configure.sensor1], ["Sensor 2", configure.sensor2], ["Sensor 3",configure.sensor3], ["Auto Range",configure.auto], ["LEDs", configure.sleep],["Power Off","poweroff"]]

		# Sets the topleft origin of the graph
		self.graphx = 23
		self.graphy = 24

		self.status_raised = False

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 71

		self.selection = 0

		self.auto = configure.auto[0]
		self.interval = timer()
		self.interval.logtime()
		#self.draw = draw
		self.titlex = 25
		self.titley = 6
		self.labely = 102

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47
		self.labely = 102


		self.title = LabelObj("Settings",titlefont)
		self.itemlabel = LabelObj("Item Label",titlefont,colour = lcars_peach)
		self.A_Label = LabelObj("Next",font,colour = lcars_blue)
		self.B_Label = LabelObj("Enter",font, colour = lcars_blue)
		self.C_Label = LabelObj("Exit",font, colour = lcars_blue)

		self.item = LabelObj("No Data",bigfont,colour = lcars_pink)
		# device needs to show multiple settings
		# first the sensor palette configuration

	def toggle(self,oper):

		# if the parameter supplied is a boolean
		if isinstance(oper[0], bool):
			#toggle its state
			oper[0] = not oper[0]

		#if the parameter supplied is an integer
		elif isinstance(oper[0], int):

			# increment the integer.
			oper[0] += 1

			# if the integer is larger than the pool
			if oper[0] > configure.max_sensors[0]-1:
				oper[0] = 0

		elif isinstance(oper, str):
			#configure.last_status[0] = configure.status[0]
			self.status_raised = True
			configure.status[0] = oper


		return oper


	def push(self, sensor, draw):

		#draw the frame heading

		self.title.push(self.titlex,self.titley,draw)


		#draw the option item heading
		self.itemlabel.string = str(self.pages[self.selection][0])
		self.itemlabel.push(self.titlex,self.titley+20,draw)



		self.A_Label.push(23,self.labely,draw)


		self.B_Label.center(self.labely,23,135,draw)


		self.C_Label.r_align(156,self.labely,draw)


		#draw the 3 graph parameter items
		if self.selection == 0 or self.selection == 1 or self.selection == 2:

			self.item.string = str(configure.sensor_info[self.pages[self.selection][1][0]][3])
			self.item.push(self.titlex,self.titley+40,draw)
		else:

			if isinstance(self.pages[self.selection][1][0], bool):
				self.item.string = str(self.pages[self.selection][1][0])
				self.item.push(self.titlex,self.titley+40,draw)


		status = "settings"

		if configure.eventready[0]:
			keys = configure.eventlist[0]

			if keys[0]:
				self.selection = self.selection + 1
				if self.selection > (len(self.pages) - 1):
					self.selection = 0

			if keys[1]:
				state = self.toggle(self.pages[self.selection][1])

				if self.status_raised:
					status = state
					self.status_raised = False

			if keys[2]:
				status = configure.last_status[0]
			configure.eventready[0] = False

		return status

class PowerDown(object):
	def __init__(self):

		# Sets the topleft origin of the graph
		self.graphx = 23
		self.graphy = 24

		self.status_raised = False

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 71

		self.selection = 0


		self.auto = configure.auto[0]
		self.interval = timer()
		self.interval.logtime()
		#self.draw = draw
		self.titlex = 25
		self.titley = 6
		self.labely = 102

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47
		self.labely = 102


		self.title = LabelObj("CAUTION",bigfont, colour = lcars_red)
		self.itemlabel = LabelObj("Item Label",titlefont,colour = lcars_orange)
		self.A_Label = LabelObj("Yes",font,colour = lcars_blue)
		self.B_Label = LabelObj("Enter",font, colour = lcars_blue)
		self.C_Label = LabelObj("No",font, colour = lcars_blue)

		self.item = LabelObj("No Data",bigfont,colour = lcars_orpeach)
		# device needs to show multiple settings
		# first the sensor palette configuration


	def push(self, draw):

		#draw the frame heading

		self.title.center(self.titley,self.titlex,135,draw)


		#draw the option item heading
		#self.itemlabel.string = str(self.pages[self.selection][0])
	#	self.itemlabel.push(self.titlex,self.titley+20,draw)



		self.A_Label.push(23,self.labely,draw)


		#self.B_Label.center(self.labely,23,135,draw)


		self.C_Label.r_align(156,self.labely,draw)


		#draw the 3 graph parameter items

		self.item.string = "Power Down?"
		self.item.center(self.titley+40, self.titlex, 135,draw)


		status = "poweroff"


		keys = configure.eventlist

		if keys[0]:
			status = "shutdown"

		if keys[1]:
			pass

		if keys[2]:
			status = "settings"


		return status



# Controls the LCARS frame, measures the label and makes sure the top frame bar has the right spacing.
class MultiFrame(object):

	def __init__(self):
		# Sets the topleft origin of the graph
		self.graphx = 23
		self.graphy = 24

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 71


		self.marginleft = 23
		self.marginright= 133

		# sets the background image for the display
		self.back = Image.open('assets/lcarsframe.png')

		# sets the currently selected sensor to focus on
		self.selection = 0

		# ties the auto state to the global object
		self.auto = configure.auto[0]

		# creates and interval timer for screen refresh.
		self.interval = timer()
		self.interval.logtime()

		# Sets the coordinates of onscreen labels.
		self.titlex = 23
		self.titley = 6
		self.labely = 102

		self.graphcycle = 0

		self.decimal = 1

		self.divider = 47

		# create our graph_screen
		self.A_Graph = graph_area(0,(self.graphx,self.graphy),(self.gspanx,self.gspany),self.graphcycle, theme1[0], width = 1)

		self.B_Graph = graph_area(1,(self.graphx,self.graphy),(self.gspanx,self.gspany),self.graphcycle, theme1[1], width = 1)

		self.C_Graph = graph_area(2,(self.graphx,self.graphy),(self.gspanx,self.gspany),self.graphcycle, theme1[2], width = 1)

		self.Graphs = [self.A_Graph, self.B_Graph, self.C_Graph]

		self.A_Label = LabelObj("a_string",font,colour = lcars_orange)

		self.B_Label = LabelObj("b_string",font, colour = lcars_blue)

		self.C_Label = LabelObj("c_string",font, colour = lcars_pinker)

		self.focus_Label = LabelObj("test",bigfont, colour = lcars_orpeach)
		self.focus_high_Label = LabelObj("test",font, colour = lcars_peach)
		self.focus_low_Label = LabelObj("test",font, colour = lcars_bluer)
		self.focus_mean_Label = LabelObj("test",font, colour = lcars_pinker)

		self.title = LabelObj("Multi-Graph",titlefont, colour = lcars_peach)

	def get_x(self):
		return self.gspanx - self.graphx

	# takes a value and sheds the second digit after the decimal place
	def arrangelabel(self,data,range = ".0f"):
		datareturn = format(float(data), range)
		return datareturn

	# defines the labels for the screen
	def labels(self,sensors):

		# depending on which number the "selection" variable takes on.
		if self.selection == 0:
			raw_a = str(self.A_Data)
			adjusted_a = self.arrangelabel(raw_a)
			a_string = adjusted_a + sensors[configure.sensor1[0]][4]

			raw_b = str(self.B_Data)
			adjusted_b = self.arrangelabel(raw_b)
			b_string = adjusted_b + " " + sensors[configure.sensor2[0]][4]

			raw_c = str(self.C_Data)
			adjusted_c = self.arrangelabel(raw_c)
			c_string = adjusted_c + " " + sensors[configure.sensor3[0]][4]

			self.A_Label.string = a_string
			self.A_Label.push(23,self.labely,self.draw)

			self.B_Label.string = b_string
			self.B_Label.center(self.labely,23,135,self.draw)

			self.C_Label.string = c_string
			self.C_Label.r_align(156,self.labely,self.draw)

		# displays more details for whatever sensor is in focus
		if self.selection != 0:

			this = self.selection - 1

			this_bundle = self.Graphs[this]

			raw = str(sensors[configure.sensors[this][0]][0])
			adjusted = self.arrangelabel(raw, '.2f')
			self.focus_Label.string = adjusted
			self.focus_Label.r_align(156,self.titley,self.draw)

			self.focus_high_Label.string = "max " + self.arrangelabel(str(this_bundle.get_high()), '.1f')
			self.focus_high_Label.push(23,self.labely,self.draw)

			self.focus_low_Label.string = "min " + self.arrangelabel(str(this_bundle.get_low()), '.1f')
			self.focus_low_Label.center(self.labely,23,135,self.draw)

			self.focus_mean_Label.string = "x- " + self.arrangelabel(str(this_bundle.get_average()), '.1f')
			self.focus_mean_Label.r_align(156,self.labely,self.draw)


	# push the image frame and contents to the draw object.
	def push(self,sensors,draw):
		# passes the current bitmap buffer to the object incase someone else needs it.
		self.draw = draw

		# Grabs the current sensor reading
		self.A_Data = sensors[configure.sensor1[0]][0]
		self.B_Data = sensors[configure.sensor2[0]][0]
		self.C_Data = sensors[configure.sensor3[0]][0]


		# Draws the Title
		if self.selection != 0:
			this = self.selection - 1
			self.title.string = configure.sensor_info[configure.sensors[this][0]][3]
		else:
			self.title.string = "Multi-Graph"

		self.title.push(self.titlex,self.titley,draw)


		# turns each channel on individually
		if self.selection == 0:

			self.C_Graph.render(self.draw)
			self.B_Graph.render(self.draw)
			self.A_Graph.render(self.draw)


		if self.selection == 1:
			self.A_Graph.render(self.draw)

		if self.selection == 2:
			self.B_Graph.render(self.draw)

		if self.selection == 3:
			self.C_Graph.render(self.draw)

		self.labels(sensors)

		# returns mode_a to the main loop unless something causes state change
		status  = "mode_a"

		print("eventready = ", configure.eventready[0])
		if configure.eventready[0]:
			keys = configure.eventlist[0]
			print("received events:", configure.eventlist)
			# if a key is registering as pressed increment or rollover the selection variable.
			if keys[0]:
				self.selection += 1
				if self.selection > 3:
					self.selection = 0

			if keys[1]:
				status =  "mode_b"

			if keys[2]:
				configure.last_status[0] = "mode_a"
				status = "settings"
			configure.eventready[0] = False

		return status
# governs the screen drawing of the entire program. Everything flows through Screen.
# Screen instantiates a draw object and passes it the image background.
# Screen monitors button presses and passes flags for interface updates to the draw object.

class ThermalFrame(object):
	def __init__(self):
		# Sets the topleft origin of the graph
		self.graphx = 23
		self.graphy = 24

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 71
		self.t_grid = ThermalGrid(23,24,133,71)
		self.t_grid_full = ThermalGrid(23,8,133,109)
		self.titlex = 23
		self.titley = 6

		self.high = 0
		self.low = 0
		self.average = 0
		self.labely = 102

		self.selection = 0

		self.timed = timer()
		self.timed.logtime()
		self.interval = .1

		self.title = LabelObj("Thermal Array",titlefont)

		self.A_Label = LabelObj("No Data",font,colour = lcars_blue)
		self.B_Label = LabelObj("No Data",font, colour = lcars_pinker)
		self.C_Label = LabelObj("No Data",font, colour = lcars_orange)


	# this function takes a value and sheds the second digit after the decimal place
	def arrangelabel(self,data):
		datareturn = format(float(data), '.0f')
		return datareturn

	def labels(self):

		if self.selection == 0 or self.selection == 1:

			raw_a = str(self.low)
			adjusted_a = self.arrangelabel(raw_a)
			a_string = "Low: " + adjusted_a

			self.A_Label.string = a_string
			self.A_Label.push(23,self.labely,self.draw)

		if self.selection == 0 or self.selection == 2:
			raw_b = str(self.high)
			adjusted_b = self.arrangelabel(raw_b)
			self.B_Label.string = "High: " + adjusted_b


			self.B_Label.center(self.labely,23,135, self.draw)
			#self.baroLabel.push(57,100)

		if self.selection == 0 or self.selection == 3:
			raw_c = str(self.average)
			adjusted_c = self.arrangelabel(raw_c)
			self.C_Label.string = "Avg: " + adjusted_c


			self.C_Label.r_align(156,self.labely,self.draw)

	def push(self, sensor, draw):

		self.draw = draw

		self.labels()

		# Draw title

		self.title.push(self.titlex,self.titley, self.draw)


		# Draw ThermalGrid object
		if self.timed.timelapsed() > self.interval:

			if self.selection == 0:
				self.average,self.high,self.low = self.t_grid.update()
				self.timed.logtime()
			if self.selection == 1:
				self.average,self.high,self.low = self.t_grid_full.update()
				self.timed.logtime()

		if self.selection == 0:
			self.t_grid.push(draw)
		elif self.selection ==1:
			self.t_grid_full.push(draw)



		status  = "mode_b"
		if configure.eventready[0]:
			keys = configure.eventlist[0]


			# ------------- Input handling -------------- #
			if keys[0]:
				status  = "mode_a"

			if keys[1]:
				self.selection += 1
				if self.selection > 1:
					self.selection = 0

			if keys[2]:
				status = "settings"
				configure.last_status[0] = "mode_b"
			configure.eventready[0] = False

		return status

class ColourScreen(object):

	def __init__(self):

		# instantiates an image and uses it in a draw object.
		self.image = Image.open('assets/lcarsframe.png')#.convert('1')
		self.blankimage = Image.open('assets/lcarsframeblank.png')

		self.status = "mode_a"

		self.multi_frame = MultiFrame()
		self.settings_frame = SettingsFrame()
		self.thermal_frame = ThermalFrame()
		self.powerdown_frame = PowerDown()


	def get_size(self):
		return self.multi_frame.get_x()

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
		self.newimage = self.blankimage.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.settings_frame.push(sensors,self.draw)
		self.pixdrw()
		return self.status

	def powerdown(self):
		self.newimage = self.blankimage.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.powerdown_frame.push(self.draw)
		self.pixdrw()
		return self.status

	def pixdrw(self):
		thisimage = self.newimage.convert(mode = "RGB")
		device.display(thisimage)
