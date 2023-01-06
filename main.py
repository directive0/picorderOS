#!/usr/bin/python

# PicorderOS Alpha --------------------------------- Dec 2022
# Created by Chris Barrett ------------------------- directive0
# For my sister, a real life Beverly Crusher.

print("PicorderOS - Alpha")
print("Loading Components")

import os
from threading import Thread


os.environ['SDL_AUDIODRIVER'] = 'alsa'

from objects import *
from sensors import *
from plars import *
from input import *

if configure.audio[0]:
	from audio import *

# This part loads the appropriate modules depending on which preference flags are set.

# load up the LED indicator module
if configure.leds:
	from leds import *


# The following are only loaded in TR-108 mode
if configure.tr108:
	# Load the TR-108 display modules
	from tos_display import *


# for the TR-109 there are two display modes supported.
if configure.tr109:

	# 1.8" TFT colour LCD
	if configure.display == 1 or configure.display == 2:
		from lcars_clr import *

	# Nokia 5110 black and white dot matrix screen.
	if configure.display == 0:
		from lcars_bw import *



# the following function is our main loop, it contains all the flow for our program.
def Main():

	# Instantiate a screen object to draw data to screen. Right now for testing
	# they all have different names but each display object should use the same
	# named methods for simplicity sake.
	if configure.tr108:
		PyScreen = Screen()
		configure.graph_size[0] = PyScreen.get_size()

	if configure.tr109:

		if configure.display == 0:
			dotscreen = NokiaScreen()
		if configure.display == 1 or configure.display == 2:
			colourscreen = ColourScreen()
			colourscreen.start_up()

		configure.graph_size[0] = colourscreen.get_size()

	start_time = time.time()

	#start the sensor loop
	sensor_thread = Thread(target = threaded_sensor, args = ())
	sensor_thread.start()


	# if leds enabled start the event monitor for inputs
	if configure.leds:
		led_thread = Thread(target = ripple_async, args = ())
		led_thread.start()



	input_thread = Thread(target = threaded_input, args = ())
	input_thread.start()

	#start the audio service
	if configure.audio[0]:
		audio_thread = Thread(target = threaded_audio, args = ())
		audio_thread.start()



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

			# The rest of these loops all handle a different mode, switched by buttons within the functions.
			if configure.status[0] == "mode_a":

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
					if configure.display == 1 or configure.display == 2:
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
					if configure.display == 1 or configure.display == 2:
						configure.status[0] = colourscreen.em_screen()

			if configure.status[0] == "mode_c":
				if configure.tr109:
					if configure.display == 1:
						configure.status[0] = colourscreen.thermal_screen()

				if configure.tr108:
					if configure.video:
						configure.status[0] = PyScreen.video_screen()
					else:
						configure.status[0] = PyScreen.slider_screen()
					if not configure.pc:
						leda_on()
						ledb_on()
						ledc_off()

			if configure.status[0] == "settings":

				if configure.tr108:
					configure.status[0] = PyScreen.settings()
					if not configure.pc:
						leda_off()
						ledb_off()
						ledc_on()

				if configure.tr109:
					if configure.display == 0:
						configure.status[0] = dotscreen.push()
					if configure.display == 1 or configure.display == 2:
						configure.status[0] = colourscreen.settings()

			if configure.status[0] == "msd":

				if configure.tr109:
					if configure.display == 1 or configure.display == 2:
						configure.status[0] = colourscreen.msd()


			# Handles the poweroff screen
			if configure.status[0] == "poweroff":

				if configure.tr109:
					if configure.display == 0:
						configure.status[0] = dotscreen.push()
					if configure.display == 1 or configure.display == 2:
						configure.status[0] = colourscreen.powerdown()

			if configure.status[0] == "shutdown":
				print("Shut Down!")
				configure.status[0] = "quit"

				if configure.leds:
					resetleds()

				if configure.input_gpio:
					cleangpio()

				os.system("sudo shutdown -h now")

		# If CTRL-C is received the program gracefully turns off the LEDs and resets the GPIO.
		except KeyboardInterrupt:
			configure.status[0] = "quit"

	print("Quit Encountered")
	print("Main Loop Shutting Down")

	# The following calls are for cleanup and just turn "off" any GPIO
	if configure.leds:
		resetleds()

	if configure.input_gpio:
		cleangpio()

	plars.shutdown()


# the following call starts our program and begins the loop.
Main()
