#!/usr/bin/python
print("Loading Unified Indicator Module")
# Provides a surface for control over the LEDs connected via GPIO. For the tr-tr108
# LEDs are controlled directly from GPIO, for the tr109 a shift register is used

from objects import *
import time
import math

#loads parameters for configurations
interval = configure.LED_TIMER
timer = timer()



# External module import
if not configure.pc:
	import RPi.GPIO as GPIO

if configure.sensehat:
	# instantiates and defines paramaters for the sensehat

	from sense_hat import SenseHat

	# instantiate a sensehat object,
	sensehat = SenseHat()

	# Initially clears the LEDs once loaded
	sensehat.clear()

	# Prepares an array of 64 pixel triplets for the Sensehat moire display
	moire=[[0 for x in range(3)] for x in range(64)]


# a list of the shift register pin data, for loop purposes (main board, sensor board).
# Pulls the pin assignments from the objects.py configuration object.
PINS = [[configure.PIN_DATA,configure.PIN_LATCH,configure.PIN_CLOCK],[configure.PIN_DATA2,configure.PIN_LATCH2,configure.PIN_CLOCK2]]

# set the mode of the shift register pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(configure.PIN_DATA, GPIO.OUT)
GPIO.setup(configure.PIN_LATCH, GPIO.OUT)
GPIO.setup(configure.PIN_CLOCK, GPIO.OUT)
GPIO.setup(configure.PIN_DATA2, GPIO.OUT)
GPIO.setup(configure.PIN_LATCH2, GPIO.OUT)
GPIO.setup(configure.PIN_CLOCK2, GPIO.OUT)

# loads the pin configurations and modes for the tr-108  (3 leds)
if configure.tr108:

	led1 = 4
	led2 = 17
	led3 = 27

	GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
	GPIO.setup(led1, GPIO.OUT) # LED pin set as output
	GPIO.setup(led2, GPIO.OUT) # LED pin set as output
	GPIO.setup(led3, GPIO.OUT) # LED pin set as output

# loads the pin configurations and modes for the tr-109 (shift register based)
if configure.tr109:
	# Pin Definitons:
	led1 = 16 #19 # Broadcom pin 19
	led2 = 20 #6 # Broadcom pin 13
	led3 = 6 #20
	led4 = 19 #16
	sc_led = 15

	# Pin Setup:
	# Set broadcom pin mode
	GPIO.setmode(GPIO.BCM)

	# Assign the
	GPIO.setup(configure.PIN_DATA, GPIO.OUT)
	GPIO.setup(configure.PIN_LATCH, GPIO.OUT)
	GPIO.setup(configure.PIN_CLOCK, GPIO.OUT)

	GPIO.setup(configure.PIN_DATA2, GPIO.OUT)
	GPIO.setup(configure.PIN_LATCH2, GPIO.OUT)
	GPIO.setup(configure.PIN_CLOCK2, GPIO.OUT)

	GPIO.setup(sc_led, GPIO.OUT)


# delivers data to the shift register
# can use alternate set of shift pins using the "board" argument
def shiftout(byte,board = 0):

		# brings the latch low
        GPIO.output(PINS[board][1], 0)

        for x in range(8):
                # Assigns logic to the pin based on the bit x
                GPIO.output(PINS[board][0], (byte >> x) & 1)

                # toggle the clock, first set the pin because it fails if I don't
                GPIO.setup(PINS[board][2], GPIO.OUT)
                GPIO.output(PINS[board][2], 1)
                GPIO.output(PINS[board][2], 0)

        GPIO.output(PINS[board][1], 1)




# a function to clear the gpio
def cleangpio():
	resetleds()
	GPIO.cleanup() # cleanup all GPIO

# a function to clear the LEDs
def resetleds():

	if configure.tr109:
		shiftout(0)
		shiftout(0, board = 1)

	if configure.tr108:
		GPIO.output(led1, GPIO.LOW)
		GPIO.output(led2, GPIO.LOW)
		GPIO.output(led3, GPIO.LOW)




# # The following set of functions are for activating each LED individually.
# # I figured it was easier than having different functions for different combinations.
# # This way you can just manually set them as you please.
def screen_on():
	if configure.tr109:
		if configure.display == 1:
			GPIO.output(sc_led, GPIO.HIGH)

def leda_on():
	GPIO.output(led1, GPIO.HIGH)

def ledb_on():
	GPIO.output(led2, GPIO.HIGH)

def ledc_on():
	GPIO.output(led3, GPIO.HIGH)

def ledd_on():
	GPIO.output(led4, GPIO.HIGH)

def leda_off():
	GPIO.output(led1, GPIO.LOW)

def ledb_off():
	GPIO.output(led2, GPIO.LOW)

def ledc_off():
	GPIO.output(led3, GPIO.LOW)

def ledd_off():
	GPIO.output(led4, GPIO.LOW)
#
def screen_off():
	if configure.tr109:
		GPIO.output(sc_led, GPIO.LOW)


# The following class drives the ABGD ripple animation for the tr-109.
class ripple(object):

	def __init__(self):
		self.beat = 0
		self.disabled = False
		self.statuswas = False
		self.lights = True
		self.ticks = 0


	def cycle(self):

		# because the tr-109 uses a shift register to drive its indicator LEDs
		# each frame of LED animations is represented by a byte, with the LEDs
		# being arranged as follows:

		#	0		0		0		0		0		0		0		0
		#	a		b		d		g		pwr		a1		b1		d1

		# the basic ripple animation is as follows.
		#140
		#74
		#41
		#26

		# if sleep detection is active:
		if configure.sleep[0]:
			#check if the door is open.
			if configure.dr_open[0]:
				# if it wasn't open last time.
				if self.statuswas != configure.dr_open[0]:
					# turn on our screen
					screen_on()
				# engage the lights
				self.lights = True
				self.statuswas = configure.dr_open[0]
			else:
				screen_off()
				self.lights = False
				self.statuswas = configure.dr_open[0]
		else:
			screen_on()


		# if lights are engaged this block of code will run the animation, or else
		# turn them off.
		if self.lights and configure.leds[0]:

			if configure.tr109:
				if self.beat > 3:
					self.beat = 0

				if self.beat == 0:
					shiftout(140)
					shiftout(140,board = 1)

				if self.beat == 1:
					shiftout(74)
					shiftout(74,board = 1)

				if self.beat == 2:
					shiftout(41)
					shiftout(41, board = 1)

				if self.beat == 3:
					shiftout(26)
					shiftout(26, board = 1)

				self.beat += 1

		else:
			if configure.tr109:
				shiftout(0)
				shiftout(0,board =1)


		if configure.sensehat and configure.moire[0]:
			cxtick = 0.5 * math.sin(self.ticks/15.0) # change this line
			cytick = 0.5 * math.cos(self.ticks/8.0) #change this line

			for x in range(8):
					for y in range(8):
							# it's this cool plasma effect from demoscene I stole from
							# somewhere.
							cx = x + cxtick #change this line
							cy = y + cytick #change this line
							v = math.sin(math.sqrt(1.0*(math.pow(cy, 2.0)+math.pow(cx, 2.0))+1.0)+self.ticks)
							v = (v + 1.0)/2.0
							v = int(v*255.0)


							# Pack the computed pixel into the moire pixel list
							moire[(x*8)+y]=[v,v,v]

			sensehat.set_pixels(moire)
			self.ticks += 1



# function to handle lights as a seperate thread.
def ripple_async():

	thread_rip = ripple()

	while not configure.status[0] == "quit":

		if timer.timelapsed() > interval:
			thread_rip.cycle()
			timer.logtime()

	# start the ripple routine
	# have a state variables
	# received commands asynchronously "start" "stop"
	# quit when asked.
