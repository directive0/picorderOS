#!/usr/bin/python
print("Loading Unified Indicator Module")
# new Changes
# will need to support a reed switch and more inputs.

from objects import *

# External module import
if not configure.pc:
	import RPi.GPIO as GPIO




PIN_DATA  = 16
PIN_LATCH = 20
PIN_CLOCK = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_DATA,  GPIO.OUT)
GPIO.setup(PIN_LATCH, GPIO.OUT)
GPIO.setup(PIN_CLOCK, GPIO.OUT)


if configure.neopixel:
#	import board
#	import neopixel
	pwr = 0
	alpha = 1
	beta = 2
	delta = 3
	gamma = 4

# delivers data to the shift register
def shiftout(byte):
	GPIO.output(PIN_LATCH, 0)
	for x in range(8):
		GPIO.output(PIN_DATA, (byte >> x) & 1)
		GPIO.output(PIN_CLOCK, 1)
		GPIO.output(PIN_CLOCK, 0)
	GPIO.output(PIN_LATCH, 1)

# loads the pin configurations and modes for the tr-108  (3 leds)
if configure.tr108:

	led1 = 4
	led2 = 17
	led3 = 27

	GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
	GPIO.setup(led1, GPIO.OUT) # LED pin set as output
	GPIO.setup(led2, GPIO.OUT) # LED pin set as output
	GPIO.setup(led3, GPIO.OUT) # LED pin set as output

# loads the pin configurations and modes for the tr-109 (many switches)
if configure.tr109:
# Pin Definitons:
	led1 = 16 #19 # Broadcom pin 19
	led2 = 20 #6 # Broadcom pin 13
	led3 = 6 #20
	led4 = 19 #16
	sc_led = 15

	# Pin Setup:
	GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
	GPIO.setup(led1, GPIO.OUT) # LED pin set as output
	GPIO.setup(led2, GPIO.OUT) # LED pin set as output
	GPIO.setup(led3, GPIO.OUT) # LED pin set as output
	GPIO.setup(led4, GPIO.OUT) # LED pin set as output
	GPIO.setup(sc_led, GPIO.OUT)


# a function to clear the gpio
def cleangpio():
	GPIO.cleanup() # cleanup all GPIO

# a function to clear the LEDs
def resetleds():
	shiftout(0)
	if configure.tr108:
		GPIO.output(led1, GPIO.LOW)
		GPIO.output(led2, GPIO.LOW)
		GPIO.output(led3, GPIO.LOW)

	if configure.tr109:
		GPIO.output(led1, GPIO.LOW)
		GPIO.output(led2, GPIO.LOW)
		GPIO.output(led3, GPIO.LOW)
		GPIO.output(led4, GPIO.LOW)
		GPIO.output(sc_led, GPIO.LOW)



# # The following set of functions are for activating each LED individually.
# # I figured it was easier than having different functions for different combinations.
# # This way you can just manually set them as you please.
def screen_on():
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
	GPIO.output(sc_led, GPIO.LOW)

class ripple(object):
	def __init__(self):
		self.beat = 0

		pass

	def cycle(self):

		testbin = '0b10001100'

		#	0		0		0		0		0		0		0		0
		#	a		b		d		g		pwr		a1		b1		d1

		#140
		#74
		#41
		#26


		screen_on()
		if configure.leds[0]:
			self.beat += 1

			if self.beat > 3:
				self.beat = 0

			if self.beat == 0:
				shiftout(140)

			if self.beat == 1:
				shiftout(74)

			if self.beat == 2:
				shiftout(41)

			if self.beat == 3:
				shiftout(26)
		else:
			print("leds shutting down")
			resetleds()
			shiftout(0)
			screen_off()
