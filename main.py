#!/usr/bin/python

# PicorderOS Alpha --------------------------------- June 2019
# Created by Chris Barrett ------------------------- directive0
#
# Intended Goals:
# Support three display modes (B/W LCD, Colour LCD, Pygame for tr108)
# Support multiple sensor options across all platforms (BME680, AMG8833, sensehat)

print("PicorderOS - alpha stage")
print("Loading Main Script")

from objects import *

if configure.tr108:
	from pygame_display import *

	if not configure.pc:
		from leds import *
		from sensehat import *

if configure.tr109:
	if not configure.pc:
		from bme import *
		from leds import *

	if configure.display == "1":
		from colourluma import *

	if configure.display == "0":
		from nokialuma import *

if configure.pc:
	from getcpu import *
	from gpiodummy import *





# Default parameters:

# sets the default mode that is called after the splash screen.
firstpage = "startup"

# the following function is our main object, it contains all the flow for our program.
def Main():
	status = firstpage


	# From out here in the loop we should instantiate the objects that are common to whatever display configuration we want to use.
	sensors = Sensor()
	timeit = timer()
	ledtime = timer()
	interval = 0


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
	# The following while loop catches ctrl-c exceptions. I use this structure so that status changes will loop back around and have a chance to activate different functions. It gets a little weird going forward, bear with me.
	while status != "quit":

		# try allows us to capture a keyboard interrupt and assign behaviours.
		try:
			# Runs the startup animation played when you first boot the program.

			# Create a timer object to time things.
			start_time = time.time()

			while status == "startup":
				status = "mode_a"

				if configure.tr108:
					status = PyScreen.startup_screen(start_time)

			if status == "ready":
				status = "mode_a"

			# The rest of these loops all handle a different mode, switched by buttons within the functions.
			while(status == "mode_a"):

				if timeit.timelapsed() > interval:
					data = sensors.get()

					# the following is only run if the tr108 flag is set
					if configure.tr108:

						status = PyScreen.graph_screen(data)

						if not configure.pc:
							leda_on()
							ledb_off()
							ledc_off()
							if configure.moire:
								moire.animate()

					if configure.tr109:
						if configure.display == "0":
							status = dotscreen.push(data)
						if configure.display == "1":
							status = colourscreen.graph_screen(data)
						if configure.leds[0]:
							lights.cycle()



					timeit.logtime()

			while(status == "mode_b"):

				if timeit.timelapsed() > interval:
					data = sensors.get()

					if configure.tr108:
						status = PyScreen.slider_screen(data)
						leda_off()
						ledb_on()
						ledc_off()


					if configure.tr109:
						if configure.leds[0]:
							lights.cycle()

						if configure.display == "0":
							status = dotscreen.push(data)
						if configure.display == "1":
							status = colourscreen.thermal_screen(data)

					timeit.logtime()

			while (status == "settings"):
				#print(status)
				if configure.tr108:
					status = PyScreen.settings()
					leda_off()
					ledb_off()
					ledc_on()

				if configure.tr109:
					status = PyScreen.settings()


		# If CTRL-C is received the program gracefully turns off the LEDs and resets the GPIO.
		except KeyboardInterrupt:
			status = "quit"

	resetleds()
	cleangpio()
	#print("Quit reached")

#print("Main class loaded and online")
# the following call starts our program
Main()
