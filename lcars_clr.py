#!/usr/bin/env python
# This module controls the st7735 type screens
print("Loading 160x128 LCARS Interface")
import math
import time

from operator import itemgetter

# remove this part and replace with display
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735

# Load up the image library stuff to help draw bitmaps to push to the screen
import PIL.ImageOps
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# load the module that draws graphs
from pilgraph import *
from amg8833_pil import *
from plars import *
from objects import *

from modulated_em import *

# Load default font.
font = ImageFont.truetype("assets/babs.otf",13)
titlefont = ImageFont.truetype("assets/babs.otf",16)
bigfont = ImageFont.truetype("assets/babs.otf",20)
giantfont = ImageFont.truetype("assets/babs.otf",30)

# Load assets
logo = Image.open('assets/picorderOS_logo.png')

# Raspberry Pi hardware SPI config:
DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0

TRANSITION = [False]


if not configure.pc:
	serial = spi(port = SPI_PORT, device = SPI_DEVICE, gpio_DC = DC, gpio_RST = RST)# ,bus_speed_hz=24000000)
	device = st7735(serial, width = 160, height = 128, mode = "RGB")
else:
	device = pygame(width = 160, height = 128)


# Standard LCARS colours
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
	def __init__(self,string, font, colour = lcars_blue):
		self.font = font
		#self.draw = draw
		self.string = string
		self.colour = colour


	def center(self,y,x,w,draw):
		size = self.font.getsize(self.string)
		xmid = x + w/2

		textposx = xmid - (size[0]/2)

		self.push(textposx,y,draw)

	def r_align(self,x,y,draw):
		size = self.font.getsize(self.string)
		self.push(x-size[0],y,draw)

	# Draws the label onto the provided draw buffer.
	def push(self,locx,locy,draw, string = "None"):
		if string == "None":
			drawstring = self.string
		else:
			drawstring = str(string)
		self.draw = draw
		self.draw.text((locx, locy), drawstring, font = self.font, fill= self.colour)

	def getsize(self):
		size = self.font.getsize(self.string)
		return size

# a class to create a simple text list.
# initialize with x/y coordinates
# on update provide list of items to display, and draw object to draw to.
class Label_List(object):

	def __init__(self, x, y, colour = None):

		#initial coordinates
		self.x = x
		self.y = y

		# used in the loop to offset y location of items.
		self.jump = 0

		#adjusts the increase in seperation
		self.spacer = 1

		# holds the items to display
		self.labels = []

		if colour == None:
			self.colour = lcars_orpeach
		else:
			self.colour = colour


	# draws the list of items as a text list.
	def update(self, items, draw):
		# clears label buffer.
		self.labels = []

		# for each item in the list of items to draw
		for index, item in enumerate(items):

			string = str(item)
			# create a text item with the string.
			thislabel = LabelObj(string, font, colour = self.colour)
			thislabel.push(self.x, self.y + self.jump,draw)

			# increase the y position by the height of the last item, plus spacer
			self.jump += (thislabel.getsize()[1] + self.spacer)

		# when loop is over reset jump counter.
		self.jump = 0



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

		# if the parameter supplied is a boolean just flip it.
		if isinstance(self.oper[0], bool):
			#toggle its state
			self.oper[0] = not self.oper[0]

		# if the parameter supplied is an integer its to change
		# one of the graphed sensors.

		elif isinstance(self.oper[0], int):

			# increment the integer.
			self.oper[0] += 1

			# if the integer is larger than the pool reset it
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

		self.pages = [["Sensor 1",configure.sensor1], ["Sensor 2", configure.sensor2], ["Sensor 3",configure.sensor3], ["Audio",configure.audio],["Alarm",configure.alarm], ["Auto Range",configure.auto], ["LEDs", configure.sleep],["Power Off","poweroff"]]

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
		self.titlex = 2
		self.titley = 11
		self.labely = 114

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47


		# the set labels for the screen
		self.title = LabelObj("Settings",bigfont)
		self.itemlabel = LabelObj("Item Label",bigfont,colour = lcars_peach)
		self.item = LabelObj("No Data",titlefont,colour = lcars_pink)

		# three input cue labels
		self.A_Label = LabelObj("Next",font,colour = lcars_orpeach)
		self.B_Label = LabelObj("Enter",font, colour = lcars_orpeach)
		self.C_Label = LabelObj("Exit",font, colour = lcars_orpeach)




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


	def push(self, draw):

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



		#draw the frame heading
		self.title.push(self.titlex,self.titley,draw)


		#draw the option item heading
		self.itemlabel.string = str(self.pages[self.selection][0])
		self.itemlabel.push(self.titlex+23,self.titley+25,draw)

		self.A_Label.push(2,self.labely,draw)
		self.B_Label.center(self.labely,23,114,draw)
		self.C_Label.r_align(156,self.labely,draw)


		#draw the 3 graph parameter items
		if self.selection == 0 or self.selection == 1 or self.selection == 2:
			self.item.string = str(configure.sensor_info[self.pages[self.selection][1][0]][0])
			self.item.push(self.titlex+23,self.titley+53,draw)
		else:
			if isinstance(self.pages[self.selection][1][0], bool):
				self.item.string = str(self.pages[self.selection][1][0])
				self.item.push(self.titlex+23,self.titley+53,draw)


		return status

class StartUp(object):
	def __init__(self):
		self.titlex = 0
		self.titley = 77
		self.labely = 102
		self.jump = 22

		self.graphcycle = 0
		self.decimal = 1

		self.divider = 47
		self.labely = 102


		self.title = LabelObj("PicorderOS " + configure.version,bigfont, colour = lcars_peach)
		self.item = LabelObj(configure.boot_message,titlefont,colour = lcars_peach)

		# creates and interval timer for screen refresh.
		self.interval = timer()
		self.interval.logtime()

	def push(self, draw):

		draw.bitmap((59,15),logo)
		#draw the frame heading
		self.title.center(self.titley,0,160,draw)

		#draw the title and version
		self.item.center(self.titley+self.jump,0, 160,draw)


		if self.interval.timelapsed() > configure.boot_delay and configure.sensor_ready[0]:
			status = "mode_a"
		else:
			status = "startup"


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


		if configure.eventready[0]:

			keys = configure.eventlist[0]

			if keys[0]:
				status = "shutdown"

			if keys[1]:
				pass

			if keys[2]:
				status = "settings"

			configure.eventready[0] = False


		return status

class EMFrame(object):
	def __init__(self):

		self.wifi = Wifi_Scan()

		self.graphcycle = 0

		# Sets the topleft origin of the graph
		self.graphx = 20
		self.graphy = 58

		# Sets the x and y span of the graph
		self.gspanx = 135
		self.gspany = 29
		self.titlex = 23
		self.titley = 2

		self.high = 0
		self.low = 0
		self.average = 0
		self.labely = 4
		self.labelxr = 156


		self.selection = 0

		# create our graph_screen
		self.Signal_Graph = graph_area(0,(self.graphx,self.graphy),(self.gspanx,self.gspany),self.graphcycle, lcars_pink, width = 2, type = 1, samples = 45)

		self.title = LabelObj("Modulated EM Scan",titlefont, colour = lcars_orange)

		self.signal_name = LabelObj("SSID",bigfont, colour = lcars_peach)
		self.signal_strength = LabelObj("ST",giantfont, colour = lcars_peach)
		self.signal_frequency = LabelObj("FQ",titlefont, colour = lcars_orpeach)
		self.signal_mac = LabelObj("MAC",font, colour = lcars_orpeach)

		self.list = Label_List(22,35, colour = lcars_peach)



	def push(self, draw):

		status  = "mode_b"

		# input handling
		if configure.eventready[0]:
			keys = configure.eventlist[0]


			# ------------- Input handling -------------- #
			if keys[0]:
				status  = "mode_a"
				configure.eventready[0] = False
				return status

			if keys[1]:
				self.selection += 1

				if self.selection >= 2:
					self.selection = 0
				pass

			if keys[2]:
				status = "settings"
				configure.last_status[0] = "mode_b"
				configure.eventready[0] = False
				return status

			configure.eventready[0] = False

		self.wifi.update_plars()

		if self.selection == 0:

			# grab EM data from plars
			info = plars.get_top_em_info()[0]

			# draw screen elements
			self.Signal_Graph.render(draw)
			self.title.string = "Dominant Transciever"
			self.title.r_align(self.labelxr,self.titley,draw)
			self.signal_name.push(20,35,draw, string = info[0])
			self.signal_strength.string = str(info[1]) + " DB"
			self.signal_strength.r_align(self.labelxr,92,draw)
			self.signal_frequency.push(20,92,draw, string = info[3])
			self.signal_mac.push(20,111, draw, string = info[6])

		if self.selection == 1:

			# list to hold the data labels
			list_for_labels = []

			# grab EM list
			em_list = plars.get_recent_em_list()

			sorted_em_list = sorted(em_list, key=itemgetter(1), reverse = True)

			# prepare a list of the data received for display
			for ssid in sorted_em_list:
				name = str(ssid[0])
				strength = str(ssid[1])

				label = strength + " dB • " + name

				list_for_labels.append(label)
			self.title.string = "Modulated EM Scan"
			self.title.r_align(self.labelxr,self.titley,draw)
			self.list.update(list_for_labels,draw)

			# assign each list element and its

		return status

# Controls the LCARS frame, measures the label and makes sure the top frame bar has the right spacing.
class MultiFrame(object):

	def __init__(self):

		# Sets the topleft origin of the graph
		self.graphx = 18
		self.graphy = 25
		self.samples = configure.samples

		# Sets the x and y span of the graph
		self.gspanx = 135
		self.gspany = 69

		self.graphcycle = 0

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
	def arrangelabel(self,data,range = ".1f"):
		datareturn = format(float(data), range)
		return datareturn

	# defines the labels for the screen
	def labels(self):

		# depending on which number the "selection" variable takes on.

		if self.selection == 0:
			raw_a = str(self.A_Data)
			adjusted_a = self.arrangelabel(raw_a)
			a_string = adjusted_a + " " + configure.sensor_info[configure.sensor1[0]][2]

			raw_b = str(self.B_Data)
			adjusted_b = self.arrangelabel(raw_b)
			b_string = adjusted_b + " " + configure.sensor_info[configure.sensor2[0]][2]

			raw_c = str(self.C_Data)
			adjusted_c = self.arrangelabel(raw_c)
			c_string = adjusted_c + " " + configure.sensor_info[configure.sensor3[0]][2]

			self.A_Label.string = a_string
			self.A_Label.push(23,self.labely,self.draw)

			self.B_Label.string = b_string
			self.B_Label.center(self.labely,23,135,self.draw)

			self.C_Label.string = c_string
			self.C_Label.r_align(156,self.labely,self.draw)

		# displays more details for whatever sensor is in focus
		if self.selection != 0:

			carousel = [self.A_Data,self.B_Data,self.C_Data]

			this = self.selection - 1

			this_bundle = self.Graphs[this]

			raw = str(carousel[this])

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
	def push(self,draw):



		# returns mode_a to the main loop unless something causes state change
		status  = "mode_a"


		if configure.eventready[0]:
			keys = configure.eventlist[0]

			# if a key is registering as pressed increment or rollover the selection variable.
			if keys[0]:

				configure.eventready[0] = False

				self.selection += 1
				if self.selection > 3:
					self.selection = 0
					status = "mode_c"
					return status

			if keys[1]:
				status =  "mode_b"
				configure.eventready[0] = False
				return status

			if keys[2]:
				configure.last_status[0] = "mode_a"
				status = "settings"
				configure.eventready[0] = False
				return status

			configure.eventready[0] = False


		# passes the current bitmap buffer to the object incase someone else needs it.
		self.draw = draw

		senseslice = []
		data_a = []
		data_b = []
		data_c = []
		datas = [data_a,data_b,data_c]

		for i in range(3):

			# determines the sensor keys for each of the three main sensors
			this_index = int(configure.sensors[i][0])

			dsc,dev,sym,maxi,mini = configure.sensor_info[this_index]

			datas[i] = plars.get_recent(dsc,dev,num = 1)



			if len(datas[i]) == 0:
				datas[i] = [47]

			item = datas[i]

			senseslice.append([item[0], dsc, dev, sym, mini, maxi])



		# Grabs the current sensor reading
		self.A_Data = senseslice[0][0]#configure.sensor_data[configure.sensor1[0]][0]
		self.B_Data = senseslice[1][0]#configure.sensor_data[configure.sensor2[0]][0]
		self.C_Data = senseslice[2][0]#configure.sensor_data[configure.sensor3[0]][0]




		# Draws the Title
		if self.selection != 0:
			this = self.selection - 1
			self.title.string = senseslice[this][1]
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


		self.labels()




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
		self.t_grid_full = ThermalGrid(23,8,133,103)
		self.titlex = 23
		self.titley = 6

		self.high = 0
		self.low = 0
		self.average = 0
		self.labely = 102

		self.selection = 0

		self.title = LabelObj("Thermal Array",titlefont)

		self.A_Label = LabelObj("No Data",font,colour = lcars_blue)
		self.B_Label = LabelObj("No Data",font, colour = lcars_pinker)
		self.C_Label = LabelObj("No Data",font, colour = lcars_orange)


	# this function takes a value and sheds the second digit after the decimal place
	def arrangelabel(self,data):
		datareturn = format(float(data), '.0f')
		return datareturn

	def labels(self):

		if self.selection == 0:
			raw_a = str(self.low)
			adjusted_a = self.arrangelabel(raw_a)
			a_string = "Low: " + adjusted_a
			self.A_Label.string = a_string
			self.A_Label.push(23,self.labely,self.draw)

		if self.selection == 0:
			raw_b = str(self.high)
			adjusted_b = self.arrangelabel(raw_b)
			self.B_Label.string = "High: " + adjusted_b
			self.B_Label.center(self.labely,23,135, self.draw)

		if self.selection == 0:
			raw_c = str(self.average)
			adjusted_c = self.arrangelabel(raw_c)
			self.C_Label.string = "Avg: " + adjusted_c
			self.C_Label.r_align(156,self.labely,self.draw)

	def push(self, draw):

		status  = "mode_c"

		if configure.eventready[0]:
			keys = configure.eventlist[0]


			# ------------- Input handling -------------- #
			if keys[0]:
				self.selection += 1
				if self.selection > 2:
					self.selection = 0
					status  = "mode_a"
					return status
				configure.eventready[0] = False


			if keys[1]:
				configure.eventready[0] = False
				status  = "mode_b"
				return status

			if keys[2]:
				status = "settings"
				configure.last_status[0] = "mode_c"
				configure.eventready[0] = False
				return status

			configure.eventready[0] = False


		self.draw = draw
		self.labels()

		# Draw title

		self.title.push(self.titlex,self.titley, self.draw)


		if self.selection == 0:
			self.average,self.high,self.low = self.t_grid.update()
		if self.selection == 1:
			self.average,self.high,self.low = self.t_grid_full.update()

		if not configure.alarm_ready[0]:
			if self.high >= configure.TEMP_ALERT[1]:
				configure.alarm_ready[0] = True
			if self.low <= configure.TEMP_ALERT[0]:
				configure.alarm_ready[0] = True

		if self.selection == 0:
			self.t_grid.push(draw)
		elif self.selection == 1:
			self.t_grid_full.push(draw)
		elif self.selection == 2:
			self.selection = 0
			status = "mode_a"

		return status

class ColourScreen(object):

	def __init__(self):

		# instantiates an image and uses it in a draw object.
		self.image = Image.open('assets/lcarsframe.png')#.convert('1')
		self.blankimage = Image.open('assets/lcarsframeblank.png')
		self.tbar = Image.open('assets/lcarssplitframe.png')
		self.burger = Image.open('assets/lcarsburgerframe.png')
		self.burgerfull = Image.open('assets/lcarsburgerframefull.png')

		self.status = "mode_a"

		self.multi_frame = MultiFrame()
		self.settings_frame = SettingsFrame()
		self.thermal_frame = ThermalFrame()
		self.powerdown_frame = PowerDown()
		self.em_frame = EMFrame()
		self.startup_frame = StartUp()


	def get_size(self):
		return self.multi_frame.samples

	def start_up(self):
		self.newimage = self.burgerfull.copy()
		self.draw = ImageDraw.Draw(self.newimage)

		self.status = self.startup_frame.push(self.draw)

		self.pixdrw()

		return self.status


	def graph_screen(self):
		self.newimage = self.image.copy()
		self.draw = ImageDraw.Draw(self.newimage)

		last_status = self.status

		self.status = self.multi_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()

		return self.status

	def em_screen(self):
		self.newimage = self.tbar.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.em_frame.push(self.draw)
		self.pixdrw()
		return self.status

	def thermal_screen(self):
		self.newimage = self.image.copy()
		self.draw = ImageDraw.Draw(self.newimage)

		last_status = self.status

		self.status = self.thermal_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()

		return self.status

	def settings(self):
		self.newimage = self.burger.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.settings_frame.push(self.draw)
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
