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


# if tr108 set up pins for buttons
if configure.tr108:
	pins = [5,6,13]

if configure.tr109:

	# by default the tr-109 uses gpio for hinge close
	import RPi.GPIO as GPIO

	# hallpin 1 was disabled as sensor board rev 2 accidentaly used it to drive
	hallpin1 = configure.HALLPIN1
	hallpin2 = configure.HALLPIN2
	alertpin = configure.ALERTPIN

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(hallpin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(hallpin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

import time

# set up requirements for USB keyboard
if configure.input_kb:
	import pygame

# set up requirements for GPIO based inputs
if configure.input_gpio:

	# setup for ugeek test rig.
	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)

	if configure.tr108:
		# setup our 3 control buttons
		GPIO.setup(pins[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(pins[1], GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(pins[2], GPIO.IN, pull_up_down=GPIO.PUD_UP)

	if configure.tr109:
		# setup our 3 control buttons


		GPIO.setup(pins[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(pins[1], GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(pins[2], GPIO.IN, pull_up_down=GPIO.PUD_UP)
	# To add:
	# GPIO Battery Low
	# GPIO Hall 1
	# GPIO Hall 2



# set up requirements for capacitive buttons using an mpr121
if configure.input_cap_mpr121:
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

if configure.input_cap1208:
	# setup for ugeek test rig.
	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)

	interrupt_pin = 0
	GPIO.setup(interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(interrupt_pin, GPIO.BOTH)


	import cap1xxx
	cap1208 = cap1xxx.Cap1208(alert_pin = 0)
	cap1208._write_byte(0x1F, configure.CAPSENSITIVITY)



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

		if GPIO.input(hallpin1) == 1:
			configure.dr_open[0] = True
		else:
			configure.dr_open[0] = False

		if configure.input_cap1208:

			#checks to see if alert pin is high

				#if high return the event list of currently released buttons

			reading = cap1208.get_input_status()

			if reading == "release" or reading == "press":
				cap1208.clear_interrupt()


		return reading

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

		if configure.input_gpio:

			for i in range(3):

				# if the button has not been registered as pressed
				if GPIO.input(pins[i]) == 0:  # button pressed
					if not self.waspressed[i]:
						self.waspressed[i] = True


				if GPIO.input(pins[i]) == 1:

					if self.waspressed[i]:
						self.buttonlist[i] = True
						self.waspressed[i] = False
					else:
						self.buttonlist[i] = False


		if configure.input_cap_mpr121:
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




	def keypress(self):
		pygame.event.get()
		#pygame.time.wait(50)
		key = pygame.key.get_pressed()

		return key




# Some functions to test the various inputs. Call them in a while loop from the repl to test.


def halltest():

	if GPIO.input(hallpin1) == 1:
		print("hallpin1 open")
	else:
		print("hallpin1 closed")


	if GPIO.input(hallpin2) == 1:
		print("hallpin2 open")
	else:
		print("hallpin2 closed")




def captest():

	if GPIO.input(configure.ALERTPIN) == 1:
		print("ALERT HIGH")
	else:
		print("ALERT LOW")

	# If the alert pin is raised
	if cap1208._interrupt_status():

		# check each item in the event lists
		channels = cap1208.get_input_status()

		for i in range(len(channels)):

			# if the item has been pressed show us what channel it is
			if channels[i] == "press":
				print(i)

		cap1208.clear_interrupt()


def testall():
	inputs = Inputs()

	while True:

		if GPIO.input(configure.ALERTPIN) == 1:
			pass
		else:
			print("ALERT LOW<<<<<<<<<<<<<<<<")
			print(inputs.read())
			cap1208.clear_interrupt()

		#halltest()
