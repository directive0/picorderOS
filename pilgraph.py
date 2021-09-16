print("Loading Python IL Module")


# PILgraph provides an object (graphlist) that will draw a new graph each frame.
# It was written to contain memory of the previous sensor readings, but this
# feature is no longer necessary.

# To do:
# - request from PLARS the N most recent values for the sensor assigned to this identifier



# it is initialized with:
# - a graph identifier so it knows which sensor to grab data for
# -

from objects import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import numpy
from array import *
from plars import *

class graph_area(object):


	def __init__(self, ident, graphcoords, graphspan, cycle = 0, colour = 0, width = 1):
		self.new = True
		self.cycle = cycle
		self.tock = timer()
		self.tock.logtime()
		self.glist = array('f', [])
		self.dlist = array('f', [])
		self.colour = colour
		self.auto = True
		self.width = width
		self.dotw = 6
		self.doth = 6
		self.buff = array('f', [])

		self.datahigh = 0
		self.datalow = 0
		self.newrange = (self.datalow,self.datahigh)

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

	# the following appends data to the list.

	def update(self, data):
		# grabs the datalist
		self.buff = self.dlist


		# if the time elapsed has reached the set interval then collect data
		if self.tock.timelapsed() >= self.cycle:

			# we load new data from the caller
			self.cleandata = data

			#append it to our list of clean data
			self.buff.append(self.cleandata)

			#pop the oldest value off
			# may remove this
#			self.buff.pop(0)
			self.tock.logtime()



	# the following pairs the list of values with coordinates on the X axis.

	# if the auto flag is set then the class will autoscale the graph so that
	# the highest and lowest currently displayed values are presented.
	# takes in a list/array with length => span
	def graphprep(self,datalist):

		# The starting X coordinate
		self.linepoint = self.spanx + self.x

		# Spacing between each point.
		self.jump = -1

		self.newlist = []

		# grabs the currently selected sensors range data
		sourcelow = configure.sensor_info[configure.sensors[self.ident][0]][1]

		sourcehigh = configure.sensor_info[configure.sensors[self.ident][0]][2]

		self.sourcerange = [sourcelow,sourcehigh]

		# get the range of the data.
		if len(datalist) > 0:
			self.datahigh = max(datalist)
			self.datalow = min(datalist)
		else:
			self.datahigh = sourcehigh
			self.datalow = sourcelow

		self.newrange = (self.datalow,self.datahigh)



		# for each vertical bar in the graph size
		for i in range(self.spanx):

			# if the cursor has data to write
			if i < len(datalist):

				# if auto scaling is on
				if self.auto == True:
					# take the sensor value received and map it against the on screen limits
					scaledata = abs(numpy.interp(datalist[i-range(self.spanx)],self.newrange,self.targetrange))
				else:
					# use the sensors stated limits as the range.
					scaledata = abs(numpy.interp(datalist[i-range(self.spanx)],self.sourcerange,self.targetrange))

				# append the current x position, with this new scaled data as the y positioning into the buffer
				self.newlist.append((self.linepoint,scaledata))
			else:
				# write intensity as scaled zero
				scaledata = abs(numpy.interp(sourcelow,self.sourcerange,self.targetrange))
				self.newlist.append((self.linepoint,scaledata))


			# increment the cursor
			self.linepoint = self.linepoint + self.jump


		return self.newlist

	def render(self, draw, auto = True, dot = True):

		self.auto = configure.auto[0]

		# for PLARS we reduce the common identifier of our currently selected sensor
		# by using its description (dsc) and device (dev): eg
		# BME680 has a thermometer and hygrometer,
		# therefore the thermometer's dsc is "thermometer" and the device is 'BME680'
		# the hygrometer's dsc is "hygrometer" and the the device is "BME680"

		# so every time through the loop PILgraph will pull the latest sensor
		# settings.

		dsc = configure.sensor_info[configure.sensors[self.ident][0]][3]
		dev = configure.sensor_info[configure.sensors[self.ident][0]][5]

		#preps the list by adding the X coordinate to every sensor value
		recent = plars.get_recent(dsc,dev,num = self.spanx)
		cords = self.graphprep(recent)


		self.buff = recent

		# draws the line graph
		draw.line(cords,self.colour,self.width)



		if dot:
			x1 = cords[0][0] - (self.dotw/2)
			y1 = cords[0][1] - (self.doth/2)
			x2 = cords[0][0] + (self.dotw/2)
			y2 = cords[0][1] + (self.doth/2)
			draw.ellipse([x1,y1,x2,y2],self.colour)
