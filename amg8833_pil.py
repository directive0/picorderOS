#import pygame
import random
import math

# Load up the image library stuff to help draw bitmaps to push to the screen
import PIL.ImageOps
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from colour import Color
# The following are for LCARS colours from LCARScom.net
lcars_orange = (255,153,0)
lcars_pink = (204,153,204)
lcars_blue = (153,153,204)
lcars_red = (204,102,102)
lcars_peach = (255,204,153)
lcars_bluer = (153,153,255)
lcars_orpeach = (255,153,102)
lcars_pinker = (204,102,153)

standard_blue = (0,0,255)
standard_red = (255,0,0)

#cool = Color("blue")
cool = Color("blue")
#hot = Color("red")
hot = Color("red")
colrange = list(cool.range_to(hot, 256))

from objects import *

if not configure.pc:
	import busio
	import board
	import adafruit_amg88xx

	i2c = busio.I2C(board.SCL, board.SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c)



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
		#print("value is ", value)

		if configure.auto[0]:
			color = map(value, low, high, 0, 254)
		else:
			color = map(value, 0, 80, 0, 254)
		if color > 255:
			color = 255
		if color < 0:
			color = 0
		#colorindex = int(color)
		colorindex = int(color)
		#print("color index is ",colorindex)
		temp = colrange[colorindex].rgb
		#print(temp)
		red = int(temp[0] * 255.0)
		green = int(temp[1] * 255.0)
		blue = int(temp[2] * 255.0)

		#print(red,green,blue)

		self.count += 1

		if self.count > 255:
			self.count = 0

		#if value == low:
			#print("lowest found, coloring: ", color)

		#surface.rectangle([(self.x, self.y), (self.x + self.w, self.y + self.h)], fill = (int(color),int(color),int(color)), outline=None)
		surface.rectangle([(self.x, self.y), (self.x + self.w, self.y + self.h)], fill = (red,green,blue), outline=None)



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


		#print(self.high, self.low)
		for i in range(8):
			self.rows[i].update(self.data[i],self.high,self.low,surface)


    # Function to draw a pretty pattern to the display.
	def animate(self):
		self.dummy = makegrid(random = False)
		for x in range(8):
			for y in range(8):
					cx = x + 0.5*math.sin(self.ticks/5.0)
					cy = y + 0.5*math.cos(self.ticks/3.0)
					v = math.sin(math.sqrt(1.0*(math.pow(cx, 2.0)+math.pow(cy, 2.0))+1.0)+self.ticks)
              		#v = v + math.sin(x*10.0+self.ticks)
					v = (v + 1.0)/2.0
					v = int(v*255.0)
					self.dummy[x][y] = v
					#dsense.set_pixel(x,y,v,v,v)
		self.ticks = self.ticks+1
		return self.dummy


	def update(self):
		if not configure.pc:
			self.data = amg.pixels
		else:
			self.data = self.animate()#makegrid()

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
		#print("Average: ", self.average, ", ", "High: ", self.high,", ","Low: ", self.low)


		self.high = max(rangemax)
		self.low = min(rangemin)

		return self.average, self.high, self.low
		#print(rangesmax)
