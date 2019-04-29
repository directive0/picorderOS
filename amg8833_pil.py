import pygame
import random

# Load up the image library stuff to help draw bitmaps to push to the screen
import PIL.ImageOps
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

#import busio
#import board
#import adafruit_amg88xx

#i2c = busio.I2C(board.SCL, board.SDA)
#amg = adafruit_amg88xx.AMG88XX(i2c)


#pygame.init()
#pygame.font.init()
#pygame.display.set_caption('amgstart')

# #the list of colors we can choose from
# blue = Color("indigo")
# colors = list(blue.range_to(Color("red"), COLORDEPTH))

#create the array of colors
# colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]
#
# displayPixelWidth = width / 30
# displayPixelHeight = height / 30
width = 320
height = 240
surface = pygame.display.set_mode((width, height))

surface.fill((0,0,0))

pygame.display.update()
#pygame.mouse.set_visible(False)

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
	# 	pygame.display.update()

class ThermalPixel(object):
	def __init__(self,x,y,w,h,surface):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.colour = (255,255,255)


		self.temp = 0
		self.surface = surface


	def update(self,value):
		print(value)
		color = map(value, 1, 81, 0, 254)
		print(color)
		pygame.draw.rect(self.surface, (color,color,color), pygame.Rect(self.x,self.y,self.w,self.h))


class ThermalRows(object):

	def __init__(self,x,y,w,h,surface):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.surface = surface

		self.pixels = []

		for i in range(8):
			self.pixels.append(ThermalPixel(self.x + (i * (w/8)), self.y, self.w / 8, self.h, self.surface))

	#[10.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0]
	def update(self,data):
		for i in range(8):
			self.pixels[i].update(data[i])



class ThermalGrid(object):

	def __init__(self,x,y,w,h,surface):
		self.x = x
		self.y = y
		self.h = h
		self.w = w

		self.surface = surface

		self.rows = []

		for i in range(8):
			self.rows.append(ThermalRows(self.x, self.y + (i * (h/8)), self.w, self.h / 8, self.surface))

	def update(self,data):
		for i in range(8):
			self.rows[i].update(data[i])


# #let the sensor initialize
# time.sleep(.1)
# a = ThermalGrid(32,32,256,168,surface)
# while(1):
# 	a.update(makegrid())#amg.pixels)
# 	#print(amg.pixels)
# 	pygame.display.flip()
#	surface =
# 	#read the pixels
	#pixels = sensor.pixels
# 	pixels = [map(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]
#
# 	#perdorm interpolation
# 	bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
#
