print("Unified Display Module loading")

# Serves as a transmission between the various display types and
# the different picorder front ends. Runs the display drawing as a process so
# it can be run concurrently.


import sys
import logging
from objects import *
from multiprocessing import Process,Queue,Pipe
import signal


if configure.display == 1:
	from luma.core.interface.serial import spi
	from luma.core.render import canvas
	from luma.lcd.device import st7735
	from luma.emulator.device import pygame
``
	# Raspberry Pi hardware SPI config:
	DC = 23
	RST = 24
	SPI_PORT = 0
	SPI_DEVICE = 0

	if not configure.pc:
		serial = spi(port = SPI_PORT, device = SPI_DEVICE, gpio_DC = DC, gpio_RST = RST)
		device = st7735(serial, width = 160, height = 128, mode = "RGB")
	else:
		# if the user has selected the emulated display we
		# load the display as a pygame window.
		device = pygame(width = 160, height = 128)
		emu_input = Pygame_Input()
		# we need something to handle input and send it back to the input handler.


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
	device.initLCD(DC, RST, LED)

# a function intended to be run as a process so as to offload the computation
# of the screen rendering from the GIL.
# takes "q" - a frame of data for the display (PIL imagedraw object)
def DisplayFunction(q):

	# an initiation bit for the process
	go = True

	# lib_tft24 screens require us to create a drawing surface for the screen
	# and add to it.
	if configure.display == 2:
		surface = device.draw()

	while go:

		payload = q.get()

		# add an event to handle shutdown.
		if payload == "quit":
			device.cleanup()
			go = False

		# the following is only for screens that use Luma.LCD
		if configure.display == 1:
			device.display(payload)

		# the following is only for TFT24T screens
		elif configure.display == 2:
			 # Resize the image and rotate it so it's 240x320 pixels.
			frame = payload.rotate(90,0,1).resize((240, 320))
			# Draw the image on the display hardware.
			surface.pasteimage(frame,(0,0))
			device.display()

# a class to control the connected display. It serves as a transmission between
# the main drawing program and the possible connected screen. A range of screens
# and libraries can be used in this way with small modifications to the base
# class.
class GenericDisplay(object):

	def __init__(self):
		self.q = Queue()
		self.display_process = Process(target=DisplayFunction, args=(self.q,))
		self.display_process.start()


	# Display takes a PILlow based drawobject and pushes it to screen.
	def display(self,frame):
		self.q.put(frame)
		emu_input.read()

	def cleanup(self):
		self.q.put("quit")


# A class to handle keyboard support when the emulation mode of luma.lcd is used (could also be useful in the future for other pygame displays)
# for now this works by default when emulation mode is used, it is probably best to disable the keyboard input option in config.ini

class Pygame_Input(object):

	def __init__(self):

		self.calibrate_timeout = 30
		self.timed = timer()
		# lists for hold behaviour tracking
		self.holding = []
		self.holdtimers = []
		# holding timer interval
		self.thresh_hold = 1.500

		# list stores each inputs previous state for comparison with now.
		self.pressed = []

		# a fresh eventlist to initialize.
		self.clear = []

		# this list stores the final state of all buttons to allow the program to check for multiple button presses for hidden features
		self.buttonlist = []
		self.door_was_open = False
		self.door_was_closed = False

		# seeds each list with a spot for each input
		for i in range(buttons):
			self.pressed.append(False)
			self.buttonlist.append(False)
			self.holding.append(False)
			self.clear.append(False)

			thistimer = timer()
			self.holdtimers.append(thistimer)

		configure.eventlist[0] = self.clear

	def getlist(self):
		pass

	def read(self):

		if configure.input_kb:

			key = self.keypress()

			# key was pressed
			if configure.eventready[0] == False:
				if key[pygame.K_LEFT]:
						if not self.pressed[0]:
							self.pressed[0] = True
							configure.eventready[0] = True
							self.holdtimers[0].logtime()
						else:
							if self.holdtimers[0].timelapsed() > self.thresh_hold:
								self.holding[0] = True

				if not key[pygame.K_LEFT]:
					self.holding[0] = False
					if self.pressed[0]:
						self.buttonlist[0] = True
						self.pressed[0] = False
					else:
						self.buttonlist[0] = False


				if key[pygame.K_DOWN]:
						if not self.pressed[1]:
							self.pressed[1] = True
							configure.eventready[0] = True
							self.holdtimers[1].logtime()
						else:

							if self.holdtimers[1].timelapsed() > self.thresh_hold:
								self.holding[1] = True

				if not key[pygame.K_DOWN]:
					self.holding[1] = False
					if self.pressed[1]:
						self.buttonlist[1] = True
						self.pressed[1] = False
					else:
						self.buttonlist[1] = False


				if key[pygame.K_RIGHT]:
						if not self.pressed[2]:
							self.pressed[2] = True
							configure.eventready[0] = True
							self.holdtimers[2].logtime()
						else:

							if self.holdtimers[2].timelapsed() > self.thresh_hold:
								self.holding[2] = True

				if not key[pygame.K_RIGHT]:
					self.holding[2] = False
					if self.pressed[2]:
						self.buttonlist[2] = True
						self.pressed[2] = False
					else:
						self.buttonlist[2] = False

		configure.eventlist[0] = self.pressed