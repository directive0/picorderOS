import time
import curses
from curses import wrapper
import sys
import os
import psutil
import numpy
import math

from plars import *
from objects import *


error = ""
frame = 0

title = "@icorderOS---------------------------------"

run = True

stdscr = curses.initscr()

curses.noecho()
curses.nocbreak()
stdscr.keypad(True)
curses.curs_set(False)


class input_handler(object):
	def __init__(self):
		pass

	def get(self):
		pass


class abgd(object):

	def __init__(self,y,x):
		self.x = x
		self.y = y
		self.titles = ["ALPHA", "BETA", "GAMMA", "DELTA"]
		self.symbols = ["██████", "    ", "    ", "    "]
		self.frame = 0
		self.timeit = Timer()
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


class Sense(object):

	def __init__(self,samplerate):
		self.buffer = []
		self.max = 0
		self.min = 0
		self.samplerate = samplerate
		self.timer = Timer()
		self.buffer = [0,0,0,0]

	def get(self):
		if self.timer.timelapsed() > self.samplerate:
			f = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
			temp = float(f[0:2] + "." + f[2:])
			cpu_percent = float(psutil.cpu_percent())
			virtmeminfo = float(psutil.virtual_memory().available * 0.0000001)
			io_counter_info = float(psutil.net_io_counters().bytes_recv * 0.00001)
			self.timer.logtime()

			self.buffer = [temp,cpu_percent,virtmeminfo,io_counter_info]
		return self.buffer


class cli_display(object):

	def __init__(self):

		self.sense = Sense(1.0)

		self.error = ""
		self.indicators = abgd(4,2)
		self.graph0 = graph(4,1,48,5,title = "Temp")
		self.graph1 = graph(14,1,48,5,title = "CPU %")

		self.refresh = Timer()
		self.refreshrate = .3

	def push(self):
		data = plars.get_top_em_info()[0]
		stdscr.clear()
		stdscr.addstr(0,0,title)
#		keyget = stdscr.getkey()
#		stdscr.addstr(1,0,keyget)
		data = self.sense.get()
		self.graph0.render(data[0])
		#self.indicators.draw()
		stdscr.refresh()

	def reset(self):
		curses.echo()
		curses.endwin()
		print(self.error)

	def run(self):
		if self.refresh.timelapsed() > self.refreshrate:
			self.push()
			self.refresh.logtime()