#!/usr/bin/python

# PicorderOS Alpha ------------------- March 2019
# Created by Chris Barrett - directive0
#
# Intended Goals:
# Query data from 3 or more sensors and displays them on screen.
# Monitor 3 or more HMI elements to provide user control
# Store data as CSV file for later viewing
#



# If running on Pi use these imports:
#from gpiobasics import *
#from sensehatbasics import *


print("PicorderOS - alpha stage")
print("Loading Main Script")


# filehandling controls saving data to disk and retrieving information
from filehandling import *

# If running on Pi use these imports:
from bme import *
from gpiobasics import *
#from sensehatbasics import *

# If testing on PC use these imports:
#from getcpu import *
#from gpiodummy import *
from display import *
from objects import *
from nokialuma import *

# Default parameters:

# sets the default mode that is called after the splash screen.
firstpage = "mode_a"

#SSSprint("Status is " + str(status))

# the following function is our main object, it contains all the flow for our program.
def Main():
	status = "startup"
	timeit = timer()
	ledtime = timer()
	interval = 0
	#ledinterval = .05
	# Instantiate a screen object to draw data to screen.
	#onScreen = Screen()
	sensors = Sensor()
	dotscreen = NokiaScreen()
	timeit.logtime()
	#ledtime.logtime()
	
	lights = ripple()
	# The following while loop catches ctrl-c exceptions. I use this structure so that status changes will loop back around and have a chance to activate different functions. It gets a little weird going forward, bear with me.
	while status != "quit":

		# try allows us to capture a keyboard interrupt and assign behaviours.
		try:
			# Runs the startup animation played when you first boot the program.

			# Create a timer object to time things.
			#start_time = time.time()

			while status == "startup":
				status = "mode_a"
				pass
				#status = onScreen.startup_screen(start_time)

			if status == "ready":
				status = firstpage

			# The rest of these loops all handle a different mode, switched by buttons within the functions.
			while(status == "mode_a"):
				#print("in slider loop")
				#print("getting sensors")
				#print("attempting to draw")
				

				
				if timeit.timelapsed() > interval:
					lights.cycle()
					data = sensors.get()
					dotscreen.push(data)
					#status = onScreen.graph_screen(data)
					timeit.logtime()

			while(status == "mode_b"):
				pass

			while (status == "mode_c"):
				pass

		# If CTRL-C is received the program gracefully turns off the LEDs and resets the GPIO.
		except KeyboardInterrupt:
			status = "quit"
	
	resetleds()
	cleangpio()
	#print("Quit reached")

#print("Main class loaded and online")
# the following call starts our program
Main()
