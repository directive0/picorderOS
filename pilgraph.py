print("Loading Python IL Module")


# PILgraph provides an object (graphlist) that will draw a new graph each frame.
# It was written to contain all the previous sensor readings, but this
# feature is no longer necessary as PLARS now handles all data history.

# To do:
# - request from PLARS the N most recent values for the sensor assigned to this identifier






from objects import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import numpy
from array import *
from plars import *
from multiprocessing import Process,Queue,Pipe

# function to calculate onscreen coordinates of graph pixels as a process.
def graph_prep_process(conn,samples,datalist,auto,newrange,targetrange,sourcerange,linepoint,jump,sourcelow):
	newlist = []
	# for each vertical bar in the graph size
	for i in range(samples):



		# if the cursor has data to write
		if i < len(datalist):

			# gives me an index within the current length of the datalist
			# goes from the most recent data backwards
			# so the graph prints from left-right: oldest-newest data.
			indexer = (len(datalist) - i) - 1

			# if auto scaling is on
			if auto == True:
				# take the sensor value received and map it against the on screen limits
				scaledata = abs(numpy.interp(datalist[indexer],newrange,targetrange))
			else:
				# use the sensors stated limits as the range.
				scaledata = abs(numpy.interp(datalist[indexer],sourcerange,targetrange))

			# append the current x position, with this new scaled data as the y positioning into the buffer
			newlist.append((linepoint,scaledata))
		else:
			# If no data just write intensity as scaled zero
			scaledata = abs(numpy.interp(sourcelow,sourcerange,targetrange))
			newlist.append((linepoint,scaledata))

		# increment the cursor
		linepoint = linepoint + jump

	conn.put(newlist)


class graph_area(object):
# it is initialized with:
# - ident: a graph identifier number so it knows which currently selected graphable sensor (0-2) this graph is
# - graphcoords: list containing the top left x,y coordinates
# - graphspan: list containing the x and y span in pixels


	def __init__(self, ident, graphcoords, graphspan, cycle = 0, colour = 0, width = 1, type = 0, samples = False):

		# if a samplesize is provided use it, otherwise grab global setting.
		if not samples:
			self.samples = configure.samples
		else:
			self.samples = samples

		self.cycle = cycle


		self.glist = array('f', [])
		self.dlist = array('f', [])

		self.colour = colour

		#controls auto scaling (set by global variable at render)
		self.auto = True

		# controls width
		self.width = width

		self.dotw = 6
		self.doth = 6
		self.buff = array('f', [])
		self.type = type

		self.timeit = timer()

		self.datahigh = 0
		self.datalow = 0
		self.newrange = (self.datalow,self.datahigh)

		self.timelength = 0

		# stores the graph identifier, there are three on the multiframe
		self.ident = ident

		# collect data for where the graph should be drawn to screen.
		self.x, self.y = graphcoords
		self.spanx,self.spany = graphspan

		# defines the vertical limits of the screen based on the area provided
		self.targetrange = ((self.y + self.spany), self.y)

		# seeds a list with the coordinates for 0 to give us a list that we
		# can put our scaled graph values in
		for i in range(self.spanx):
			self.glist.append(self.y + self.spany)

		# seeds a list with sourcerange zero so we can put our sensor readings into it.
		# dlist is the list where we store the raw sensor values with no scaling
		for i in range(self.spanx):
			self.dlist.append(self.datalow)
			self.buff.append(self.datalow)


	# the following function returns the graph list.
	def grabglist(self):
		return self.glist

	# the following function returns the data list.
	def grabdlist(self):
		return self.dlist

	# Returns the average of the current dataset
	def get_average(self):
		average = sum(self.buff) / len(self.buff)
		return average

	# returns the highest
	def get_high(self):
		return max(self.buff)

	def get_low(self):
		return min(self.buff)

	# this function calculates the approximate time scale of the graph
	def giveperiod(self):
		self.period = (self.spanx * self.cycle) / 60

		return self.period



	# the following pairs the list of values with coordinates on the X axis.

	# if the auto flag is set then the class will autoscale the graph so that
	# the highest and lowest currently displayed values are presented.
	# takes in a list/array with length => span
	def graphprep(self, datalist, ranger = None):

		index = configure.sensors[self.ident][0]

		dsc,dev,sym,maxi,mini = configure.sensor_info[index]

		# The starting X coordinate, the graph draws from right to left (new to old).
		self.linepoint = self.spanx + self.x

		# calculate how many pixels per sample the graph will take.
		spacing = self.spanx / self.samples

		# Spacing between each point.
		self.jump = -spacing



		# if this graph ISNT for WIFI.
		if self.type == 0:
			# grabs the currently selected sensors range data.
			sourcelow = mini
			sourcehigh = maxi

			self.sourcerange = [sourcelow,sourcehigh]
		#otherwise assume its for wifi.
		else:
			sourcelow = -90

			sourcehigh = -5

			self.sourcerange = [sourcelow,sourcehigh]

		# get the range of the data.
		if len(datalist) > 0:
			self.datahigh = max(datalist)
			self.datalow = min(datalist)
		else:
			self.datahigh = sourcehigh
			self.datalow = sourcelow

		self.newrange = (self.datalow,self.datahigh)



		q = Queue()
		prep_process = Process(target=graph_prep_process, args=(q,self.samples,datalist,self.auto,self.newrange,self.targetrange,self.sourcerange,self.linepoint,self.jump,sourcelow,))
		prep_process.start()

		prep_process.join()
		result = q.get()

		return result




	def render(self, draw, auto = True, dot = True, ranger = None):


		return_value = 0

		self.auto = configure.auto[0]

		# for PLARS we reduce the common identifier of our currently selected sensor
		# by using its description (dsc) and device (dev): eg
		# BME680 has a thermometer and hygrometer,
		# therefore the thermometer's dsc is "thermometer" and the device is 'BME680'
		# the hygrometer's dsc is "hygrometer" and the the device is "BME680"

		# so every time through the loop PILgraph will pull the latest sensor
		# settings.

		# standard pilgraph: takes DSC,DEV keypairs from screen drawer, asks
		# plars for data, graphs it.

		# Standard graph
		if self.type == 0:
			index = configure.sensors[self.ident][0]
			dsc,dev,sym,maxi,mini = configure.sensor_info[index]
			recent, self.timelength = plars.get_recent(dsc,dev,num = self.samples, time = True)


			# for returning last value on multigraph
			if len(recent) == 0:
				return_value = 47
			else:
				return_value = recent[-1]

		# EM pilgraph: pulls wifi data only.
		elif self.type == 1:
			recent = plars.get_top_em_history(no = self.samples)
			return_value = recent[-1]

		# Testing a new graph
		elif self.type == 2:
			recent = plars.get_recent(dsc,dev,num = self.samples)



		cords = self.graphprep(recent)
		self.buff = recent

		# draws the line graph
		draw.line(cords,self.colour,self.width)

		# draws the line dot.
		if dot:
			x1 = cords[0][0] - (self.dotw/2)
			y1 = cords[0][1] - (self.doth/2)

			x2 = cords[0][0] + (self.dotw/2)
			y2 = cords[0][1] + (self.doth/2)
			draw.ellipse([x1,y1,x2,y2],self.colour)


		return return_value
