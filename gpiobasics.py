#!/usr/bin/python

# new Changes
# will need to support a reed switch and more inputs.

# External module imports
import RPi.GPIO as GPIO

# Pin Definitons:
led1 = 19 # Broadcom pin 19
led2 = 6 # Broadcom pin 13
led3 = 20
led4 = 16

# The following pins are basic three buttons.
buta = 26
butb = 21
butc = 13


# Pin Setup:
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(led1, GPIO.OUT) # LED pin set as output
GPIO.setup(led2, GPIO.OUT) # LED pin set as output
GPIO.setup(led3, GPIO.OUT) # LED pin set as output
GPIO.setup(led4, GPIO.OUT) # LED pin set as output
GPIO.setup(buta, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(butb, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(butc, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# a function to clear the gpio
def cleangpio():
	GPIO.cleanup() # cleanup all GPIO

# a function to clear the LEDs
def resetleds():
	GPIO.output(led1, GPIO.LOW)
	GPIO.output(led2, GPIO.LOW)
	GPIO.output(led3, GPIO.LOW)
	GPIO.output(led4, GPIO.LOW)

# The following set of functions are for activating each LED individually. I figured it was easier than having different functions for different combinations. This way you can just manually set them as you please.
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

class ripple(object):
	def __init__(self):
		self.beat = 0

		pass

	def cycle(self):
		self.beat += 1

		if self.beat > 3:
			self.beat = 0

		if self.beat == 0:
			leda_on()
			ledb_off()
			ledc_off()
			ledd_off()

		if self.beat == 1:
			leda_off()
			ledb_on()
			ledc_off()
			ledd_off()

		if self.beat == 2:
			leda_off()
			ledb_off()
			ledc_on()
			ledd_off()

		if self.beat == 3:
			leda_off()
			ledb_off()
			ledc_off()
			ledd_on()


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

		buttonlist = [self.afire, self.bfire, self.cfire]

		self.afire = False
		self.bfire = False
		self.cfire = False
		#print("buttons = " + str(buttonlist))
		return buttonlist

# The following function is merely a hardware tool so I can ensure my LED's were wired correctly.
#def cycleloop():
	#while True:
			#try:
			#leda_on()
				#time.sleep(0.2)
			#leda_off()
			#ledb_on()
				#time.sleep(0.2)
			#ledb_off()
			#ledc_on()
				#time.sleep(0.2)
			#ledc_off()

			#except KeyboardInterrupt:
			#print("cleaning up")

			#cleangpio()
				#print("shutting down")
			#sys.exit()

#resetleds()
