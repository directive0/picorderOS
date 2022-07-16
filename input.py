print("Loading Unified Input Module")
# This script retrieves and packages all input events that might be useful to the program
# The input object checks the configuration object and returns an array of button inputs.


# This script needs to be able to accept 3 different kinds of inputs
	# 1) inputs handed directly from the RPI gpio
	# 2) inputs handed from pygame event checkers
	# 3) inputs handed from the capacitive touch device on i2c

# array needs:

# geo, met and bio are going to be standard across all trics.


# array holds the pins for each hard coded button on the tric
# The TR-108 only has 3 buttons

# Max number of buttons
#	0	1	 2  	3  	4	5	6		7				8			9		10			11	  12	13	14
# geo, met, bio, pwr, f1/f2, I, E, accpt/pool, intrship/tricrder, EMRG, fwd/input, rvs/erase, Ib, Eb, ID


import time
from objects import *


# stores the number of buttons to be queried
buttons = 16

threshold = 3
release_threshold = 2


# if tr108 set up pins for gpio buttons
if configure.tr108:
	pins = [5,6,13]

# tr109 by default uses cap1208. This will require modifying for other inputs
if configure.tr109:

	import RPi.GPIO as GPIO


	hallpin1 = configure.HALLPIN1
	hallpin2 = configure.HALLPIN2


	alertpin = configure.ALERTPIN

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(hallpin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(hallpin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if configure.sensehat:
	if configure.input_joystick:
		from sense_hat import SenseHat
		sense = SenseHat()

# set up requirements for USB keyboard
if configure.input_kb:
	import pygame
	pygame.init()

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


# set up requirements for capacitive buttons using an mpr121
if configure.input_cap_mpr121:
	# if using the capacitive touch board from adafruit we import that library
	import adafruit_mpr121
	import busio

	# initiate I2C bus.
	i2c = busio.I2C(configure.PIN_SCL, configure.PIN_SDA)

	# Create MPR121 object. Address can be 5A or 5B (proto uses 5A)
	mpr121 = adafruit_mpr121.MPR121(i2c, address = 0x5A)

	# initializes each input
	for i in range(3):
		test = adafruit_mpr121.MPR121_Channel(mpr121,i)
		test.threshold = threshold
		test.release_threshold = release_threshold

if configure.input_cap1208:


	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)


	GPIO.setup(configure.ALERTPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(configure.ALERTPIN, GPIO.BOTH)


	import cap1xxx
	cap1208 = cap1xxx.Cap1208(alert_pin = 0)
	cap1208._write_byte(0x1F, configure.CAPSENSITIVITY)

if configure.input_pcf8575:
	from pcf8575 import PCF8575
	i2c_port_num = 1
	pcf_address = 0x20
	pcf = PCF8575(i2c_port_num, pcf_address)

	button_table = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,0,3,2,4]

# the input class receives and relays control events for user interaction
class Inputs(object):

	def __init__(self):


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

		# looks for door open/close.
		if configure.tr109 and configure.dr[0]:
			# top hall sensor, 1 = door open
			if GPIO.input(hallpin1) == 1:
				if self.door_was_closed == True:
					self.door_was_closed = False
					configure.dr_opening[0] = True

				configure.dr_open[0] = True
			else:
				self.door_was_closed = True
				configure.dr_open[0] = False

			# lower hall, 0 = door open
			if GPIO.input(hallpin2) == 1:
				if self.door_was_open == True:
					self.door_was_open = False
					configure.dr_closing[0] = True
			else:
				self.door_was_open = True

		if configure.input_cap1208:

			# if the alert pin is brought LOW
			if GPIO.input(configure.ALERTPIN) == 0 and configure.eventready[0] == False:

				#print("touch received")

				# collect the event list from the chip
				reading = cap1208.get_input_status()

				# for each item in that event list
				for iteration, input in enumerate(reading):

					# if an item is pressed
					if input == "press":
						# mark it in the pressed list
						self.pressed[iteration] = True
						# raise the eventready flag
						configure.eventready[0] = True
						# raise the sound effect flag
						configure.beep_ready[0] = True
					else:
						# if an item is marked "released"
						if input == "release":
							# if it was previously marked pressed
							if self.pressed[iteration] == True:
								# ignore it
								self.pressed[iteration] = False
							else:
								# if it wasn't marked pressed last time (was missed)
								configure.eventready[0] = True
								self.pressed[iteration] = True
								configure.beep_ready[0] = True
						# else mark it not pressed
						else:
							self.pressed[iteration] = False



				#clear Alert pin
				cap1208.clear_interrupt()

				configure.eventlist[0] = self.pressed

				# return the pressed data
				return self.pressed

			else:
				# otherwise just return a line of negatives.
				return self.clear

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

		if configure.input_gpio:

			for i in range(3):

				# if the button has not been registered as pressed
				if GPIO.input(pins[i]) == 0:  # button pressed
					if not self.pressed[i]:
						self.pressed[i] = True
						configure.eventlist[0] = True


				if GPIO.input(pins[i]) == 1:

					if self.pressed[i]:
						self.buttonlist[i] = True
						self.pressed[i] = False
					else:
						self.buttonlist[i] = False

		if configure.sensehat and configure.input_joystick:

			if configure.eventready[0] == False:

				for event in sense.stick.get_events():

					if (event.direction == 'left' and event.action == 'pressed'):
						if not self.pressed[0]:
							self.pressed[0] = True
							configure.eventready[0] = True
							self.holdtimers[0].logtime()
						else:
							if self.holdtimers[0].timelapsed() > self.thresh_hold:
								self.holding[0] = True

					if (event.direction == 'left' and event.action == 'released'):
						self.holding[0] = False
						if self.pressed[0]:
							self.buttonlist[0] = True
							self.pressed[0] = False
						else:
							self.buttonlist[0] = False

					if (event.direction == 'down' and event.action == 'pressed'):
						if not self.pressed[1]:
							self.pressed[1] = True
							configure.eventready[0] = True
							self.holdtimers[1].logtime()
						else:
							if self.holdtimers[1].timelapsed() > self.thresh_hold:
								self.holding[1] = True

					if (event.direction == 'down' and event.action == 'released'):
						self.holding[1] = False
						if self.pressed[1]:
							self.buttonlist[1] = True
							self.pressed[1] = False
						else:
							self.buttonlist[1] = False

					if (event.direction == 'right' and event.action == 'pressed'):
						if not self.pressed[2]:
							self.pressed[2] = True
							configure.eventready[0] = True
							self.holdtimers[2].logtime()
						else:
							if self.holdtimers[2].timelapsed() > self.thresh_hold:
								self.holding[2] = True

					if (event.direction == 'right' and event.action == 'released'):
						self.holding[2] = False
						if self.pressed[2]:
							self.buttonlist[2] = True
							self.pressed[2] = False
						else:
							self.buttonlist[2] = False

		if configure.input_cap_mpr121:
			# Reads the touched capacitive elements
			touched = mpr121.touched_pins

			# runs a loop to check each possible button
			for i in range(len(touched)):

				# if the button has not been registered as pressed
				if touched[i]:  # button pressed
					if not self.pressed[i]:
						self.pressed[i] = True
						self.holdtimers[i].logtime()
					else:

						if self.holdtimers[i].timelapsed() > self.thresh_hold:
							self.holding[i] = True

				if not touched[i]:
					self.holding[i] = False
					if self.pressed[i]:
						self.buttonlist[i] = True
						self.pressed[i] = False
					else:
						self.buttonlist[i] = False

		if configure.input_pcf8575:

			if not configure.eventready[0]:
				this_frame = list(pcf.port)

				for this, button in enumerate(this_frame):

					# if an item is pressed
					if not button:

						#if it wasn't pressed last time
						if not self.pressed[this]:

							# mark it in the pressed list
							print("pad press registered at ", this)
							print("raising an event at address ", button_table[this])

							self.pressed[button_table[this]] = True
							configure.eventready[0] = True
							configure.beep_ready[0] = True
					else:
						self.pressed[button_table[this]] = False

		configure.eventlist[0] = self.pressed


	def keypress(self):
		pygame.event.get()
		#pygame.time.wait(50)
		key = pygame.key.get_pressed()

		return key



def threaded_input():


	timed = timer()
	input = Inputs()
	timeit = timer()

	while not configure.status == "quit":

		if configure.samplerate[0] < timed.timelapsed():
			input.read()
