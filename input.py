\
print("Loading Unified Input Module")
# This script retrieves and packages all input events that might be useful to the program
# The input object checks the configuration object and returns an array of button inputs.


# This script needs to be able to accept 3 different kinds of inputs
	# 1) inputs handed directly from the RPI gpio
	# 2) inputs handed from pygame event checkers
	# 3) inputs handed from the capacitive touch device on i2c

# array needs:

# geo, met and bio are going to be standard across all trics.


from objects import *

# array holds the pins for each hard coded button on the tric
# The TR-108 only has 3 buttons

# Max number of buttons
#	0	1	 2  	3  	4	5	6		7				8			9		10			11	  12	13	14
# geo, met, bio, pwr, f1/f2, I, E, accpt/pool, intrship/tricrder, EMRG, fwd/input, rvs/erase, Ib, Eb, ID

# stores the number of buttons to be queried
buttons = 15

threshold = 3
release_threshold = 2


# if tr108 set up pins
if configure.tr108:
	pins = [5,6,13]


import time

# set up requirements for USB keyboard
if configure.input_kb:
	import pygame

# set up requirements for GPIO based inputs
if configure.input_gpio:
	# setup for ugeek test rig.
	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)
	# Up, Down, left, right, fire

	GPIO.setup(pins[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)  #X Button for GPIO5
	GPIO.setup(pins[1], GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Trigon Button for GPIO24
	GPIO.setup(pins[2], GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Square Button for GPIO22

# set up requirements for capacitive buttons using an mpr121
if configure.input_cap:
	# if using the capacitive touch board from adafruit we import that library
	import adafruit_mpr121
	import busio
	import board

	# Create I2C bus.
	i2c = busio.I2C(board.SCL, board.SDA)

	# Create MPR121 object. Address can be 5A or 5B (proto uses 5A)
	mpr121 = adafruit_mpr121.MPR121(i2c, address = 0x5A)

	for i in range(3):
		test = adafruit_mpr121.MPR121_Channel(mpr121,i)
		test.threshold = threshold
		test.release_threshold = release_threshold
# the input class handles all the requirements for handling user directed inputs
class Inputs(object):

	def __init__(self):

		# # create some status variables for debounce.
		self.eventlist = []

		# fired stores immidiate state of button (if its pressed or not)
		self.fired = []

		# down stores the first moment of activation, for instances where falling edge detection is required
		self.down = []

		# up stores the return to being not pressed
		self.up = []

		self.holding = []
		self.holdstarted = []
		self.holdtimers = []
		self.thresh_hold = 1.500

		# waspressed stores information about previous state
		self.waspressed = []

		# this list stores the final state of all buttons to allow the program to check for multiple button presses for hidden features
		self.buttonlist = []

		# prepares these lists for the script
		for i in range(buttons):
			self.fired.append(False)
			self.buttonlist.append(False)
			self.down.append(False)
			self.up.append(True)
			self.waspressed.append(False)
			self.holding.append(False)
			self.holdstarted.append(0)
			thistimer = timer()
			self.holdtimers.append(thistimer)
			self.eventlist.append(True)

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

	def is_up(self, i):
		if not self.down[i]:
			return True
		else:
			return False

	def getlist(self):
		pass

	def read(self):
		if configure.input_kb:

			key = self.keypress()

			# key was pressed

			if key[pygame.K_LEFT]:
					if not self.waspressed[0]:
						self.waspressed[0] = True
						self.holdtimers[0].logtime()
					else:

						if self.holdtimers[0].timelapsed() > self.thresh_hold:
							self.holding[0] = True

			if not key[pygame.K_LEFT]:
				self.holding[0] = False
				if self.waspressed[0]:
					self.buttonlist[0] = True
					self.waspressed[0] = False
				else:
					self.buttonlist[0] = False


			if key[pygame.K_DOWN]:
					if not self.waspressed[1]:
						self.waspressed[1] = True
						self.holdtimers[1].logtime()
					else:

						if self.holdtimers[1].timelapsed() > self.thresh_hold:
							self.holding[1] = True

			if not key[pygame.K_DOWN]:
				self.holding[1] = False
				if self.waspressed[1]:
					self.buttonlist[1] = True
					self.waspressed[1] = False
				else:
					self.buttonlist[1] = False


			if key[pygame.K_RIGHT]:
					if not self.waspressed[2]:
						self.waspressed[2] = True
						self.holdtimers[2].logtime()
					else:

						if self.holdtimers[2].timelapsed() > self.thresh_hold:
							self.holding[2] = True

			if not key[pygame.K_RIGHT]:
				self.holding[2] = False
				if self.waspressed[2]:
					self.buttonlist[2] = True
					self.waspressed[2] = False
				else:
					self.buttonlist[2] = False
			#
			# if key[pygame.K_DOWN] and not self.bwaspressed:
			# 		self.buttonlist[1] = True
			# 		self.bwaspressed = True
			#
			# if not key[pygame.K_DOWN] and self.bwaspressed:
			# 		self.bwaspressed = False
			# 		self.buttonlist[1] = False
			# 		self.down[1] = True
			#
			# if key[pygame.K_RIGHT] and not self.cwaspressed:
			# 		self.buttonlist[2] = True
			# 		self.cwaspressed = True
			#
			# if not key[pygame.K_RIGHT] and self.cwaspressed:
			# 		self.cwaspressed = False
			# 		self.buttonlist[2] = False
			# 		self.down[2] = True

		if configure.input_gpio:
			# for i in range(3):
			# 	if (not self.fired[i]) and (not GPIO.input(pins[i])):  # Fire button pressed
			# 		self.fired[i] = True
			# 		#print("Button ", i, " registered!")
			# 		self.buttonlist[i] = True
			# 	#device.emit(uinput.KEY_LEFTCTRL, 1) # Press Left Ctrl key
			# 	if self.fired[i] and GPIO.input(pins[i]):  # Fire button released
			# 		self.fired[i] = False
			# 		self.buttonlist[i] = False
			# 		self.down[i] = True
			for i in range(3):
				print("i =", i, " ", GPIO.input(pins[i]))
				# if the button has not been registered as pressed
				if GPIO.input(pins[i]):  # button pressed
					if not self.waspressed[i]:
						self.waspressed[i] = True
						self.holdtimers[i].logtime()
					else:

						if self.holdtimers[i].timelapsed() > self.thresh_hold:
							self.holding[i] = True

				if not GPIO.input(pins[i]):
					self.holding[i] = False
					if self.waspressed[i]:
						self.buttonlist[i] = True
						self.waspressed[i] = False
					else:
						self.buttonlist[i] = False



		if configure.input_cap:
			# Reads the touched capacitive elements
			touched = mpr121.touched_pins

			# runs a loop to check each possible button
			for i in range(len(touched)):
				# if the button has not been registered as pressed
				if touched[i]:  # button pressed
					if not self.waspressed[i]:
						self.waspressed[i] = True
						self.holdtimers[i].logtime()
					else:

						if self.holdtimers[i].timelapsed() > self.thresh_hold:
							self.holding[i] = True

				if not touched[i]:
					self.holding[i] = False
					if self.waspressed[i]:
						self.buttonlist[i] = True
						self.waspressed[i] = False
					else:
						self.buttonlist[i] = False


		#print(self.buttonlist)
		return self.buttonlist


	def keypress(self):
		pygame.event.get()
		#pygame.time.wait(50)
		key = pygame.key.get_pressed()

		return key
