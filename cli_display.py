import time
import curses
import sys
import os
import psutil
import numpy
import math

# pull in the picorder stuff
from objects import *
from plars import *

error = ""
frame = 0
		
title = "PicorderOS----------------------------------------"
		
run = True

stdscr = curses.initscr()

curses.noecho()
curses.nocbreak()
stdscr.keypad(True)
curses.curs_set(False)


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
		self.sense = Sense()
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
							stdscr.addstr(self.buffer[column]+i,position,"█")
					else:
						for i in range(abs(difference)):
							stdscr.addstr(self.buffer[column]-i,position,"█")

			if column < len(self.buffer):

				# draw this point
				stdscr.addstr(self.buffer[column],position,"█")
			else:
				#no data
				stdscr.addstr(self.g_low,position,"X")

		n = len(self.data_buffer)

		for i in range(0, n - self.w):
			self.data_buffer.pop()
#			self.buffer = []


class Sense(object):

	def __init__(self):
#		self.step = 0.0
#		self.step2 = 0.0
#		self.steptan = 0.0
#		totalmem = float(psutil.virtual_memory().total) / 1024

#		self.cputemp = [0, 100, "CpuTemp", self.deg_sym + "c", "RaspberryPi"]
#		self.cpuperc = [0,100,"CpuPercent","%","Raspberry Pi"]
#		self.virtmem = [0,totalmem,"VirtualMemory","b","RaspberryPi"]
#		self.bytsent = [0,100000,"BytesSent","b","RaspberryPi"]
#		self.bytrece = [0, 100000,"BytesReceived","b","RaspberryPi"]
		self.buffer = []
		self.max = 0
		self.min = 0

	def get(self):

		f = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
		temp = float(f[0:2] + "." + f[2:])
		cpu_percent = float(psutil.cpu_percent())
		virtmeminfo = float(psutil.virtual_memory().available * 0.0000001)
		io_counter_info = float(psutil.net_io_counters().bytes_recv * 0.00001)

		return [temp,cpu_percent,virtmeminfo,io_counter_info]


class CLI_display(object):

	def __init__(self):

		self.sense = Sense()

		self.error = ""
		self.indicators = abgd(4,2)
		self.graph0 = graph(3,14,32,3,title = "Temp")
		self.graph1 = graph(9,14,32,3,title = "CPU %")

	def domin_transciever(self):

		# grab EM data from plars
		info = plars.get_top_em_info()[0]

		return info



		# self.draw_title("Dominant Transciever", draw)

		# self.signal_name.push(20,35,draw, string = info[0])

		# self.signal_strength.string = str(info[1]) + " DB"
		# self.signal_strength.r_align(self.labelxr,92,draw)
		# self.signal_frequency.push(20,92,draw, string = str(info[3])+"GHz")
		# self.signal_mac.push(20,111, draw, string = info[6])



	def push(self):

		try:
			stdscr.clear()
			stdscr.addstr(0,0,title)
			data = self.sense.get()
			self.graph0.render(data[0])
			self.graph1.render(self.domin_transciever[1])
			self.indicators.draw()
			stdscr.refresh()

		except Exception as err:
			self.error = err
			self.reset()
			return False

		return True


	def reset(self):
		curses.echo()
		curses.endwin()
		print(self.error)


display = CLI_display()

while run:
	run = display.push()
	time.sleep(.3)