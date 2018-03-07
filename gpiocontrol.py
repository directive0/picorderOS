# Picorder 2 - GPIO control interface.
# System will monitor buttons and provide lighting commands.

#Right now I feel like the sequencing "look and feel" lights will just be tied into a simple LED sequencer chip.

# External module imports
import RPi.GPIO as GPIO
import sys
import time

# Pin Definitons:
led1 = 4 # Broadcom pin 4 (Pi0 pin 7)
led2 = 17 # Broadcom pin 17 (Pi0 pin 11)
led3 = 27 # Broadcom pin 27 (Pi0 pin 13)

# The following pins are my three buttons.
geobut = 5
metbut = 6
biobut = 13


# Pin Setup:    
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(led1, GPIO.OUT) # LED pin set as output
GPIO.setup(led2, GPIO.OUT) # LED pin set as output
GPIO.setup(led3, GPIO.OUT) # LED pin set as output
GPIO.setup(geobut, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Circle Button for GPIO23
GPIO.setup(metbut, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Square Button for GPIO22
GPIO.setup(biobut, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #R Button for GPIO4


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
     
    buttondict = {'geobut':False, 'metbut':False, 'biobut':False} 

    buttondict['geobut'] = GPIO.input(geobut)
    buttondict['metbut'] = GPIO.input(metbut)
    buttondict['biobut'] = GPIO.input(biobut)
    
    #buttonstate = GPIO.input(geobut),GPIO.input(metbut),GPIO.input(biobut)
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
        
        if (button_readings['geobut']==False):
            self.awaspressed = 1

        if (button_readings['metbut']==False):
            self.bwaspressed = 1
          
        if (button_readings['biobut']==False):
            self.cwaspressed = 1
        
        if (self.awaspressed == 1):
            if (button_readings['geobut']==True):
                self.afire = True
                self.awaspressed = 0

        if (self.bwaspressed == 1):
            if (button_readings['metbut']==True):
                self.bfire = True
                self.bwaspressed = 0
                
        if (self.cwaspressed == 1):
            if (button_readings['biobut']==True):
                self.cfire = True
                self.cwaspressed = 0
        
        buttondict = {'geobut':False, 'metbut':False, 'biobut':False} 
        buttondict['geobut'] = self.afire
        buttondict['metbut'] = self.bfire
        buttondict['biobut'] = self.cfire
        
        self.afire = False
        self.bfire = False
        self.cfire = False
        
        return buttondict
    
# The following function is merely a hardware tool so I can ensure my LED's were wired correctly.
def cycleloop():
    while True:
        try:
            leda_on()
            time.sleep(0.2)
            leda_off()
            ledb_on()
            time.sleep(0.2)
            ledb_off()
            ledc_on()
            time.sleep(0.2)
            ledc_off()
    
        except KeyboardInterrupt:
            print("cleaning up")
            
            cleangpio()
            print("shutting down")
            sys.exit()

#resetleds()

