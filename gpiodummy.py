#!/usr/bin/python
print("Loading GPIO Dummy")

# This entire module just returns dummy results so as to avoid errors in the program. It has no useful purpose beyond that.

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


# a function to clear the gpio
def cleangpio():
	pass

def resetleds():
	pass

def leda_on():
	pass

def ledb_on():
	pass

def ledc_on():
	pas

def leda_off():
	pass

def ledb_off():
	pass

def ledc_off():
	pass


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
