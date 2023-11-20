import curses
from curses import wrapper
import os
import psutil
import numpy

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

logo = """
 :==+=+=-  .==+=+-- 
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


class abgd(object):

	def __init__(self,y,x):
		self.x = x
		self.y = y
		self.titles = ["ALPHA", "BETA", "GAMMA", "DELTA"]
		self.symbols = ["██████", "    ", "    ", "    "]
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
		self.graph0 = graph(4,1,48,5,title = "Temp")
		self.graph1 = graph(14,1,48,5,title = "Baro")
		self.graph2 = graph(24,1,48,5,title = "Humid")

		self.refresh = timer()
		self.refreshrate = .2
		self.datas = [47,47,47]
		self.titles = ["default", "default", "default"]
		self.events = Events(["modem"],"multi")


	def push(self):

		stdscr.clear()
		stdscr.addstr(0,0,title)

		#gathers the data for all three sensors currently selected for each slot.
		if configure.sensor_ready[0]:

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

			stdscr.refresh()

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

		self.freqmap_grid = DrawGrid(self.vizX1, self.vizY1, self.vizW, self.vizH, lcars_grid)

		self.events = Events([1,0,0],"modem")

class cli_display(object):

	def __init__(self):

		self.startup = StartUp()
		self.multi_frame = Multi_Frame()

		# carousel dict to hold the keys and defs for each state
		self.carousel = {"startup":self.start_up,
				   "multi":self.graph_screen,
				   "modem":self.em_screen,
				   "settings":self.settings,
				   "msd":self.msd,
				   "shutdown":self.powerdown}

	def start_up(self):
		configure.status[0] = "multi"

	def graph_screen(self):
		self.status = self.multi_frame.display()

	def em_screen(self):
		pass

	def settings(self):
		pass

	def esd(self):
		pass

	def powerdown(self):
		pass

	def powerdown(self):
		curses.echo()
		curses.endwin()


	def run(self):
		if self.refresh.timelapsed() > self.refreshrate:
			configure.status[0] = self.carousel[configure.status[0]]()
			self.push()
			self.refresh.logtime()
