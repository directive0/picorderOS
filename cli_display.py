import curses
from curses import wrapper
import os
import psutil
import numpy

from operator import itemgetter

from plars import *
from objects import *


error = ""
frame = 0

title = "[PicorderOS]----------------------------[CLI MODE]"

run = True

stdscr = curses.initscr()
curses.noecho()
curses.nocbreak()
stdscr.keypad(True)
curses.curs_set(False)

logo = """ :==+=+=-  .==+=+-- 
 +      .+--      :-
 +   .:. :+  :..  -:
 :+    :=+#=-    .+ 
  :+:  :####=. .=+  
    :*##*+++###*.   
   :*+:       -*+.  
  =+.        .::+#: 
 =*      .=*+=-:-#* 
:+    .=+=.      -#-
*-  :+=.        .*.*
#- =*.         -+. #
*===         :+=   *
.*#.      .-*=    -=
 =#-  .:=++:      *.
  +#+==-:       :*- 
   -#=.       :++:  
     -**+===+#+:    
"""

class Start_Frame(object):
	def __init__(self):
		self.bootto = "multi"
		self.started = False
		self.timesup = timer()
		self.logoxy = [2,2]
		self.titlexy = [1,1]

	def display(self):

		if not self.started:
			self.timesup.logtime()
			self.started = True

		# display splash logo
		if self.started:
			for y, line in enumerate(logo.splitlines(), self.logoxy[1]):
				stdscr.addstr(y, self.logoxy[0], line)

			

			if self.timesup.timelapsed() >= configure.boot_delay and configure.sensor_ready[0]:
				self.started = False
				return "multi"


		return "startup"
# A pointless indicator widget to mimic the Alpha Beta Gamma Delta annunciators from the prop.
class abgd(object):

	def __init__(self,y,x):
		self.x = x
		self.y = y
		self.titles =  ["ALPHA", "BETA", "GAMMA", "DELTA"]
		self.symbols = ["████", "    ", "    ", "    "]
		self.frame = 0
		self.timeit = timer()
		self.timeit.logtime()
		self.interval = .25

	def draw(self):

		for i in range(len(self.titles)):
			loc = self.y + (i * 2)
			stdscr.addstr(loc+1,self.x,self.titles[i])
			stdscr.addstr(loc,self.x,self.symbols[i])

		if self.timeit.timelapsed() >= self.interval:
			item = self.symbols.pop()
			self.symbols.insert(0,item)
			self.timeit.logtime()


class graph(object):

	def __init__(self,y,x,w,h,title = "graph"):
		self.cursor = 0
		self.y, self.x = y,x
		self.w, self.h = w,h
		self.g_low = self.y + self.h
		self.buffer = []
		self.data_buffer = []
		self.range = (0,100)
		self.draw_range = (self.g_low, self.y)
		self.title = title

	def set_cursor(self,cur):
		self.cursor = cur

	def render(self, data):

		self.data_buffer.insert(0,data)

		if len(self.data_buffer) > 0:
			this_range = (min(self.data_buffer),max(self.data_buffer))
		else:
			this_range = self.range

		stdscr.addstr(self.y-1,self.x,self.title)
		stdscr.addstr(self.y-1,self.x+len(self.title)+1,str(data))

		for i in range(self.w):
			if len(self.data_buffer) > i:
				result = int(numpy.interp(self.data_buffer[i],this_range,self.draw_range))
				self.buffer.insert(0, result)

		# draw envelope
		# go column by column
		block = ' '
		for column in range(self.w):
			position = column + self.x
			# determine distance from last notch
			if column > 0 and column < len(self.buffer):
				now = self.buffer[column]
				last = self.buffer[column - 1]
				difference = now - last
				#only draw a tail if needed
				if abs(difference) > 1:
					if difference < 0:
						for i in range(abs(difference)):
							stdscr.addch(self.buffer[column]+i,position,block,curses.A_REVERSE)
					else:
						for i in range(abs(difference)):
							stdscr.addch(self.buffer[column]-i,position,block,curses.A_REVERSE)

			if column < len(self.buffer):

				# draw this point
				stdscr.addch(self.buffer[column],position,block,curses.A_REVERSE)
			else:
				#no data
				stdscr.addstr(self.g_low,position,"X")

		n = len(self.data_buffer)

		for i in range(0, n - self.w):
			self.data_buffer.pop()


class Multi_Frame(object):

	def __init__(self):

		self.error = ""
		self.indicators = abgd(4,2)
		self.graph0 = graph(4,9,40,5,title = "Temp")
		self.graph1 = graph(14,9,40,5,title = "Baro")
		self.graph2 = graph(24,9,40,5,title = "Humid")

		self.datas = [47,47,47]
		self.titles = ["default", "default", "default"]
		self.events = Events(["modem"],"multi")


	def display(self):

		# returns mode to the main loop unless something causes state change
		status,payload  = self.events.check()

		self.indicators.draw()

		#gathers the data for all three sensors currently selected for each slot.
		for i in range(3):

			# determines the sensor keys for each of the three main sensors
			this_index = int(configure.sensors[i][0])

			# grabs the sensor metadata for display
			dsc,dev,sym,maxi,mini = configure.sensor_info[this_index]

			# grabs sensor data
			value = plars.get_recent(dsc,dev,num=1)[0]

			if len(value) > 0:
				self.titles[i] = dsc
				self.datas[i] = value[0]
			else:
				self.titles[i] = "OFFLINE"
				self.datas[i] = 47

		self.graph0.title = self.titles[0]
		self.graph0.render(self.datas[0])

		self.graph1.title = self.titles[1]
		self.graph1.render(self.datas[1])

		self.graph2.title = self.titles[2]
		self.graph2.render(self.datas[2])



		return status




class EM_Frame(object):
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


		# assign x coordinates for frequency map
		self.vizX1 = 20
		self.vizY1 = 36
		self.vizX2 = 157
		self.vizY2 = 77
		self.vizW = self.vizX2 - self.vizX1 
		self.vizH = self.vizY2 - self.vizY1

		self.events = Events(["multi",0,0],"modem")

	# Draws a list of APs with data.
	def em_scan(self):
			
			stdscr.addstr(2,2,"Modulated EM Scan")

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
				


				for y, line in enumerate(list_for_labels, 3):
					if y <= stdscr.getmaxyx()[0]:
						stdscr.addstr(y, 2, line)
			else:
				stdscr.addstr(2, 2, "No SSIDS Detected OR PLARS Error!")

	def display(self):
		self.em_scan()
		return "modem"

# function to shut down CLI if needed from outside this loop.
def cli_reset(self):
	curses.nocbreak()
	stdscr.keypad(False)
	curses.echo()

class CLI_Display(object):

	def __init__(self):
		self.refresh = timer()
		self.refreshrate = .2 

		self.startup = Start_Frame()
		self.multi_frame = Multi_Frame()
		self.em_frame = EM_Frame()

		# carousel dict to hold the keys and defs for each state
		self.carousel = {"startup":self.start_up,
				   "multi":self.graph_screen,
				   "modem":self.em_screen,
				   "settings":self.settings,
				   "msd":self.msd,
				   "powerdown":self.powerdown}

	def start_up(self):
		return self.startup.display()

	def graph_screen(self):
		return self.multi_frame.display()

	def em_screen(self):
		return self.em_frame.display()

	def settings(self):
		pass

	def msd(self):
		pass

	def powerdown(self):
		pass

	def run(self):

		if self.refresh.timelapsed() > self.refreshrate:

			# Clear the screen
			stdscr.erase()

			# Add the Window Title
			stdscr.addstr(0,0,title)

			# retrieve status from whatever frame matches current status
			configure.status[0] = self.carousel[configure.status[0]]()
			
			# Draw the screen
			stdscr.refresh()
			
			# keep track of time for refresh
			self.refresh.logtime()
