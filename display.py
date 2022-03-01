print("Unified Display Module loading")
import sys
import logging
from objects import *

if configure.display == 1:
	from luma.core.interface.serial import spi
	from luma.core.render import canvas
	from luma.lcd.device import st7735
	from luma.emulator.device import pygame

	# Raspberry Pi hardware SPI config:
	DC = 23
	RST = 24
	SPI_PORT = 0
	SPI_DEVICE = 0

	if not configure.pc:
		serial = spi(port = SPI_PORT, device = SPI_DEVICE, gpio_DC = DC, gpio_RST = RST)
		device = st7735(serial, width = 160, height = 128, mode = "RGB")
	else:
		device = pygame(width = 160, height = 128)

# for TFT24T screens
elif configure.display == 2:
	# Details pulled from https://github.com/BehindTheSciences/ili9341_SPI_TouchScreen_LCD_Raspberry-Pi/blob/master/BTS-ili9341-touch-calibration.py
	from lib_tft24T import TFT24T
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	import spidev
	DC = 24
	RST = 25
	LED = 15
	PEN = 26
	device = TFT24T(spidev.SpiDev(), GPIO)
	# Initialize display and touch.
	TFT.initLCD(DC, RST, LED)

class GenericDisplay(object):

	def __init__(self):

		# lib_tft24 screens require us to create a drawing surface for the screen
		# and add to it.
		if configure.display == 2:
			self.surface = device.draw()


	# Display takes a PILlow based drawobject and pushes it to screen.
	def display(self,frame):

		# the following is only for screens that use Luma.LCD
		if configure.display == 1:
			device.display(frame)

		# the following is only for TFT24T screens
		elif configure.display == 2:
			 # Resize the image and rotate it so it's 240x320 pixels.
			frame = frame.rotate(90,0,1).resize((240, 320))
			# Draw the image on the display hardware.
			self.surface.pasteimage(frame,(0,0))
			device.display()
