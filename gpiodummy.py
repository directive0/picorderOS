#!/usr/bin/python

# External module imports
#import RPi.GPIO as GPIO
import pygame
import sys
import time

# Pin Definitons:
led1 = 4 # Broadcom pin 4 (Pi0 pin 7)
led2 = 17 # Broadcom pin 17 (Pi0 pin 11)
led3 = 27 # Broadcom pin 27 (P1 pin 13)

# The following pins are my three buttons.
buta = 5
butb = 6
butc = 13


## Pin Setup:
#GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
#GPIO.setup(led1, GPIO.OUT) # LED pin set as output
#GPIO.setup(led2, GPIO.OUT) # LED pin set as output
#GPIO.setup(led3, GPIO.OUT) # LED pin set as output
#GPIO.setup(buta, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Circle Button for GPIO23
#GPIO.setup(butb, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Square Button for GPIO22
#GPIO.setup(butc, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #R Button for GPIO4


# a function to clear the gpio
def cleangpio():
	pass
#    GPIO.cleanup() # cleanup all GPIO

# a function to clear the LEDs

def resetleds():
	pass
	#GPIO.output(led1, GPIO.LOW)
	#GPIO.output(led2, GPIO.LOW)
	#GPIO.output(led3, GPIO.LOW)

# The following set of functions are for activating each LED individually. I figured it was easier than having different functions for different combinations. This way you can just manually set them as you please.
def leda_on():
	pass
#    GPIO.output(led1, GPIO.HIGH)

def ledb_on():
	pass
#	GPIO.output(led2, GPIO.HIGH)

def ledc_on():
	pass
#    GPIO.output(led3, GPIO.HIGH)

def leda_off():
	pass
#GPIO.output(led1, GPIO.LOW)

def ledb_off():
	pass
	#GPIO.output(led2, GPIO.LOW)

def ledc_off():
	pass
#    GPIO.output(led3, GPIO.LOW)

# The following function returns the instantanious state of each button.
def buttonget():

	buttondict = {'buta':False, 'butb':False, 'butc':False}

	return buttondict

# The following function returns the debounced activation for each button, much more elegant for use in my program.
class debounce(object):

	def __init__(self):
		self.awaspressed = 0
		self.bwaspressed = 0
		self.cwaspressed = 0
		self.afire = False
		self.bfire = False
		self.cfire = False

	def read(self):
		self.afire = False
		self.bfire = False
		self.cfire = False
		buttondict = {'buta':False, 'butb':False, 'butc':False}
		buttondict['buta'] = self.afire
		buttondict['butb'] = self.bfire
		buttondict['butc'] = self.cfire

		return buttondict


# The following function is merely a hardware tool so I can ensure my LED's were wired correctly.
def cycleloop():
	pass
