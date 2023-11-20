#!/usr/bin/env python
# This module controls the st7735 type screens
print("Loading 160x128 LCARS Interface")
from objects import *
import math
import time
import socket

from operator import itemgetter

from display import GenericDisplay

device = GenericDisplay()

# Load up the image library stuff to help draw bitmaps to push to the screen
import random
import numpy
import PIL.ImageOps
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# load the module that draws graphs
from pilgraph import *
from amg8833_pil import *
from plars import *




# Load default font.
microfont = ImageFont.truetype("assets/babs.otf",7)
littlefont = ImageFont.truetype("assets/babs.otf",10)
font = ImageFont.truetype("assets/babs.otf",13)
titlefont = ImageFont.truetype("assets/babs.otf",16)
bigfont = ImageFont.truetype("assets/babs.otf",20)
giantfont = ImageFont.truetype("assets/babs.otf",30)

# Standard LCARS colours
lcars_orange = (255,153,0)
lcars_pink = (204,153,204)
lcars_blue = (153,153,208)
lcars_red = (204,102,102)
lcars_peach = (255,204,153)
lcars_bluer = (153,153,255)
lcars_orpeach = (255,153,102)
lcars_pinker = (204,102,153)
lcars_grid = (47,46,84)

theme1 =  [lcars_orange,lcars_blue,lcars_pinker]

fore_col = 0
back_col = 1



class DrawGrid(object):
	def __init__(self,x,y,w,h,colour,segx = 4, segy = 4):
		self.x = x
		self.y = y
		self.h = h
		self.w = w
		self.colour = colour
		self.segx = segx
		self.segy = segy

		#calculate the interval of the vertical segments ( | )
		self.intervalx = self.w / self.segx

		#calculate the interval of the horizontal segments ( - )
		self.intervaly = self.h / self.segy

		self.hcoordlist = []
		self.vcoordlist = []

		self.assign()

	def assign(self):

		# determine verticals
		
		# for each division of the total width
		for i in range(self.segx):

			# if not the first and last positions
			if i != 0 and i != self.segx:

				# define coords for the line segment for this position along the y
				y1 = self.y
				y2 = self.y + self.h 
				
				# x position determined by the current i times the interval
				x = self.x + (self.intervalx * i)

				# append the list of the x/y coords for the line segment into the coord list
				result = [(x,y1),(x,y2)]
				self.vcoordlist.append(result)

		# determine horizontals
		for i in range(self.segy):

			# if not the first and last positions
			if i != 0 and i != self.segy:

				# define coords for the line segment for this position along the y
				x1 = self.x
				x2 = self.x + self.w 
				
				# y position determined by the current i times the interval
				y = self.y + (self.intervaly * i)

				# append the list of the x/y coords for the line segment into the coord list
				result = [(x1,y),(x2,y)]
				self.hcoordlist.append(result)
			

	def push(self, draw):

		# draws the horizontals	
		for i in range(len(self.hcoordlist)):
			draw.line(self.hcoordlist[i],self.colour,1)
		
		#draws the verticals
		for i in range(len(self.vcoordlist)):
			draw.line(self.vcoordlist[i],self.colour,1)


class Dialogue(object):

	def __init__(self):

		self.selection = 0


		self.auto = configure.auto[0]
		self.interval = timer()
		self.interval.logtime()

		self.titlex = 25
		self.titley = 6
		self.labely = 102

		self.divider = 47

		self.labely = 102

		self.result = "multi"
		self.title = LabelObj("CAUTION",bigfont, colour = lcars_red)
		self.itemlabel = LabelObj("Item Label",titlefont,colour = lcars_orange)
		self.A_Label = LabelObj("Yes",font,colour = lcars_blue)
		self.B_Label = LabelObj("Enter",font, colour = lcars_blue)
		self.C_Label = LabelObj("No",font, colour = lcars_blue)

		self.item = LabelObj("No Data",bigfont,colour = lcars_orpeach)
		# device needs to show multiple settings
		# first the sensor palette configuration

		self.events = Events([self.result,0,"last",0,0,0,0,0], "poweroff")

	def push(self, draw):

		status,payload = self.events.check()

		#draw the frame heading

		self.title.center(self.titley,self.titlex,135,draw)
		self.A_Label.push(23,self.labely,draw)
		self.C_Label.r_align(156,self.labely,draw)
		self.item.string = "Power Down?"
		self.item.center(self.titley+40, self.titlex, 135,draw)


		return status

	def assign(self,heading,body,result):
		self.title.string = heading
		self.itemlabel.string = body
		self.result = result
		pass

# Controls text objects drawn to the LCD
class LabelObj(object):
	def __init__(self,string, font, colour = lcars_blue):
		self.font = font
		#self.draw = draw
		self.string = string
		self.colour = colour


	# to center the text you need to give it the y position, the starting x pos
	# and the width. Also the draw object.
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

	def __init__(self, x, y, colour = lcars_orpeach, ofont = font):

		#initial coordinates
		self.x = x
		self.y = y

		# used in the loop to offset y location of items.
		self.jump = 0

		#adjusts the increase in seperation
		self.spacer = 1

		# holds the items to display
		self.labels = []

		self.font = ofont

		self.colour = colour


	# draws the list of items as a text list.
	def update(self, items, draw):
		# clears label buffer.
		self.labels = []

		# for each item in the list of items to draw
		for index, item in enumerate(items):

			string = str(item)
			# create a text item with the string.
			thislabel = LabelObj(string, self.font, colour = self.colour)
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

# serves as a screen to show the current status of the picorder
class MasterSystemsDisplay(object):

	def __init__(self):
		self.title = None
		self.status_list = None
		#self.draw = draw
		self.titlex = 2
		self.titley = 7
		self.labely = 24


		# the set labels for the screen
		self.title = LabelObj("Master Systems Display",titlefont,colour = lcars_orange)

		# three input cue labels
		self.C_Label = LabelObj("Exit",font, colour = lcars_orpeach)

		# A list of all the cool data.
		self.status_list = Label_List(25,23, colour = lcars_blue, ofont = littlefont)

		# grabs the RPI model info
		if not configure.pc:
			text = os.popen("cat /proc/device-tree/model").readline()
			self.model = str(text.rstrip("\x00")).replace("Raspberry Pi","Raspi")
		else:
			self.model = "Unknown"

		self.events = Events([1,2,"last",0,0,0,0,0],"msd")


	def load_list(self):

		# pulls data from the modulated_em.py
		wifi = "SSID: " + os.popen("iwgetid").readline()

		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		try:
			s.connect(("8.8.8.8", 80))
			IPAddr = s.getsockname()[0]
		except:
			IPAddr = "No IP Found"
		
		ip_str = "IP:  " + IPAddr
		host_str = "Name:  " + socket.gethostname()
		sense_ready = "Sensors Avl:  " + str(len(configure.sensor_info))
		model_name = "CPU:  " + self.model
		PLARS_size, PLARS_em_size = plars.get_plars_size()
		db_size = "PLARS Size:  " + str(PLARS_size)
		em_size = "PLARS EM Size:  " + str(PLARS_em_size)

		status_list = [model_name, ip_str, host_str, sense_ready, db_size, em_size]
		return status_list


	def push(self,draw):

		status, payload = self.events.check()

		#draw the frame heading
		self.title.center(self.titley,21,139,draw)
		#self.C_Label.r_align(26,self.labely,draw)
		self.status_list.update(self.load_list(),draw)

		return status

class PowerMenu(object):
	
	def __init__(self):

		# pages are a description string and an item to change. 
		# If a boolean it will toggle it. 
		# First 3 items are reserved for graph items.
		self.pages = [["Shutdown", "poweroff"],
						["Reboot", "reboot"],
						["Fault Mode", "fault"],
						["Timed Shutdown", "timer"]]

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 71

		self.selection = 0
		self.status_raised = False

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
		self.title = LabelObj("Power Control",bigfont)
		self.itemlabel = LabelObj("Item Label",bigfont,colour = lcars_peach)
		self.item = LabelObj("No Data",titlefont,colour = lcars_pink)

		# three input cue labels
		self.A_Label = LabelObj("Next",font,colour = lcars_orpeach)
		self.B_Label = LabelObj("Enter",font, colour = lcars_orpeach)
		self.C_Label = LabelObj("Exit",font, colour = lcars_orpeach)

		self.events = Events([1,2,"last","last",0,"msd",0,0],"settings")


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

		# returns mode_a to the main loop unless something causes state change
		status,payload  = self.events.check()

		if payload == 1:
			self.selection = self.selection + 1
			if self.selection > (len(self.pages) - 1):
				self.selection = 0
		elif payload == 2:
			state = self.toggle(self.pages[self.selection][1])
			if self.status_raised:
				status = state
				self.status_raised = False




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

class SettingsFrame(object):
	def __init__(self):

		# pages are a description string and an item to change. 
		# If a boolean it will toggle it. 
		# First 3 items are reserved for graph items.
		self.pages = [["Sensor 1", configure.sensor1],
						["Sensor 2", configure.sensor2],
						["Sensor 3", configure.sensor3],
						["Audio", configure.audio],
						["Warble", configure.warble],
						["LEDs", configure.leds_on],
						["Alarm", configure.alarm],
						["Auto Range", configure.auto],
						["Trim Buffer", configure.trim_buffer],
						["Data Logging", configure.datalog]]

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 71

		self.selection = 0
		self.status_raised = False

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

		self.events = Events([1,2,"last","last",0,"msd",0,0],"settings")


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

		# returns mode_a to the main loop unless something causes state change
		status,payload  = self.events.check()

		if payload == 1:
			self.selection = self.selection + 1
			if self.selection > (len(self.pages) - 1):
				self.selection = 0
		elif payload == 2:
			state = self.toggle(self.pages[self.selection][1])
			if self.status_raised:
				status = state
				self.status_raised = False




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

# a simple frame that tells the user that the picorder is loading another screen.
class LoadingFrame(object):

	captions = ["working", "accessing", "initializing", "computing", "calculating"]

	def __init__(self):
		self.annunciator = LabelObj("Stand By",giantfont,colour = lcars_peach)
		self.caption = LabelObj("47",bigfont,colour = lcars_peach)
		self.titley = 20
		self.captiony = 65

	def push(self, draw, status):

		self.caption.string = random.choice(self.captions)
		self.annunciator.center(self.titley,0,160,draw)
		self.caption.center(self.captiony,0,160,draw)

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
		self.item = LabelObj(configure.boot_message,font,colour = lcars_peach)

		# creates and interval timer for screen refresh.
		self.interval = timer()
		self.interval.logtime()

	def push(self, draw):


		#draw the frame heading
		self.title.center(self.titley,0,160,draw)

		#draw the title and version
		self.item.center(self.titley+self.jump,0, 160,draw)


		if self.interval.timelapsed() > configure.boot_delay and configure.sensor_ready[0]:
			status = "multi"
		else:
			status = "startup"


		return status

class PowerDown(object):
	def __init__(self):

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

		self.events = Events(["shutdown",0,"last","0",0,0,0,0], "poweroff")


	def push(self, draw):

		status,payload = self.events.check()

		#draw the frame heading

		self.title.center(self.titley,self.titlex,135,draw)
		self.A_Label.push(23,self.labely,draw)
		self.C_Label.r_align(156,self.labely,draw)
		self.item.string = "Power Down?"
		self.item.center(self.titley+40, self.titlex, 135,draw)


		return status

class EMFrame(object):
	def __init__(self):

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

		self.ossification = 0
		

		# create our graph_screen
		self.Signal_Graph = graph_area(0,(self.graphx+1,self.graphy+1),(self.gspanx-3,self.gspany-3),self.graphcycle, lcars_pink, width = 1, type = 1, samples = 45)
		self.Signal_Grid = DrawGrid(self.graphx,self.graphy,self.gspanx,self.gspany,lcars_grid)

		self.title = LabelObj("Modulated EM Scan",titlefont, colour = lcars_orange)

		self.signal_name = LabelObj("SSID",bigfont, colour = lcars_peach)
		self.signal_name_sm = LabelObj("SSID",font, colour = lcars_peach)

		self.signal_strength = LabelObj("ST",giantfont, colour = lcars_peach)
		self.signal_strength_sm = LabelObj("ST",littlefont, colour = lcars_peach)

		self.signal_frequency = LabelObj("FQ",titlefont, colour = lcars_orpeach)
		self.signal_frequency_sm = LabelObj("FQ",littlefont, colour = lcars_peach)
		self.signal_mac = LabelObj("MAC",font, colour = lcars_orpeach)
		

		self.indicator1 = LabelObj("00",littlefont, colour = (0,0,0))
		self.overlapping_no = LabelObj("00",littlefont, colour = (0,0,0))

		self.list = Label_List(22,35, colour = lcars_peach)

		self.overlap_list = Label_List(20,93, colour = lcars_blue, ofont = littlefont)

		self.burgerfull = Image.open('assets/lcarsburgerframefull.png')

		# assign x coordinates for frequency map
		self.vizX1 = 20
		self.vizY1 = 36
		self.vizX2 = 157
		self.vizY2 = 77
		self.vizW = self.vizX2 - self.vizX1 
		self.vizH = self.vizY2 - self.vizY1

		self.freqmap_grid = DrawGrid(self.vizX1, self.vizY1, self.vizW, self.vizH, lcars_grid)

		self.events = Events([1,"multi",0,"settings","poweroff",2,0,0],"modem")

	def draw_indicators(self,draw):
			idents, cur_no, max_no = plars.get_em_stats()
			self.indicator1.string = str(cur_no)
			self.indicator1.r_align(14,67,draw)

			self.overlapping_no.string = str(cur_no)
			self.overlapping_no.r_align(14,97,draw)

	def draw_title(self,title, draw):
		self.title.string = title
		self.title.r_align(self.labelxr,self.titley,draw)

	def domin_transciever(self,draw):

			# grab EM data from plars
			info = plars.get_top_em_info()[0]
			rect_coords = (self.graphx,self.graphy,self.graphx + self.gspanx,self.graphy + self.gspany)
			draw.rounded_rectangle(rect_coords, outline = lcars_grid, width = 1, radius = 2)

			# draw screen elements 
			self.Signal_Grid.push(draw)
			graphval = self.Signal_Graph.render(draw)




			self.draw_title("Dominant Transciever", draw)

			self.signal_name.push(20,35,draw, string = info[0])

			self.signal_strength.string = str(info[1]) + " DB"
			self.signal_strength.r_align(self.labelxr,92,draw)
			self.signal_frequency.push(20,92,draw, string = str(info[3])+"GHz")
			self.signal_mac.push(20,111, draw, string = info[6])

	# Draws a list of APs with data.
	def em_scan(self, draw):
			
			self.draw_title("Modulated EM Scan", draw)

			# list to hold the data labels
			list_for_labels = []

			# grab EM list
			em_list = plars.get_recent_em_list()

			if len(em_list) > 0:
				#sort it so strongest is first
				sorted_em_list = sorted(em_list, key=itemgetter(1), reverse = True)

				# prepare a list of the data received for display
				for ssid in sorted_em_list:
					name = str(ssid[0])
					strength = str(ssid[1])

					label = strength + " dB • " + name

					list_for_labels.append(label)
				

				self.list.update(list_for_labels,draw)

	def em_statistics(self,draw):
		
		idents, cur_no, max_no = plars.get_em_stats()

		self.draw_title("Modulated EM Stats", draw)

		str1 = "APs Detected: " + str(cur_no)
		str2 = "Most Detected: " + str(max_no) 
		str3 = "Uniques: " + str(len(idents))

		# list to hold the data labels
		list_for_labels = [str1, str2, str3]


		self.list.update(list_for_labels,draw)

	def mod_bt(self,draw):
		self.draw_title("Modulated BT Scan", draw)

		# list to hold the data labels
		list_for_labels = []

		# grab EM list
		bt_list = plars.get_recent_bt_list()


		# prepare a list of the data received for display
		if len(bt_list) > 0:
			for bt in bt_list:
				name = str(bt[0])
				address = str(bt[6])

				label = name + " - " + address

				list_for_labels.append(label)

	def frequency_map(self,draw):
		# returns the data necessary for freq_intensity map with EM.
		# displays each SSID as a line segment. Its position along the x is
		# determined by frequency. Its height by its signal strength.

			# value to store visualization envelope
			vizX1 = 20
			vizY1 = 36
			vizX2 = 157
			vizY2 = 77

			ballsize = 6

			focus_freq = 0
			overlapping = []

			# change Background
			#draw.rectangle((0,0,320,240),(0,0,0))
			#draw._image = self.burgerfull	



			#draw labels
			self.draw_title("EM Channel Analysis", draw)

			#grab EM list
			unsorted_em_list = plars.get_recent_em_list()
			noossids = len(unsorted_em_list)


			self.freqmap_grid.push(draw)

			if len(unsorted_em_list) > 0:

				# sort it so strongest is first.
				em_list = sorted(unsorted_em_list, key=itemgetter(1), reverse = True)

				# create a list to hold just the info we need for the screen.
				items_list = []
				strength_list = []

				for ssid in em_list:
					strength = ssid[1]
					strength_list.append(strength)

				#filter info into items_list
				for ssid in em_list:
					name = str(ssid[0])
					strength = ssid[1]
					frequency = ssid[3]
					#frequency = float(frequency.replace(' GHz', ''))

					# determing x coordinate
					screenpos = numpy.interp(frequency,(2.412, 2.462),(vizX1 + ballsize, vizX2 - ballsize))

					# determine y coordinate
					lineheight = numpy.interp(strength, (min(strength_list), max(strength_list)), (vizY2 - ballsize, vizY1 + ballsize))

					# package into list
					this_ssid = (name,screenpos,lineheight,strength,frequency)
					items_list.append(this_ssid)
					


				# draw lines and balls
				#for each item in item_list, in reverse order
				for index, item in reversed(list(enumerate(items_list))):

					# determine dot coordinates.
					cords = ((item[1],vizY2),(item[1],item[2]))
					radius = ballsize/2
					x1 = cords[1][0] - (radius)
					y1 = cords[1][1] - (radius)
					x2 = cords[1][0] + (radius)
					y2 = cords[1][1] + (radius)

					# if this is the strongest signal draw labels and change colour.
					if index == 0:
						draw.line(cords,lcars_peach,1)
						draw.ellipse([x1,y1,x2,y2],lcars_peach)


						name = item[0]
						trunc_name = name[:16] + (name[16:] and '..')

						focus_freq = item[4]


						# draw the strongest signals name
						self.signal_name_sm.push(20,80,draw,string = trunc_name)

						# put strength at lower left
						strength_string = str(item[3]) + " DB"
						#self.signal_strength_sm.push(19,114,draw,string = strength_string)

						# put frequency at lower right
						self.signal_frequency_sm.string = str(focus_freq) + " GHZ" + ", " + strength_string
						self.signal_frequency_sm.r_align(155,82,draw)


					# otherwise just draw the line and dot in the usual color
					else:
						draw.line(cords,lcars_blue,1)
						draw.ellipse([x1,y1,x2,y2],lcars_blue)

			#draw round rect background
			draw.rounded_rectangle((vizX1,vizY1,vizX2,vizY2), outline = lcars_grid, width = 1, radius = 3)


			label_list = []

			for item in items_list:
				if item[4] == focus_freq:
					overlapping.append(item)




			if len(overlapping) > 1:
				del overlapping[0]
				for ssid in overlapping:
					name = ssid[0]
					strength = ssid[1]
					frequency = ssid[4]

					# package into list
					this_ssid = (name,strength)
					label_list.append(this_ssid)

				self.overlap_list.colour = lcars_pink
			else:
				thislist = sorted(unsorted_em_list, key=itemgetter(1), reverse = True)
				del thislist[0]
				for ssid in thislist:
					name = ssid[0]
					strength = ssid[1]
					frequency = ssid[4]

					# package into list
					this_ssid = (name,strength)
					label_list.append(this_ssid)
				self.overlap_list.colour = lcars_blue

			self.overlap_list.update(label_list,draw)

# This is the main function called by the loop 
	def push(self, draw):

		status, payload = self.events.check()

		if payload == 1:
			self.selection += 1

			if self.selection == 4:
				self.selection = 0
		elif payload == 2:
			if self.selection == 4:
				self.selection = 0
			else:
				self.selection = 4

		if len(plars.get_top_em_info()) < 1:
			self.selection = -1

		# if no wifi available.
		if self.selection == -1:
			self.title.string = "No SSIDs Detected"
			self.title.r_align(self.labelxr,self.titley,draw)

		# details on strongest wifi network.
		if self.selection == 0:
			self.domin_transciever(draw)

		# frequency intensity map
		if self.selection == 1:
			self.frequency_map(draw)

		#list of all wifi ssids
		if self.selection == 2:
			self.em_scan(draw)
				
		if self.selection == 3:
			self.em_statistics(draw)

		# bluetooth list
		if self.selection == 4:
			self.mod_bt(draw)



		return status




# Controls the LCARS frame, measures the label and makes sure the top frame bar has the right spacing.
class MultiFrame(object):

	def __init__(self):

		# Sets the topleft origin of the graph
		self.graphx = 22
		self.graphy = 25
		self.samples = configure.samples

		# Sets the x and y span of the graph
		self.gspanx = 133
		self.gspany = 68

		self.graphcycle = 0

		self.marginleft = 23
		self.marginright= 132

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
		self.labely = 95
		self.labelx = 25



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


		self.A_Desc = LabelObj("a_string",littlefont,colour = lcars_orange)

		self.B_Desc = LabelObj("b_string",littlefont, colour = lcars_blue)

		self.C_Desc = LabelObj("c_string",littlefont, colour = lcars_pinker)

		self.focus_Label = LabelObj("test",bigfont, colour = lcars_orpeach)
		self.focus_high_Label = LabelObj("test",font, colour = lcars_peach)
		self.focus_low_Label = LabelObj("test",font, colour = lcars_bluer)
		self.focus_mean_Label = LabelObj("test",font, colour = lcars_pinker)

		self.indicatorA = LabelObj("00",littlefont, colour = (0,0,0))
		self.indicatorB = LabelObj("00",littlefont, colour = (0,0,0))
		self.indicatorC = LabelObj("00",littlefont, colour = (0,0,0))



		self.title = LabelObj("Multi-Graph",titlefont, colour = lcars_peach)

		self.events = Events(["modem",1,0,"settings","poweroff","thermal",0,0,0],"multi")

	# takes a value and sheds the second digit after the decimal place
	def arrangelabel(self,data,range = ".1f"):
		datareturn = format(float(data), range)
		return datareturn

	# defines the labels for the screen
	def labels(self):

		# Draw the status indicators

		# Graph time length
		self.indicatorA.string = self.arrangelabel(str(self.A_Graph.timelength/5))
		self.indicatorA.r_align(19,33,self.draw)

		# Auto Scale indicator
		if configure.auto[0]:
			self.indicatorB.string = "A"
		else:
			self.indicatorB.string = "M"

		self.indicatorB.r_align(19,82,self.draw)

		# Auto Scale indicator
		if configure.low_power_flag[0]:
			self.indicatorC.string = "C"
		else:
			self.indicatorC.string = "D"

		self.indicatorC.r_align(19,95,self.draw)

		# depending on which number the "selection" variable takes on. print the item and its unit symbol

		if self.selection == 0:
			raw_a = str(self.A_Data)
			adjusted_a = self.arrangelabel(raw_a)
			a_string = adjusted_a + " " + str(configure.sensor_info[configure.sensor1[0]][2])

			raw_b = str(self.B_Data)
			adjusted_b = self.arrangelabel(raw_b)
			b_string = adjusted_b + " " + str(configure.sensor_info[configure.sensor2[0]][2])

			raw_c = str(self.C_Data)
			adjusted_c = self.arrangelabel(raw_c)
			c_string = adjusted_c + " " + str(configure.sensor_info[configure.sensor3[0]][2])

			self.A_Label.string = a_string
			self.A_Label.push(self.labelx,self.labely,self.draw)

			#set string to item description
			self.A_Desc.string = str(configure.sensor_info[configure.sensor1[0]][0])[:6]
			self.A_Desc.push(self.labelx,self.labely+13,self.draw)

			self.B_Label.string = b_string
			self.B_Label.center(self.labely,self.labelx,135,self.draw)

			#set string to item description
			self.B_Desc.string = str(configure.sensor_info[configure.sensor2[0]][0])[:6]
			self.B_Desc.center(self.labely+13,self.labelx,135,self.draw)

			self.C_Label.string = c_string
			self.C_Label.r_align(156,self.labely,self.draw)

			#set string to item description
			self.C_Desc.string = str(configure.sensor_info[configure.sensor3[0]][0])[:6]
			self.C_Desc.r_align(156,self.labely+13,self.draw)

		# displays more details for whatever sensor is in focus
		if self.selection != 0:

			carousel = [self.A_Data,self.B_Data,self.C_Data]
			carousel2 = [configure.sensor_info[configure.sensor1[0]][2],configure.sensor_info[configure.sensor2[0]][2],configure.sensor_info[configure.sensor3[0]][2]]

			this = self.selection - 1

			this_bundle = self.Graphs[this]

			raw = str(carousel[this])

			adjusted = self.arrangelabel(raw, '.2f')
			self.focus_Label.string = adjusted + str(carousel2[this])
			self.focus_Label.r_align(156,self.titley-2,self.draw)

			self.focus_high_Label.string = "max " + self.arrangelabel(str(this_bundle.get_high()), '.1f')
			self.focus_high_Label.push(self.labelx,self.labely,self.draw)

			self.focus_low_Label.string = "min " + self.arrangelabel(str(this_bundle.get_low()), '.1f')
			self.focus_low_Label.center(self.labely,self.labelx,135,self.draw)

			self.focus_mean_Label.string = "x- " + self.arrangelabel(str(this_bundle.get_average()), '.1f')
			self.focus_mean_Label.r_align(156,self.labely,self.draw)


	# push the image frame and contents to the draw object.
	def push(self,draw):

		# returns mode_a to the main loop unless something causes state change
		status,payload  = self.events.check()

		if payload == 1:
			self.selection += 1
			if self.selection > 3:
				self.selection = 0


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

			senseslice.append(["47", dsc, dev, sym, mini, maxi])



		# Draws the Title
		if self.selection != 0:
			this = self.selection - 1
			self.title.string = senseslice[this][1]
			self.title.push(self.titlex,self.titley,draw)
		else:
			self.title.string = "Multi-Graph"
			self.title.r_align(156,self.titley,draw)



		# turns each channel on individually
		if self.selection == 0:
			self.C_Data = self.C_Graph.render(self.draw)
			self.B_Data = self.B_Graph.render(self.draw)
			self.A_Data = self.A_Graph.render(self.draw)



		if self.selection == 1:
			self.A_Data = self.A_Graph.render(self.draw)

		if self.selection == 2:
			self.B_Data = self.B_Graph.render(self.draw)

		if self.selection == 3:
			self.C_Data =  self.C_Graph.render(self.draw)


		self.labels()
		#self.indicatorA.string = self.arrangelabel(str(self.A_Graph.timelength))
		#self.indicatorA.r_align(19,33,draw)



		return status

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

		self.indicatorA = LabelObj("00",littlefont, colour = (0,0,0))
		self.indicatorB = LabelObj("00",littlefont, colour = (0,0,0))
		self.indicatorC = LabelObj("00",littlefont, colour = (0,0,0))


		self.events = Events(["modem",1,0,"settings","poweroff","multi",0,0],"thermal")


	# this function takes a value and sheds the second digit after the decimal place
	def arrangelabel(self,data):
		
		datareturn = format(float(data), '.0f')
		return datareturn

	def labels(self):
		# Draw the status indicators

		# Graph time length
		self.indicatorA.string = "47"
		self.indicatorA.r_align(19,33,self.draw)

		# Auto Scale indicator
		if configure.auto[0]:
			self.indicatorB.string = "I"
		else:
			self.indicatorB.string = "R"

		self.indicatorB.r_align(19,82,self.draw)

		# Auto Scale indicator
		if configure.low_power_flag[0]:
			self.indicatorC.string = "C"
		else:
			self.indicatorC.string = "D"

		self.indicatorC.r_align(19,95,self.draw)

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

		# ------------- Input handling -------------- #
		status,payload  = self.events.check()
		if payload == 1:
			self.selection += 1
			if self.selection > 1:
				self.selection = 0



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
		self.image = Image.open('assets/lcarsframe.png')
		self.blankimage = Image.open('assets/lcarsframeblank.png')
		self.tbar = Image.open('assets/lcarssplitframe.png')
		self.burger = Image.open('assets/lcarsburgerframe.png')
		self.burgerfull = Image.open('assets/lcarsburgerframefull.png')
		self.tr109_schematic = Image.open('assets/tr109.png')

		# Load assets
		self.logo = Image.open('assets/picorderOS_logo.png')

		self.status = "mode_a"

		self.multi_frame = MultiFrame()
		self.settings_frame = SettingsFrame()
		self.thermal_frame = ThermalFrame()
		self.powerdown_frame = PowerDown()
		self.em_frame = EMFrame()	
		self.startup_frame = StartUp()
		self.loading_frame = LoadingFrame()
		self.msd_frame = MasterSystemsDisplay()

		# carousel dict to hold the keys and defs for each state
		self.carousel = {"startup":self.start_up,
				   "multi":self.graph_screen,
				   "voc":self.voc_screen,
				   "thermal":self.thermal_screen,
				   "modem":self.em_screen,
				   "settings":self.settings,
				   "msd":self.msd,
				   "poweroff":self.powerdown,
				   "shutdown":self.powerdown}

	def get_size(self):
		return self.multi_frame.samples

	def start_up(self):
		self.newimage = self.burgerfull.copy()
		self.newimage.paste(self.logo,(59,15))
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.startup_frame.push(self.draw)
		self.pixdrw()

		return self.status

	# simple frame to let user know new info is loading while waiting.
	def loading(self):
		self.newimage = self.burgerfull.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		self.status = self.loading_frame.push(self.draw,self.status)

		self.pixdrw()
		return self.status

	def graph_screen(self):
		self.newimage = self.image.copy()
		self.draw = ImageDraw.Draw(self.newimage)

		last_status = self.status
		self.status = self.multi_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()
		else:
			self.loading()

		return self.status

	def voc_screen(self):
		pass

	def em_screen(self):
		self.newimage = self.tbar.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		last_status = self.status
		self.status = self.em_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()
		else:
			self.loading()
		return self.status

	def thermal_screen(self):
		self.newimage = self.image.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		last_status = self.status
		self.status = self.thermal_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()
		else:
			self.loading()

		return self.status

	def settings(self):
		self.newimage = self.burger.copy()
		self.draw = ImageDraw.Draw(self.newimage)
		last_status = self.status
		self.status = self.settings_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()
		else:
			self.loading()
		return self.status

	def msd(self):
		
		self.newimage = self.blankimage.copy()
		self.newimage.paste(self.tr109_schematic,(113,38))
		self.draw = ImageDraw.Draw(self.newimage)
		last_status = self.status
		self.status = self.msd_frame.push(self.draw)

		if self.status == last_status:
			self.pixdrw()
		else:
			self.loading()
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

	def run(self):
		configure.status[0] = self.carousel[configure.status[0]]()