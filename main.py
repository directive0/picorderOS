#!/usr/bin/python

# PicorderOS Alpha --------------------------------- April 2019
# Created by Chris Barrett ------------------------- directive0
#
# Intended Goals:
# Query data from 3 or more sensors and displays them on screen
# Monitor 3 or more HMI elements to provide user control
# Store data as CSV file for later viewing

print("PicorderOS - alpha stage")
print("Loading Main Script")


# filehandling controls saving data to disk and retrieving information
from filehandling import *
from objects import *


if configure.tr108:
	from pygame_display import *
	if not configure.pc:
		from sensehatbasics import *

		if configure.amg88xx:
			from sensehatbasics import *

if configure.tr109:
	if not configure.pc:
		from bme import *

if configure.pc:
	from getcpu import *
	from gpiodummy import *
else:
	from gpiobasics import *


if configure.display == "st7735":
	from colourluma import *

if configure.display == "5110":
	from nokialuma import *

# Default parameters:

# sets the default mode that is called after the splash screen.
firstpage = "mode_a"

# the following function is our main object, it contains all the flow for our program.
def Main():
	status = "mode_a"

	timeit = timer()
	ledtime = timer()
	interval = 0
	buttons = debounce()

	# Instantiate a screen object to draw data to screen.
	if configure.tr108:
		onScreen = Screen(buttons)


	sensors = Sensor()

	if configure.display == "5110":
		dotscreen = NokiaScreen()
	if configure.display == "st7735":
		colourscreen = ColourScreen()

	timeit.logtime()
	ledtime.logtime()


	#lights = ripple()
	# The following while loop catches ctrl-c exceptions. I use this structure so that status changes will loop back around and have a chance to activate different functions. It gets a little weird going forward, bear with me.
	while status != "quit":
		print(status)
		# try allows us to capture a keyboard interrupt and assign behaviours.
		try:
			# Runs the startup animation played when you first boot the program.

			# Create a timer object to time things.
			start_time = time.time()

			while status == "startup":
				status = "mode_a"

				if configure.tr108:
					status = onScreen.startup_screen(start_time)

			if status == "ready":
				status = firstpage

			# The rest of these loops all handle a different mode, switched by buttons within the functions.
			while(status == "mode_a"):

				if timeit.timelapsed() > interval:
					data = sensors.get()

					if configure.tr108:
						status = onScreen.graph_screen(data)
					if configure.tr109:
						lights.cycle()

					if configure.display == "5110":
						colourscreen.push(data)
					if configure.display == "st7735":
						colourscreen.push(data)

					timeit.logtime()

			while(status == "mode_b"):
				if timeit.timelapsed() > interval:
					data = sensors.get()

					if configure.tr108:
						status = onScreen.slider_screen(data)
					if configure.tr109:
						lights.cycle()

					if configure.display == "5110":
						colourscreen.push(data)
					if configure.display == "st7735":
						colourscreen.push(data)

					timeit.logtime()

			while (status == "settings"):
				status = onScreen.settings()


		# If CTRL-C is received the program gracefully turns off the LEDs and resets the GPIO.
		except KeyboardInterrupt:
			status = "quit"

	resetleds()
	cleangpio()
	#print("Quit reached")

#print("Main class loaded and online")
# the following call starts our program
Main()
