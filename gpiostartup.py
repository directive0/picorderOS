#!/usr/bin/python

# External module imports
import RPi.GPIO as GPIO
import sys
import time
import os

# Pin Definitons:
led1 = 4 # Broadcom pin 4 (Pi0 pin 7)
led2 = 17 # Broadcom pin 17 (Pi0 pin 11)
led3 = 27 # Broadcom pin 27 (P1 pin 13)

# The following pins are my three buttons.
buta = 5
butb = 6
butc = 13


# Pin Setup:
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(led1, GPIO.OUT) # LED pin set as output
GPIO.setup(led2, GPIO.OUT) # LED pin set as output
GPIO.setup(led3, GPIO.OUT) # LED pin set as output
GPIO.setup(buta, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Circle Button for GPIO23
GPIO.setup(butb, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Square Button for GPIO22
GPIO.setup(butc, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #R Button for GPIO4


# a function to clear the gpio 
def cleangpio():
    GPIO.cleanup() # cleanup all GPIO

# a function to clear the LEDs
def resetleds():
    GPIO.output(led1, GPIO.LOW)
    GPIO.output(led2, GPIO.LOW)
    GPIO.output(led3, GPIO.LOW)

# The following set of functions are for activating each LED individually. I figured it was easier than having different functions for different combinations. This way you can just manually set them as you please.
def leda_on():
    GPIO.output(led1, GPIO.HIGH)
    
def ledb_on():
    GPIO.output(led2, GPIO.HIGH)
    
def ledc_on():
    GPIO.output(led3, GPIO.HIGH)

def leda_off():
    GPIO.output(led1, GPIO.LOW)
    
def ledb_off():
    GPIO.output(led2, GPIO.LOW)

def ledc_off():
    GPIO.output(led3, GPIO.LOW)

# The following function returns the instantanious state of each button.
def buttonget():
     
    buttondict = {'buta':False, 'butb':False, 'butc':False} 

    buttondict['buta'] = GPIO.input(buta)
    buttondict['butb'] = GPIO.input(butb)
    buttondict['butc'] = GPIO.input(butc)
    
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
        button_readings = buttonget()
        
        if (button_readings['buta']==False):
            self.awaspressed = 1

        if (button_readings['butb']==False):
            self.bwaspressed = 1
          
        if (button_readings['butc']==False):
            self.cwaspressed = 1
        
        if (self.awaspressed == 1):
            if (button_readings['buta']==True):
                self.afire = True
                self.awaspressed = 0

        if (self.bwaspressed == 1):
            if (button_readings['butb']==True):
                self.bfire = True
                self.bwaspressed = 0
                
        if (self.cwaspressed == 1):
            if (button_readings['butc']==True):
                self.cfire = True
                self.cwaspressed = 0
        
        buttondict = {'buta':False, 'butb':False, 'butc':False} 
        buttondict['buta'] = self.afire
        buttondict['butb'] = self.bfire
        buttondict['butc'] = self.cfire
        
        self.afire = False
        self.bfire = False
        self.cfire = False
        
        return buttondict
    
resetleds()

buttons = debounce()

state = 'running'

while (state == 'running'):
    button_readings = buttons.read()
    
    if (button_readings['buta']==True) and (button_readings['butb']==False) and (button_readings['butc']==False):
        os.system ("python picorder.py")
        print('launching tricorder')
        state = 'exit'

if state == 'exit':
    print('exit was reached')
    cleangpio
    



