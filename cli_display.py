import curses
from curses import wrapper
import os
import psutil
import numpy
import socket

from sshkeyboard import listen_keyboard


from operator import itemgetter

from plars import *
from objects import *


error = ""
frame = 0

title = "[PicorderOS]--------------------------------------"


run = True

stdscr = curses.initscr()
curses.noecho()
curses.nocbreak()
stdscr.keypad(True)
curses.curs_set(False)

rows, cols = stdscr.getmaxyx()

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


map = """             @   .-                            
       +@=-@   @@@@@            @@@@           
 @@@@@@@@@@- @ *@@ :   =@@@@@@@@@@@@@@@@@@@@@@ 
 @  @@@@@@  @@       : . @@@@@@@@@@@@@@@   @   
     @@@@@@@@:@      #@@@@@@@@@@@@@@@@@@@      
     @@@@@@@         @     %@ @@@@@@@@=  @     
      @@            @@@@@@=@@ @@@@@@@@@        
        @@          @@@@@@@ @.  @*  @  #       
           @@@@        @@@@@@    :  @ @#       
           @@@@@@*      @@@@              @-   
            #@@@=       @@@ @         -@@@@  . 
            @@@         *@            @@@@@@   
            @                                @ 
                                               
-----------------------------------------------"""

class keyboard_events(object):
	
	def __init__(self):
		self.keymap = {'left':0,'up':1,'right':2}
		listen_keyboard(on_press=self.check)

	def check(self,key):

		for keys in self.keymap:
			if key == keys:
				configure.eventlist[self.keymap[keys]] = True
				configure.eventready[0] = True


class Start_Frame(object):
	def __init__(self):
		self.bootto = "multi"
		self.started = False
		self.timesup = timer()
		self.logoxy = [15,2]
		self.titlexy = [1,25]

	def display(self):

		if not self.started:
			self.timesup.logtime()
			self.started = True
		


		# display splash logo
		if self.started:

			stdscr.addstr(self.titlexy[1],self.titlexy[0],configure.boot_message)

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

class PLARS_Graph():

	def __init__(self,y,x,w,h,setting):
		self.cursor = 0
		self.y, self.x = y,x
		self.w, self.h = w,h
		self.g_low = self.y + self.h
		self.data = 47
		self.buffer = []
		self.data_buffer = []
		self.range = (0,100)
		self.draw_range = (self.g_low, self.y)
		self.setting = setting
		self.dsc = 'none'
		self.dev = 'none'
		self.sym = 'none'

	def get_identity(self):

		# determines the sensor keys for each of the three main sensors
		this_index = int(configure.sensors[self.setting][0])
		infopack = configure.sensor_info

		if len(infopack) > 0:
			self.dsc,self.dev,self.sym,maxi,mini = configure.sensor_info[this_index]

		# grabs the sensor metadata for display

	def render(self):

		self.get_value()

		self.data_buffer.insert(0,self.data)

		if len(self.data_buffer) > 0:
			this_range = (min(self.data_buffer),max(self.data_buffer))
		else:
			this_range = self.range

		# Draw description
		stdscr.addstr(self.y-2,self.x,self.title)

		# Draw value
		stdscr.addstr(self.y-2,self.x+len(self.title)+1,str(self.data))

		# update the graph buffer
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




class graph(object):

	def __init__(self,y,x,w,h,setting):
		self.cursor = 0
		self.y, self.x = y,x
		self.w, self.h = w,h
		self.g_low = self.y + self.h
		self.data = 47
		self.buffer = []
		self.data_buffer = []
		self.range = (0,100)
		self.draw_range = (self.g_low, self.y)
		self.setting = setting
		self.dsc = 'none'
		self.dev = 'none'
		self.sym = 'none'

		

	def get_identity(self):

		# determines the sensor keys for each of the three main sensors
		this_index = int(configure.sensors[self.setting][0])
		infopack = configure.sensor_info

		if len(infopack) > 0:
			self.dsc,self.dev,self.sym,maxi,mini = configure.sensor_info[this_index]

		# grabs the sensor metadata for display
		

	def get_value(self):
		self.get_identity()
		# grabs sensor data
		value = plars.get_recent(self.dsc,self.dev,num=1)[0]
		
		if len(value) > 0:
			self.title = self.dsc
			self.data = value[0]
		else:
			self.title = "OFFLINE"
			self.data = 47
		
	def set_cursor(self,cur):
		self.cursor = cur

	def render(self):

		self.get_value()

		self.data_buffer.insert(0,self.data)

		if len(self.data_buffer) > 0:
			this_range = (min(self.data_buffer),max(self.data_buffer))
		else:
			this_range = self.range

		# Draw description
		stdscr.addstr(self.y-2,self.x,self.title)

		# Draw value
		stdscr.addstr(self.y-2,self.x+len(self.title)+1,str(self.data))

		# update the graph buffer
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
		self.graph0 = graph(4,9,40,5,0)
		self.graph1 = graph(14,9,40,5,1)
		self.graph2 = graph(24,9,40,5,2)

		self.datas = [47,47,47]
		self.titles = ["default", "default", "default"]
		self.events = Events(["modem"],"multi")


	def display(self):

		# returns mode to the main loop unless something causes state change
		status,payload  = self.events.check()

		self.indicators.draw()

		self.graph0.render()
		self.graph1.render()
		self.graph2.render()

		return status
	
class Master_Systems_Display_Frame(object):
	def __init__(self):

		self.events = Events(["multi",0,0],"msd")

		# grabs the RPI model info
		if not configure.pc:
			text = os.popen("cat /proc/device-tree/model").readline()
			self.model = str(text.rstrip("\x00")).replace("Raspberry Pi","Raspi")
		else:
			self.model = "Unknown"


	def display(self):

		lasty = 0

		# returns mode to the main loop unless something causes state change
		status,payload  = self.events.check()

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
		cpu_name = "CPU:  " + self.model
		PLARS_size, PLARS_em_size = plars.get_plars_size()
		db_size = "PLARS Size:  " + str(PLARS_size)
		em_size = "PLARS EM Size:  " + str(PLARS_em_size)

		# Device Info
		stdscr.addstr(3, 2, "Device")
		stdscr.addstr(4, 2, host_str)
		stdscr.addstr(5, 2, cpu_name)

		stdscr.addstr(7, 2, "Network Uplink")
		stdscr.addstr(8, 2, wifi)
		stdscr.addstr(9, 2, ip_str)

		stdscr.addstr(11, 2, "PLARS Database Status")
		stdscr.addstr(12, 2, sense_ready)
		stdscr.addstr(13, 2, db_size)
		stdscr.addstr(14, 2, em_size)

		
		return status

class Position_Frame(object):
	def __init__(self):
		self.last_position = [47,47]
		self.mapx = 1
		self.mapy = 2
		self.events = Events(["msd",0,0],"position")

	def retrieve_data(self):

		if configure.gps:
			value = plars.get_recent("GPS Speed","gps",num=1)[0]
		else:
			return 47

		if len(value) > 0:
			return value
		else:
			return 47

	def display(self):

		lasty = 0

		# returns mode to the main loop unless something causes state change
		status,payload  = self.events.check()

		stdscr.addstr(7,1,"Orbit Supplied Position")

		for y, line in enumerate(map.splitlines(), self.mapy):
			stdscr.addstr(y, self.mapx, line)
			lasty = y
			
		locationy = int(numpy.interp(configure.position[0],[-90,90],[lasty,self.mapy]))
		locationx = int(numpy.interp(configure.position[1],[-180,180],[self.mapx,self.mapx + 47]))
		stdscr.addstr(locationy, locationx, "+")

		stdscr.addstr(17, 2, "Current Location")
		stdscr.addstr(18, 2, "Lat = " + str(configure.position[0]))
		stdscr.addstr(19, 2, "Lon = " + str(configure.position[1]))
		stdscr.addstr(20, 2, "Speed = " + str(self.retrieve_data()))

		
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

		self.events = Events(["position",0,0],"modem")

	# Draws a list of APs with data.
	def em_scan(self):
			
			stdscr.addstr(7,2,"Modulated EM Scan")

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
				


				for y, line in enumerate(list_for_labels, 8):
					if y <= stdscr.getmaxyx()[0]:
						stdscr.addstr(y, 2, line)
			else:
				stdscr.addstr(2, 2, "No SSIDS Detected OR PLARS Error!")


	def em_statistics(self):
		
		idents, cur_no, max_no = plars.get_em_stats()

		stdscr.addstr(2,2,"Modulated EM Stats")

		str1 = "APs Detected: " + str(cur_no)
		str2 = "Most Detected: " + str(max_no) 
		str3 = "Uniques: " + str(len(idents))

		# list to hold the data labels
		list_for_labels = [str1, str2, str3]

		for y, line in enumerate(list_for_labels, 3):
			if y <= stdscr.getmaxyx()[0]:
				stdscr.addstr(y, 2, line)

	def display(self):

		# returns mode to the main loop unless something causes state change
		status,payload  = self.events.check()

		self.em_statistics()
		self.em_scan()
		return status

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
		self.position_frame = Position_Frame()
		self.msd_frame = Master_Systems_Display_Frame()

		# carousel dict to hold the keys and defs for each state
		self.carousel = {"startup":self.start_up,
				   "multi":self.graph_screen,
				   "modem":self.em_screen,
				   "settings":self.settings,
				   "position":self.position,
				   "msd":self.msd,
				   "powerdown":self.powerdown}

		self.labels = {"startup":"[CLI MODE]",
				   "multi":"[MULTI GRAPH]",
				   "modem":"[MODULATED EM]",
				   "settings":"[OPERATION]",
				   "position":"[GEOGRAPHIC POSITION]",
				   "msd":"[MASTER SYSTEM DISPLAY]",
				   "powerdown":"[POWERDOWN]"}

	def start_up(self):
		return self.startup.display()

	def graph_screen(self):
		return self.multi_frame.display()

	def em_screen(self):
		return self.em_frame.display()
	
	def position(self):
		return self.position_frame.display()

	def settings(self):
		pass

	def msd(self):
		return self.msd_frame.display()

	def powerdown(self):
		pass

	def label_draw(self):
		
			# Add the Window Title
			stdscr.addstr(0,0,title)

			thislabel = self.labels[configure.status[0]]

			size = len(thislabel)

			# Add the Window Title
			stdscr.addstr(0,cols - size,thislabel)

	def run(self):

		if self.refresh.timelapsed() > self.refreshrate:

			# Clear the screen
			stdscr.erase()

			# Draw the title bar
			self.label_draw()

			# retrieve status from whatever frame matches current status
			configure.status[0] = self.carousel[configure.status[0]]()
			
			# Draw the screen
			stdscr.refresh()
			
			# keep track of time for refresh
			self.refresh.logtime()
