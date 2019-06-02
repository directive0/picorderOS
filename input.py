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


if configure.input_kb:
	import pygame

if configure.input_gpio:
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
		self.buttonlist = []
		self.down = []
		for i in range(buttons):
			self.fired.append(False)
			self.buttonlist.append(False)
			self.down.append(True)

		self.awaspressed = False
		self.bwaspressed = False
		self.cwaspressed = False
		self.afire = False
		self.bfire = False
		self.cfire = False

	def is_down(self, i):
		if self.down[i]:
			self.down[i] = False
			return True
		else:
			return False

	def read(self):

		if configure.input_kb:
			# the following button inputs allow the test program to run on PC and be interactive.
			key = self.keypress()
			#print(key)

			if key[pygame.K_LEFT] and not self.awaspressed:
					self.buttonlist[0] = True
					#configure.auto = not configure.auto
					self.awaspressed = True

			if not key[pygame.K_LEFT] and self.awaspressed:
					self.awaspressed = False
					self.buttonlist[0] = False
					self.down[0] = True

			if key[pygame.K_DOWN] and not self.bwaspressed:
					self.buttonlist[1] = True
					self.bwaspressed = True

			if not key[pygame.K_DOWN] and self.bwaspressed:
					self.bwaspressed = False
					self.buttonlist[1] = False
					self.down[1] = True

			if key[pygame.K_RIGHT] and not self.cwaspressed:
					self.buttonlist[2] = True
					self.cwaspressed = True

			if not key[pygame.K_RIGHT] and self.cwaspressed:
					self.cwaspressed = False
					self.buttonlist[2] = False
					self.down[2] = True

			#print("buttonlist: ", self.buttonlist)
			return self.buttonlist


		if configure.input_gpio:
			for i in range(3):
				if (not self.fired[i]) and (not GPIO.input(pins[i])):  # Fire button pressed
					self.fired[i] = True
					#print("Button ", i, " registered!")
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
