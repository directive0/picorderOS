# tft24T    V0.3 April 2015     Brian Lavery    TJCTM24024-SPI    2.4 inch Touch 320x240 SPI LCD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.

# Calibration scaling values from the calibration utility:
# Makes touchscreen coordinates agree with TFT coordinates (240x320) for YOUR device
# You may need to adjust these values for YOUR device
calib_scale240 = 272
calib_scale320 = -364
calib_offset240 = 16
calib_offset320 = -354

margin = 13
# "margin" is a no-go perimeter (in pixels).  [Stylus at very edge of touchscreen is rather jitter-prone.]


import numbers
import time

from PIL import Image
from PIL import ImageDraw
import textwrap

from types import MethodType

# Constants for interacting with display registers.
ILI9341_TFTWIDTH    = 240
ILI9341_TFTHEIGHT   = 320

ILI9341_SWRESET     = 0x01
ILI9341_SLPOUT      = 0x11
ILI9341_INVOFF      = 0x20
ILI9341_INVON       = 0x21
ILI9341_GAMMASET    = 0x26
ILI9341_DISPON      = 0x29
ILI9341_CASET       = 0x2A
ILI9341_PASET       = 0x2B
ILI9341_RAMWR       = 0x2C
ILI9341_RAMRD       = 0x2E
ILI9341_MADCTL      = 0x36
ILI9341_PIXFMT      = 0x3A
ILI9341_FRMCTR1     = 0xB1
ILI9341_DFUNCTR     = 0xB6

ILI9341_PWCTR1      = 0xC0
ILI9341_PWCTR2      = 0xC1
ILI9341_VMCTR1      = 0xC5
ILI9341_VMCTR2      = 0xC7
ILI9341_GMCTRP1     = 0xE0
ILI9341_GMCTRN1     = 0xE1


Buffer = None
# textrotated custom method for our "draw" cannot find TFT's canvas buffer if it is not global.
# This method obviously precludes multiple instances of TFT running independently,
# but we use both CE0/CE1 of the Raspberry Pi anyway, so how could we have another display?
# (Want the second SPI of the RPI2? - Not considered in this library)

class TFT24T():
	def __init__(self, spi, gpio, landscape=False):


		self.is_landscape = landscape
		self._spi = spi
		self._gpio = gpio

# TOUCHSCREEN HARDWARE PART

	# ads7843 max spi speed 2 MHz?
	X = 0xD0
	Y = 0x90
	Z1 = 0xB0
	Z2 = 0xC0

	def initTOUCH(self, pen,  ce=0,  spi_speed=100000):
		self._ce_tch = ce
		self._spi_speed_tch=spi_speed
		self._pen = pen
		self._gpio.setup(pen, self._gpio.IN)

	def penDown(self):
		# reads True when stylus is in contact
		return not self._gpio.input(self._pen)

	def readValue(self, channel):
#        self._spi.open(0, self._ce_tch)
		self._spi.open(1,self._ce_tch)
		self._spi.max_speed_hz=self._spi_speed_tch

		responseData = self._spi.xfer([channel , 0, 0])
		self._spi.close()
		return (responseData[1] << 5) | (responseData[2] >> 3)
		# Pick off the 12-bit reply

	def penPosition(self):
		self.readValue(self.X)
		self.readValue(self.Y)
		self.readValue(self.X)
		self.readValue(self.Y)
		# burn those
		x=0
		y=0
		for k in range(10):
			x += self.readValue(self.X)
			y += self.readValue(self.Y)
		# average those
		x = x / 10
		y = y / 10
		# empirically set calibration factors:
		x2 = (4096 -x) * calib_scale240 / 4096   -calib_offset240
		y2 = y * calib_scale320 / 4096   - calib_offset320
		# So far, these co-ordinates are the native portrait mode

		if y2<margin or y2>(319-margin) or x2<margin or x2 > (239-margin):
			x2=0
			y2=0
		# The fringes of touchscreen give a lot of erratic/spurious results
		# Don't allow fringes to return anything.
		# (Also, user should not program hotspots/icons out in the margin, to discourage pointing pen there)
		# a return of (0,0) is considered a nul return

		if self.is_landscape:
			# rotate the coordinates
			x3 = x2
			x2 = 319-y2
			y2 = x3
		return [x2, y2]


#    TFT/LCD part

	def send2lcd(self, data, is_data=True, chunk_size=4096):

		# Set DC low for command, high for data.
		self._gpio.output(self._dc, is_data)
		self._spi.open(0, self._ce_lcd)
		self._spi.max_speed_hz=self._spi_speed_lcd

		# Convert scalar argument to list so either can be passed as parameter.
		if isinstance(data, numbers.Number):
			data = [data & 0xFF]
		# Write data a chunk at a time.
		for start in range(0, len(data), chunk_size):
			end = min(start+chunk_size, len(data))
			self._spi.writebytes(data[start:end])
		self._spi.close()

	def command(self, data):
		"""Write a byte or array of bytes to the display as command data."""
		self.send2lcd(data, False)

	def data(self, data):
		"""Write a byte or array of bytes to the display as display data."""
		self.send2lcd(data, True)

	def resetlcd(self):
		if self._rst is not None:
			self._gpio.output(self._rst, self._gpio.HIGH)
			time.sleep(0.005)
			self._gpio.output(self._rst, self._gpio.LOW)
			time.sleep(0.02)
			self._gpio.output(self._rst, self._gpio.HIGH)
			time.sleep(0.150)
		else:
			self.command(ILI9341_SWRESET)
			sleep(1)

	def _init9341(self):
		self.command(ILI9341_PWCTR1)
		self.data(0x23)
		self.command(ILI9341_PWCTR2)
		self.data(0x10)
		self.command(ILI9341_VMCTR1)
		self.data([0x3e, 0x28])
		self.command(ILI9341_VMCTR2)
		self.data(0x86)
		self.command(ILI9341_MADCTL)
		self.data(0x48)
		self.command(ILI9341_PIXFMT)
		self.data(0x55)
		self.command(ILI9341_FRMCTR1)
		self.data([0x00, 0x18])
		self.command(ILI9341_DFUNCTR)
		self.data([0x08, 0x82, 0x27])
		self.command(0xF2)
		self.data(0x00)
		self.command(ILI9341_GAMMASET)
		self.data(0x01)
		self.command(ILI9341_GMCTRP1)
		self.data([0x0F, 0x31, 0x2b, 0x0c, 0x0e, 0x08, 0x4e, 0xf1, 0x37, 0x07, 0x10, 0x03, 0x0e, 0x09, 0x00])
		self.command(ILI9341_GMCTRN1)
		self.data([0x00, 0x0e, 0x14, 0x03, 0x11, 0x07, 0x31, 0xc1, 0x48, 0x08, 0x0f, 0x0c, 0x31, 0x36, 0x0f])
		self.command(ILI9341_SLPOUT)
		time.sleep(0.120)
		self.command(ILI9341_DISPON)

	def initLCD(self, dc=None, rst=None, led=None, ce=0, spi_speed=32000000):
		global Buffer
		self._dc = dc
		self._rst = rst
		self._led = led
		self._ce_lcd = ce
		self._spi_speed_lcd=spi_speed
		# Set DC as output.
		self._gpio.setup(dc, self._gpio.OUT)
		# Setup reset as output (if provided).
		if rst is not None:
			self._gpio.setup(rst, self._gpio.OUT)
		if led is not None:
			self._gpio.setup(led, self._gpio.OUT)
			self._gpio.output(led, self._gpio.HIGH)

		# Create an image buffer.
		if self.is_landscape:
			Buffer = Image.new('RGB', (ILI9341_TFTHEIGHT, ILI9341_TFTWIDTH))
		else:
			Buffer = Image.new('RGB', (ILI9341_TFTWIDTH, ILI9341_TFTHEIGHT))
		# and a backup buffer for backup/restore
		self.buffer2 = Buffer.copy()
		self.resetlcd()
		self._init9341()

	def set_frame(self, x0=0, y0=0, x1=None, y1=None):

		if x1 is None:
			x1 = ILI9341_TFTWIDTH-1
		if y1 is None:
			y1 = ILI9341_TFTHEIGHT-1
		self.command(ILI9341_CASET)        # Column addr
		self.data([x0 >> 8, x0, x1 >> 8, x1])
		self.command(ILI9341_PASET)        # Row addr
		self.data([y0 >> 8, y0, y1 >> 8, y1])
		self.command(ILI9341_RAMWR)

	def display(self, image=None):
		"""Write the display buffer or provided image to the hardware.  If no
		image parameter is provided the display buffer will be written to the
		hardware.  If an image is provided, it should be RGB format and the
		same dimensions as the display hardware.
		"""
		# By default write the internal buffer to the display.
		if image is None:
			image = Buffer
		if image.size[0] == 320:
			image = image.rotate(90)

		# Set address bounds to entire display.
		self.set_frame()
		# Convert image to array of 16bit 565 RGB data bytes.
		pixelbytes = list(self.image_to_data(image))
		# Write data to hardware.
		self.data(pixelbytes)

	def penprint(self, position, size, color=(0,0,0) ):
		x=position[0]
		y=position[1]
		if self.is_landscape:
			# rotate the coordinates. The intrinsic hardware is portrait
			x3 = x
			x = y
			y = 319-x3
		self.set_frame(x, y-size, x+size, y+size)
		pixelbytes=[0]*(size*size*8)
		self.data(pixelbytes)


	def clear(self, color=(0,0,0)):
		"""
		Clear the image buffer to the specified RGB color (default black).
		USE (r, g, b) NOTATION FOR THE COLOUR !!
		"""

		if type(color) != type((0,0,0)):
			print("clear() function colours must be in (255,255,0) form")
			exit()
		width, height = Buffer.size
		Buffer.putdata([color]*(width*height))
		self.display()

	def draw(self):
		"""Return a PIL ImageDraw instance for drawing on the image buffer."""
		d = ImageDraw.Draw(Buffer)
		# Add custom methods to the draw object:
		d.textrotated = MethodType(_textrotated, d, ImageDraw.Draw)
		d.pasteimage = MethodType(_pasteimage, d, ImageDraw.Draw)
		d.textwrapped = MethodType(_textwrapped, d, ImageDraw.Draw)
		return d

	def load_wallpaper(self, filename):
		# The image should be 320x240 or 240x320 only (full wallpaper!). Errors otherwise.
		# We need to cope with whatever orientations file image and TFT canvas are.
		image = Image.open(filename)
		if image.size[0] > Buffer.size[0]:
			Buffer.paste(image.rotate(90))
		elif image.size[0] < Buffer.size[0]:
			Buffer.paste(image.rotate(-90))
		else:
			Buffer.paste(image)

	def backup_buffer(self):
		self.buffer2.paste(Buffer)

	def restore_buffer(self):
		Buffer.paste(self.buffer2)

	def invert(self, onoff):
		if onoff:
			self.command(ILI9341_INVON)
		else:
			self.command(ILI9341_INVOFF)

	def backlite(self, onoff):
		if self._led is not None:
			self._gpio.output(self._led, onoff)

	def image_to_data(self, image):
		"""Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
		# Source of this code: Adafruit ILI9341 python project
		pixels = image.convert('RGB').load()
		width, height = image.size
		for y in range(height):
			for x in range(width):
				r,g,b = pixels[(x,y)]
				color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
				yield (color >> 8) & 0xFF
				yield color & 0xFF


	def textdirect(self, pos, text, font, fill="white"):

		width, height = self.draw().textsize(text, font=font)
		# Create a new image with transparent background to store the text.
		textimage = Image.new('RGBA', (width, height), (255,255,255,0))
		# Render the text.
		textdraw = ImageDraw.Draw(textimage)
		textdraw.text((0,0), text, font=font, fill=fill)
		self.set_frame(pos[0], pos[1], pos[0]+width-1, pos[1]+height-1)
		# Convert image to array of 16bit 565 RGB data bytes.
		pixelbytes = list(self.image_to_data(textimage))
		# Write data to hardware.
		self.data(pixelbytes)

	def penOnHotspot(self, HSlist, pos):
		# HotSpot list of "hotspots" - of form   [(x0,y0,x1,y1,returnvalue)]*numOfSpots
		# if cursor position "pos" is within a hotspot box x0y0:x1y1, then "returnvalue" is returned
		x=pos[0]
		y=pos[1]
		for hs in HSlist:
			if x >= hs[0] and x<= hs[2] and y>= hs[1] and y<=hs[3]:
				return hs[4]
		return None

# CUSTOM FUNCTIONS FOR draw() IN LCD CANVAS SYSTEM

# We import these extra functions below as new custom methods of the PIL "draw" function:
# Hints on this custom method technique:
#     http://www.ianlewis.org/en/dynamically-adding-method-classes-or-class-instanc

def _textrotated(self, position, text, angle, font, fill="white"):
	# Define a function to create rotated text.
	# Source of this rotation coding: Adafruit ILI9341 python project
	# "Unfortunately PIL doesn't have good
	# native support for rotated fonts, but this function can be used to make a
	# text image and rotate it so it's easy to paste in the buffer."
	width, height = self.textsize(text, font=font)
	# Create a new image with transparent background to store the text.
	textimage = Image.new('RGBA', (width, height), (0,0,0,0))
	# Render the text.
	textdraw = ImageDraw.Draw(textimage)
	textdraw.text((0,0), text, font=font, fill=fill)
	# Rotate the text image.
	rotated = textimage.rotate(angle, expand=1)
	# Paste the text into the TFT canvas image, using text itself as a mask for transparency.
	Buffer.paste(rotated, position, rotated)  # into the global Buffer
	#   example:  draw.textrotated(position, text, angle, font, fill)

def _pasteimage(self, image, position):
	Buffer.paste(image, position)
	#Buffer.paste(Image.open(filename), position)
	# example: draw.pasteimage('bl.jpg', (30,80))

def _textwrapped(self, position, text1, length, height, font, fill="white"):
	text2=textwrap.wrap(text1, length)
	y=position[1]
	for t in text2:
		self.text((position[0],y), t, font=font, fill=fill)
		y += height
	# example:  draw.textwrapped((2,0), "but a lot longer", 50, 18, myFont, "black")

#        All colours may be any notation:
#        (255,0,0)  =red    (R, G, B)
#        0x0000FF   =red    BBGGRR
#        "#FF0000"  =red    RRGGBB
#        "red"      =red    html colour names, insensitive
