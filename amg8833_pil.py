print("Loading AMG8833 Thermal Camera Module")
#import pygame
import random
import math

# Load up the image library stuff to help draw bitmaps to push to the screen
import PIL.ImageOps


# from https://learn.adafruit.com/adafruit-amg8833-8x8-thermal-camera-sensor/raspberry-pi-thermal-camera
# interpolates the data into a smoothed screen res
import numpy as np
from scipy.interpolate import griddata
from colour import Color


# some utility functions
def constrain(val, min_val, max_val):
	return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from colour import Color
# The following are for LCARS colours from LCARScom.net
lcars_orange = (255,153,0)
lcars_pink = (204,153,204)
lcars_blue = (153,152,208)
lcars_red = (204,102,102)
lcars_peach = (255,204,153)
lcars_bluer = (153,153,255)
lcars_orpeach = (255,153,102)
lcars_pinker = (204,102,153)

standard_blue = (0,0,255)
standard_red = (255,0,0)

# low range of the sensor (this will be blue on the screen)
MINTEMP = -2.0

# high range of the sensor (this will be red on the screen)
MAXTEMP = 150.0

# how many color values we can have
COLORDEPTH = 1024

# pylint: disable=invalid-slice-index
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
# pylint: enable=invalid-slice-index
# sensor is an 8x8 grid so lets do a square
height = 133
width = 71

# the list of colors we can choose from
cool = Color(rgb=(0.0, 0.0, 0.0)) #Color("blue")
hot = Color(rgb=(0.8, 0.4, 0.6))#"red")
#blue = Color("indigo")
colors = list(cool.range_to(hot, COLORDEPTH))

# create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

displayPixelWidth = width / 30
displayPixelHeight = height / 30


colrange = list(cool.range_to(hot, 256))

rotate = False
fliplr = False
flipud = True

from objects import *

import sensors

if configure.amg8833:
	import adafruit_amg88xx
	import busio
	import board
	i2c = busio.I2C(board.SCL, board.SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c, addr=0x68)



#some utility functions
def constrain(val, min_val, max_val):
	return min(max_val, max(min_val, val))

def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# create an 8x8 array for testing purposes. Displays random 'sensor data'.
def makegrid(random = True):
	dummyvalue = []
	#
	for i in range(8):
		dummyrow = []
		for r in range(8):
			if random:
				dummyrow.append(random.uniform(1.0,81.0))
			else:
				dummyrow.append(0)
		dummyvalue.append(dummyrow)

	return dummyvalue

# a single pixel of temperature information
class ThermalPixel(object):

	def __init__(self,x,y,w,h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.colour = (255,255,255)
		self.temp = 0
		self.count = 0


	def update(self,value,high,low,surface):

		if configure.auto[0]:
			color = map(value, low, high, 0, 254)
		else:
			color = map(value, 0, 80, 0, 254)
		if color > 255:
			color = 255
		if color < 0:
			color = 0

		colorindex = int(color)

		temp = colrange[colorindex].rgb

		red = int(temp[0] * 255.0)
		green = int(temp[1] * 255.0)
		blue = int(temp[2] * 255.0)

		self.count += 1

		if self.count > 255:
			self.count = 0

		surface.rectangle([(self.x, self.y), (self.x + self.w, self.y + self.h)], fill = (red,green,blue), outline=None)

class ThermalColumns(object):

	def __init__(self,x,y,w,h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

		self.pixels = []

		for i in range(8):
			self.pixels.append(ThermalPixel(self.x, self.y + (i * (h/8)), self.w, self.h / 8))

	#[10.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0]
	def update(self,data,high,low,surface):
		for i in range(8):
			self.pixels[i].update(data[i],high, low, surface)

class ThermalRows(object):

	def __init__(self,x,y,w,h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

		self.pixels = []

		for i in range(8):
			self.pixels.append(ThermalPixel(self.x + (i * (w/8)), self.y, self.w / 8, self.h))

	#[10.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0]
	def update(self,data,high,low,surface):
		for i in range(8):
			self.pixels[i].update(data[i],high, low, surface)

class ThermalGrid(object):

	def __init__(self,x,y,w,h):
		self.x = x
		self.y = y
		self.h = h
		self.w = w
		self.data = []

		self.rows = []
		self.high = 0.0
		self.low = 0.0
		self.average = 0
		self.ticks = 0

		for i in range(8):
			self.rows.append(ThermalRows(self.x, self.y + (i * (h/8)), self.w, self.h / 8))

		self.update()

	def push(self,surface):
		if not configure.interpolate[0]:
			for i in range(8):
				self.rows[i].update(self.data[i],self.high,self.low,surface)
		else:
			self.interpolate(surface)
	# Function to draw a pretty pattern to the display for demonstration.
	def animate(self):

		self.dummy = makegrid(random = False)

		for x in range(8):
			for y in range(8):
					cx = x + 0.5*math.sin(self.ticks/5.0)
					cy = y + 0.5*math.cos(self.ticks/3.0)
					a = math.sin(math.sqrt(1.0*(math.pow(cx, 2.0)+math.pow(cy, 2.0))+1.0)+self.ticks)
					b = math.sin(10*(x * math.sin(self.ticks/2) + y * math.cos(self.ticks/3))+self.ticks)
					v = (a + 1.0)/2.0

					v = int(v*256.0)
					self.dummy[x][y] = v
					#dsense.set_pixel(x,y,v,v,v)
		self.ticks = self.ticks+1
		return self.dummy

	def interpolate(self, surface):

		height = self.w
		width = self.h
		displayPixelWidth = width / 30
		displayPixelHeight = height / 30

		if configure.auto[0]:
			# low range of the sensor (this will be blue on the screen)
			mintemp = self.low
			# high range of the sensor (this will be red on the screen)
			maxtemp = self.high
		else:
			mintemp = MINTEMP
			maxtemp = MAXTEMP

		pixels = []

		for row in self.data:
			pixels = pixels + list(row)
		pixels = [map_value(p, mintemp, maxtemp, 0, COLORDEPTH - 1) for p in pixels]

		# perform interpolation
		bicubic = griddata(points, pixels, (grid_x, grid_y), method="cubic")

		# draw everything
		for ix, row in enumerate(bicubic):
			for jx, pixel in enumerate(row):
				x = self.x + (displayPixelHeight * ix)
				y = self.y + (displayPixelWidth * jx)
				x2 = x + displayPixelHeight
				y2 = y + displayPixelWidth
				surface.rectangle([(x, y), (x2, y2)], fill = colors[constrain(int(pixel), 0, COLORDEPTH - 1)], outline=None)

	def update(self):

		if configure.amg8833:
			self.data = amg.pixels
		else:
			self.data = self.animate()

		if rotate:
			self.data = np.transpose(self.data).tolist()

		if fliplr:
			self.data = np.fliplr(self.data).tolist()

		if flipud:
			self.data = np.flipud(self.data).tolist()

		thisaverage = 0
		rangemax = []
		rangemin = []

		for i in range(8):

			for j in range(8):
				thisaverage += self.data[i][j]

			thismax = max(self.data[i])
			thismin = min(self.data[i])
			rangemin.append(thismin)
			rangemax.append(thismax)

		self.average = thisaverage / (8*8)

		self.high = max(rangemax)
		self.low = min(rangemin)

		return self.average, self.high, self.low
