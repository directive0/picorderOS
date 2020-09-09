#!/usr/bin/python

# PicorderOS Alpha --------------------------------- June 2019
# Created by Chris Barrett ------------------------- directive0
#
# Intended Goals:
# Support three display modes (B/W LCD, Colour LCD, Pygame for tr108)
# Support multiple sensor options across all platforms (BME680, AMG8833, sensehat)

print("PicorderOS - Alpha")
print("Loading Components")

from objects import *
from sensors import *

# This part loads the appropriate modules depending on which preference flags are set.

# If we are NOT just running on a computer for development or demo purposes.
if not configure.pc:
	# load up the LED indicator module and sensors that require GPIO.
	from leds import *
#	from sensehat import *
	#from sensors import *
else:
	# otherwise load up the demonstration and dummy modules that emulate sensors and pass GPIO signals without requiring any real GPIO.
	#from getcpu import *
	from gpiodummy import *


# The following are only loaded in TR-108 mode
if configure.tr108:
	# Load the TR-108 display modules
	from tos_display import *
	if configure.senshat:
		from sensehat import *


# for the new TR-109 there are two display modes supported.
if configure.tr109:

	# 1.8" TFT colour LCD
	if configure.display == "1":
		from lcars_clr import *

	# Nokia 5110 black and white dot matrix screen.
	if configure.display == "0":
		from lcars_bw import *

# the following function is our main object, it contains all the flow for our program.
def Main():


	# From out here in the loop we should instantiate the objects that are common to whatever display configuration we want to use.
	sensors = Sensor()
	timeit = timer()
	ledtime = timer()

	# I think this sets the delay between draws.
	interval = 0.5


	# Instantiate a screen object to draw data to screen. Right now for testing they all have different names but each display object should use the same named methods for simplicity sake.
	if configure.tr108:
		PyScreen = Screen(buttons)
		if not configure.pc:
			moire = led_display()

	if configure.tr109:
		if configure.display == "0":
			dotscreen = NokiaScreen()
		if configure.display == "1":
			colourscreen = ColourScreen()

	timeit.logtime()
	ledtime.logtime()

	if configure.leds[0]:
		lights = ripple()

	print("Main Loop Starting")
	# The following while loop catches ctrl-c exceptions. I use this structure so that configure.status[0] changes will loop back around and have a chance to activate different functions. It gets a little weird going forward, bear with me.
	while configure.status[0] != "quit":
		#print(configure.status[0])

		# try allows us to capture a keyboard interrupt and assign behaviours.
		try:
			# Runs the startup animation played when you first boot the program.

			# Create a timer object to time things.
			start_time = time.time()

			if configure.status[0] == "startup":
				configure.status[0] = "mode_a"

				if configure.tr108:
					configure.status[0] = PyScreen.startup_screen(start_time)

			if configure.status[0] == "ready":
				configure.status[0] = "mode_a"

			# The rest of these loops all handle a different mode, switched by buttons within the functions.
			if (configure.status[0] == "mode_a"):

				#if timeit.timelapsed() > interval:
				data = sensors.get()

				# the following is only run if the tr108 flag is set
				if configure.tr108:

					configure.status[0] = PyScreen.graph_screen(data)

					if not configure.pc:
						leda_on()
						ledb_off()
						ledc_off()
						if configure.moire:
							moire.animate()

				if configure.tr109:
					if timeit.timelapsed() > interval:
						if configure.display == "0":
							configure.status[0] = dotscreen.push(data)
						if configure.display == "1":
							configure.status[0] = colourscreen.graph_screen(data)
						if configure.leds[0] and not configure.pc:
							lights.cycle()



					#timeit.logtime()

			if (configure.status[0] == "mode_b"):

				if timeit.timelapsed() > interval:
					data = sensors.get()

					if configure.tr108:
						configure.status[0] = PyScreen.slider_screen(data)
						if not configure.pc:
							leda_off()
							ledb_on()
							ledc_off()


					if configure.tr109:
						if configure.leds[0]:
							lights.cycle()

						if configure.display == "0":
							configure.status[0] = dotscreen.push(data)
						if configure.display == "1":
							configure.status[0] = colourscreen.thermal_screen(data)

					timeit.logtime()

			if (configure.status[0] == "settings"):
				#print(configure.status[0])
				if configure.tr108:
					configure.status[0] = PyScreen.settings()
					if not configure.pc:
						leda_off()
						ledb_off()
						ledc_on()

				if configure.tr109:
					if configure.display == "0":
						configure.status[0] = dotscreen.push(data)
					if configure.display == "1":
						configure.status[0] = colourscreen.settings(data)

			# Handles the poweroff screen
			if (configure.status[0] == "poweroff"):

				if configure.tr109:
					if configure.display == "0":
						configure.status[0] = dotscreen.push()
					if configure.display == "1":
						configure.status[0] = colourscreen.powerdown()

		# If CTRL-C is received the program gracefully turns off the LEDs and resets the GPIO.
		except KeyboardInterrupt:
			configure.status[0] = "quit"
	print("Quit Encountered")
	print("Main Loop Shutting Down")

	# The following calls are for cleanup and just turn "off" any GPIO
	resetleds()
	cleangpio()
	#print("Quit reached")


# the following call starts our program and begins the loop.
Main()
