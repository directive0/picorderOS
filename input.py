# This script retrieves and packages all input events that might be useful to the program
# The input object checks the configuration object and returns an array of button inputs.


# This script needs to be able to accept 3 different kinds of inputs
	# 1) inputs handed directly from the RPI gpio
	# 2) inputs handed from pygame event checkers
	# 3) inputs handed from the capacitive touch device on i2c

# array needs:

#	0	1	 2  	3  	4	5	6		7				8			9		10			11	  12	13	14
# geo, met, bio, pwr, f1/f2, I, E, accpt/pool, intrship/tricrder, EMRG, fwd/input, rvs/erase, Ib, Eb, ID

# geo, met and bio are going to be standard across all trics.

# array holds the pin#s for each hard coded button on the tric

#ugeek setup
pins = [5,24,22]

# number of buttons
buttons = 15

from objects import *

import time


if configure.pc:
	import pygame
else:

	# setup for ugeek test rig.
	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)
	# Up, Down, left, right, fire

	GPIO.setup(pins[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)  #X Button for GPIO5
	GPIO.setup(pins[1], GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Trigon Button for GPIO24
	GPIO.setup(pins[2], GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Square Button for GPIO22


class Inputs(object):

	def __init__(self):

		# # create some status variables for debounce.
		self.fired = []
		for i in range(buttons):
			self.fired.append(False)

		self.buttonlist = []
		for i in range(buttons):
			self.buttonlist.append(False)

		self.awaspressed = False
		self.bwaspressed = False
		self.cwaspressed = False
		self.afire = False
		self.bfire = False
		self.cfire = False
		# self.pwr = False
		# self.f1_f2 = False
		# self.I = False
		# self.E = False
		# self.geo = False
		# self.met = False
		# self.bio = False
		# self.accpt_pool = False
		# self.intrship = False
		# self.EMRG = False
		# self.fwd = False
		# self.rvs = False
		# self.Ib = False
		# self.Eb = False
		# self.ID = False

	def read(self):

		if configure.pc:

			# the following button inputs allow the test program to run on PC and be interactive.
			key = self.keypress()
			#print(key)

			if key[pygame.K_LEFT]:
				if not self.awaspressed:
					self.buttonlist[0] = True
					configure.auto = not configure.auto
					print(configure.auto)
					self.awaspressed = True

			if self.awaspressed:
				if not key[pygame.K_LEFT]:
					self.awaspressed = False
					self.buttonlist[0] = False

			if key[pygame.K_DOWN]:
				if not self.bwaspressed:
					self.buttonlist[1] = True
					self.bwaspressed = True

			if self.bwaspressed:
				if not key[pygame.K_DOWN]:
					self.bwaspressed = False
					self.buttonlist[1] = False

			if key[pygame.K_RIGHT]:
				if not self.cwaspressed:
					self.buttonlist[2] = True
					self.cwaspressed = True

			if self.cwaspressed:
				if not key[pygame.K_RIGHT]:
					self.cwaspressed = False
					self.buttonlist[2] = False


			print("buttonlist: ", self.buttonlist)
			return self.buttonlist
		else:
			for i in range(3):
				if (not self.fired[i]) and (not GPIO.input(pins[i])):  # Fire button pressed
					self.fired[i] = True
					print("Button ", i, " registered!")
					self.buttonlist[i] = True
				#device.emit(uinput.KEY_LEFTCTRL, 1) # Press Left Ctrl key
				if self.fired[i] and GPIO.input(pins[i]):  # Fire button released
					self.fired[i] = False
					self.buttonlist[i] = False
				#device.emit(uinput.KEY_LEFTCTRL, 0) # Release Left Ctrl key

	def keypress(self):
		pygame.event.get()
		#pygame.time.wait(50)
		key = pygame.key.get_pressed()

		return key
