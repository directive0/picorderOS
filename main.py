#!/usr/bin/python

# PicorderOS Alpha --------------------------------- September 2020
# Created by Chris Barrett ------------------------- directive0

print("PicorderOS - Alpha")
print("Loading Components")

import os
from queue import Queue
from threading import Thread

os.environ['SDL_AUDIODRIVER'] = 'dsp'

from objects import *
from sensors import *
from plars import *
from input import *

if configure.audio[0]:
	from audio import *

# This part loads the appropriate modules depending on which preference flags are set.

# If we are NOT just running on a computer for development or demo purposes.
if not configure.pc:
	# load up the LED indicator module
	from leds import *
else:
	# otherwise load up the demonstration and dummy modules that emulate sensors and pass GPIO signals without requiring any real GPIO.
	from gpiodummy import *

# The following are only loaded in TR-108 mode
if configure.tr108:
	# Load the TR-108 display modules
	from tos_display import *
#	if configure.sensehat:
#		from sensehat import *


# for the new TR-109 there are two display modes supported.
if configure.tr109:

	if configure.display == 2:
		from lcars_clr import *

	# 1.8" TFT colour LCD
	if configure.display == 1:
		from lcars_clr import *

	# Nokia 5110 black and white dot matrix screen.
	if configure.display == 0:
		from lcars_bw import *


# the following function is our main loop, it contains all the flow for our program.
def Main():

	#start the sensor loop
	sensor_thread = Thread(target = threaded_sensor, args = ())
	sensor_thread.start()

	if configure.leds[0]:
		# seperate thread for LED lighting.
		led_thread = Thread(target = ripple_async, args = ())
		led_thread.start()


	#start the event monitor
	input_thread = Thread(target = threaded_input, args = ())
	input_thread.start()

	#start the audio service
	if configure.audio[0]:
		audio_thread = Thread(target = threaded_audio, args = ())
		audio_thread.start()

	# Instantiate a screen object to draw data to screen. Right now for testing
	# they all have different names but each display object should use the same
	# named methods for simplicity sake.
	if configure.tr108:

		PyScreen = Screen()

	if configure.tr109:

		if configure.display == 0:
			dotscreen = NokiaScreen()
		if configure.display == 1:
			colourscreen = ColourScreen()
			colourscreen.start_up()

			if configure.sensor_ready[0]:
				plars.set_buffer(colourscreen.get_size()*len(configure.sensor_info[0])*3)


	print("Main Loop Starting")

	# Main loop. Break when status is "quit".
	while configure.status[0] != "quit":


		# try allows us to capture a keyboard interrupt and assign behaviours.
		try:

			# Runs the startup animation played when you first boot the program.
			if configure.status[0] == "startup":

				if configure.tr109:
					configure.status[0] = colourscreen.start_up()


				if configure.tr108:
					configure.status[0] = PyScreen.startup_screen(start_time)

			if configure.status[0] == "ready":
				configure.status[0] = "mode_a"

			# The rest of these loops all handle a different mode, switched by buttons within the functions.
			if (configure.status[0] == "mode_a"):

				# the following is only run if the tr108 flag is set
				if configure.tr108:

					configure.status[0] = PyScreen.graph_screen()

					if not configure.pc:
						leda_on()
						ledb_off()
						ledc_off()

				if configure.tr109:

					if configure.display == 0:
						configure.status[0] = dotscreen.push(data)
					if configure.display == 1:
						configure.status[0] = colourscreen.graph_screen()

			if configure.status[0] == "mode_b":

				if configure.tr108:

					configure.status[0] = PyScreen.slider_screen()
					if not configure.pc:
						leda_off()
						ledb_on()
						ledc_off()

				if configure.tr109:

					if configure.display == 0:
						configure.status[0] = dotscreen.push(data)
					if configure.display == 1:
						configure.status[0] = colourscreen.em_screen()


			if configure.status[0] == "mode_c":


				if configure.tr109:
					if configure.display == 1:
						configure.status[0] = colourscreen.thermal_screen()


			if (configure.status[0] == "settings"):

				if configure.tr108:
					configure.status[0] = PyScreen.settings()
					if not configure.pc:
						leda_off()
						ledb_off()
						ledc_on()

				if configure.tr109:
					if configure.display == 0:
						configure.status[0] = dotscreen.push()
					if configure.display == 1:
						configure.status[0] = colourscreen.settings()

			# Handles the poweroff screen
			if (configure.status[0] == "poweroff"):

				if configure.tr109:
					if configure.display == 0:
						configure.status[0] = dotscreen.push()
					if configure.display == 1:
						configure.status[0] = colourscreen.powerdown()

			if configure.status[0] == "shutdown":
				print("Shut Down!")
				configure.status[0] = "quit"
				resetleds()
				cleangpio()
				os.system("sudo shutdown -h now")

		# If CTRL-C is received the program gracefully turns off the LEDs and resets the GPIO.
		except KeyboardInterrupt:
			configure.status[0] = "quit"

	print("Quit Encountered")
	print("Main Loop Shutting Down")

	# The following calls are for cleanup and just turn "off" any GPIO
	resetleds()
	cleangpio()
	plars.shutdown()
	#print("Quit reached")


# the following call starts our program and begins the loop.
Main()
