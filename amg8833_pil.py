#import pygame
import random

# Load up the image library stuff to help draw bitmaps to push to the screen
import PIL.ImageOps
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from colour import Color

cool = Color("blue")
hot = Color("red")
colrange = list(cool.range_to(hot, 255))
print(colrange)

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

def makegrid():
	dummyvalue = []
	#
	for i in range(8):
		dummyrow = []
		for r in range(8):
			dummyrow.append(random.uniform(1.0,81.0))
		dummyvalue.append(dummyrow)

	return dummyvalue


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
		#print(value)

		color = map(value, low, high, 0, 255)
		#colorindex = int(color)
		colorindex = int(self.count)
		#print(colorindex)
		temp = colrange[colorindex].rgb
		print(temp)
		red = int(temp[0] * 255.0)
		green = int(temp[1] * 255.0)
		blue = int(temp[2] * 255.0)

		print(red,green,blue)

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

		self.rows = []
		self.high = 0.0
		self.low = 0.0

		for i in range(8):
			self.rows.append(ThermalRows(self.x, self.y + (i * (h/8)), self.w, self.h / 8))

	def update(self,surface):
		if not configure.pc:
			data = amg.pixels
		else:
			data = makegrid()
			#print(len(data))

		rangemax = []
		rangemin = []
		for i in range(8):
			thismax = max(data[i])
			thismin = min(data[i])
			rangemin.append(thismin)
			rangemax.append(thismax)

		self.high = max(rangemax)
		self.low = min(rangemin)

		print(self.high, self.low)
		for i in range(8):
			self.rows[i].update(data[i],self.high,self.low,surface)
		#print(rangesmax)
