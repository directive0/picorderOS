#!/usr/bin/python
# This module holds the initialization and global variables for the program.
# Special thanks to SCIFI.radio for their work on the INI loader!

import time, configparser
from os.path import exists


class preferences(object):
	def str2bool(self,v):
  		return v.lower() in ("yes", "true", "t", "1")

	def createMissingINI(self,filepath):
		print("config.ini file is missing - making a new one. You'll want to edit to taste and restart.")
		config = configparser.ConfigParser(allow_no_value=True)

		config['SYSTEM'] = {'# Text displayed after "picorderOS" on title screen':None,
							'version':'v2',                               	# version number
							'# Greeting displayed on title screen':None,
							'boot_message':'Initializing Sensor Array',   	# Initialization Message
							'# Boot Delay is the time allowed to display the banner screen':None,
							'boot_delay':'2',								# boot delay
							'# Emulating the hardware on a PC?':None,
							'pc':'no',       								# emulating the hardware on a PC?
							'# Select either TR-108, or TR-109. You must choose only one.':None,
							'tr108':'yes',									# Running a TR-108 simulation - mutually exclusive with tr109
							'tr109':'no'}									# Running a TR-109 simulation - mutually exclusive with tr108

		config['SENSORS'] =  {'# Only TR-108 uses SenseHat':None,
							'sensehat':'no',								# Only TR-108 uses this
							'system_vitals':'yes',
							'# BME680 Raw Values':None,
							'bme':'no',
							'# BME680 VOC BSEC':None,
							'bme_bsec':'no',
							'amg8833':'no',
							'pocket_geiger':'no',
							'# IR Infrared Imaging':None,
							'ir_thermo':'no',								# IR infrared imaging
							'envirophat':'no',
							'# Only TR-109 uses this':None,
							'EM':'no'}										# Only TR-109 uses this

		config['INPUT'] =    {'# Controls which input method is active (Choose only one)':None,
							'kb':'no',
							'gpio':'no',
							'cap_mpr121':'no',
							'pcf8575':'no',
							'cap1208':'no',
							'sensehat_joystick':'no',
							'capsensitivity':'50'}							# Used only if cap1208 is 'yes'

		config['PIN ASSIGNMENTS'] = {'#I2C pins':None,
							'PIN_SDA':'2',							# I2C pins
							'PIN_SCL':'3',
							'# Main board shift register pins':None,
							'# The TR-109 supports two shift registers, and two sets of pin addresses':None,
							'# Prototype units 00 and 01 have different pin assignments,':None,
							'# so these may need to be swapped.':None,

							'PIN_DATA':'16',						# Main board shift register pins - The TR109 supports two shift registers,
							'PIN_LATCH':'6',						# and so two sets of pin addresses; prototype unit 00 and 01 have different pin
							'PIN_CLOCK':'20',						# assignments, so these values may need to be swapped

							'PIN_DATA2':'19',						# Sensor board shift register pins
							'PIN_LATCH2':'21',
							'PIN_CLOCK2':'26',
							'# Hall effect sensor pins, for door open/close detection':None,

							'HALLPIN1':'12',						# Hall effect sensor pins, for door open and close
							'HALLPIN2':'4',

							'# Cap1208 Alert Pin':None,
							'ALERTPIN':'0',							# Cap1208 Alert Pin

							'# Pocket-Geiger Sensor Pins':None,
							'PG_SIG':'20',							# PocketGeiger Pins
							'PG_NS':'21'}

		config['OUTPUT'] = {'display':'1',
							'LED_timer':'0.2',
							}

		config['GLOBALS'] = {'# Controls whether LEDs are active':None,
							'leds':'yes',
							'# Enables the moire pattern on the SenseHat LED matrix - TR-108 only':None,
							'moire':'no',
							'video':'yes',
							'# Enables audio playback (videos will not play without this)':None,
							'audio':'no',									# Enables audio playback
                                                        '# Enables video player capabilities':None,
							'video':'no',
							'alarm':'no',
							'# If sleep is "yes" then lights will respond to Hall Effect sensors':None,
							'sleep':'yes',									# If sleep is True the lights will respond to hall effect sensors
							'# Autoranging of graphs':None,
							'autoranging':'yes',							# Auto ranging of graphs
							'mode_a_graph_width':'280',						# graph width for TR108 mode_a
							'mode_a_graph_height':'160',					# graph height for TR108 mode_a\
							'mode_a_x_offset':18,							# x offset for TR108 mode_a
							'mode_a_y_offset':31,							# y offset for TR108 mode_a
							'# Interpolate Temperature':None,
							'interpolate':'yes',							# Interpolate temperature
							'samplerate':'0',
							'# Affects graphing density':None,
							'samples':'16',
							'# Currently not used':None,
							'displayinterval':'0',
							'# Turns data logging on - data is written to data/datacore.csv':None,
							'datalog':'no',
							'doordetection':'yes',
							'# Settings for mode_a Graph Screen on TR-108':None,
							'graph_width':'280',
							'graph_height':'182',
							'graph_x':'18',
							'graph_y':'20'}

		with open('config.ini','w') as configfile:
			config.write(configfile)
			print("New INI file is ready.")

	# Initializes the parameters for the program.
	def __init__(self):
		print("Loading Global Objects")
		if not exists("config.ini"):
			self.createMissingINI('config.ini')

		config=configparser.ConfigParser()
		config.read('config.ini')

		# Sets the variables for boot up
		self.version = config['SYSTEM']['version']
		self.boot_message = config['SYSTEM']['boot_message']

		self.boot_delay = int(config['SYSTEM']['boot_delay'])

		# enables "PC Mode": sensors and GPIO calls are disabled.
		# Machine vitals are substituted and Luma screens use emulator
		self.pc = self.str2bool(config['SYSTEM']['pc'])

		# These two bits determine the target device (Original picorder or new version)
		# If both true the screens will fight for control!
		self.tr108 = self.str2bool(config['SYSTEM']['tr108'])
		self.tr109 = self.str2bool(config['SYSTEM']['tr109'])
# SENSORS----------------------------------------------------------------------#
		# TR108 uses this sensehat
		self.sensehat = self.str2bool(config['SENSORS']['sensehat'])

		# Toggles individual sensor support
		self.system_vitals = self.str2bool(config['SENSORS']['system_vitals'])
		self.bme = self.str2bool(config['SENSORS']['bme'])
		self.amg8833 = self.str2bool(config['SENSORS']['amg8833'])

		# Experimental sensors
		self.pocket_geiger = self.str2bool(config['SENSORS']['pocket_geiger'])
		self.ir_thermo = self.str2bool(config['SENSORS']['ir_thermo'])
		self.envirophat = self.str2bool(config['SENSORS']['envirophat'])

		# toggles wifi/bt scanning
		self.EM = self.str2bool(config['SENSORS']['EM'])


# INPUT MODULE-----------------------------------------------------------------#

		# testing this setting to switch between Pygame controls and gpio ones
		self.input_kb = self.str2bool(config['INPUT']['kb']) # also enables Sensehat joystick if present
		self.input_gpio = self.str2bool(config['INPUT']['gpio'])
		self.input_cap_mpr121 = self.str2bool(config['INPUT']['cap_mpr121'])
		self.input_pcf8575 = self.str2bool(config['INPUT']['pcf8575'])
		self.input_joystick = self.str2bool(config['INPUT']['sensehat_joystick'])

		# CAP1208 and sensitivity settings
		self.input_cap1208 = self.str2bool(config['INPUT']['cap1208'])
		self.CAPSENSITIVITY = int(config['INPUT']['capsensitivity'])


# PIN ASSIGNMENTS--------------------------------------------------------------#]

		# GPIO Pin Assignments (BCM)

		# i2c Pins
		self.PIN_SDA = int(config['PIN ASSIGNMENTS']['pin_sda'])
		self.PIN_SCL = int(config['PIN ASSIGNMENTS']['pin_scl'])

		# the tr109 supports two shift registers, and so two sets of pin addresses
		# prototype unit 00 and 01 have different pin assignments for latch and clock
		# so these values may need to be swapped

		# Main board shift register pins
		self.PIN_DATA  = int(config['PIN ASSIGNMENTS']['pin_data'])
		self.PIN_LATCH = int(config['PIN ASSIGNMENTS']['pin_latch'])
		self.PIN_CLOCK = int(config['PIN ASSIGNMENTS']['pin_clock'])

		# Sensor board shift register pins
		self.PIN_DATA2 = int(config['PIN ASSIGNMENTS']['pin_data2'])
		self.PIN_LATCH2 = int(config['PIN ASSIGNMENTS']['pin_latch2'])
		self.PIN_CLOCK2 = int(config['PIN ASSIGNMENTS']['pin_clock2'])


		# Hall effect sensors pins, for door open/close.
		self.HALLPIN1 = int(config['PIN ASSIGNMENTS']['hallpin1'])
		self.HALLPIN2 = int(config['PIN ASSIGNMENTS']['hallpin2'])

		# CAP1208 alert pin
		self.ALERTPIN = int(config['PIN ASSIGNMENTS']['alertpin'])

		# PocketGeiger Pins
		self.PG_SIG = int(config['PIN ASSIGNMENTS']['pg_sig'])
		self.PG_NS = int(config['PIN ASSIGNMENTS']['pg_ns'])

# OUTPUT SETTINGS--------------------------------------------------------------#

		# chooses SPI display (0 for nokia 5110, 1 for st7735)
		self.display = int(config['OUTPUT']['display'])

		# led refresh rate.
		self.LED_TIMER = float(config['OUTPUT']['led_timer'])

# GLOBAL VARIABLES-------------------------------------------------------------#

		# Controls for global event list
		self.eventlist = [[]]
		self.eventready = [False]

		# contains the current button state (0 is unpressed, 1 is pressed)
		self.events = [0,0,0,0,0,0,0,0]

		# holds state for beep input feedback
		self.beep_ready = [False]
		self.alarm_ready = [False]


		# flags control the onboard LEDS. Easy to turn them off if need be.
		self.leds = [self.str2bool(config['GLOBALS']['leds'])] # was True

		# controls Moire pattern on tr-108
		self.moire = [self.str2bool(config['GLOBALS']['moire'])] # was True

		# enables sound effect playback
		self.audio = [self.str2bool(config['GLOBALS']['audio'])]

                # enables video playback library
		self.video = [self.str2bool(config['GLOBALS']['video'])]

		# turns alarms on/off
		self.alarm = [self.str2bool(config['GLOBALS']['alarm'])]

		# If sleep is True the lights will respond to hall effect sensors
		self.sleep = [self.str2bool(config['GLOBALS']['sleep'])]

		# controls auto ranging of graphs
		self.auto = [self.str2bool(config['GLOBALS']['autoranging'])]

        # controls sizes and offsets for mode_a on TR108
		self.mode_a_graph_width = int(config['GLOBALS']['mode_a_graph_width'])
		self.mode_a_graph_height = int(config['GLOBALS']['mode_a_graph_height'])
		self.mode_a_x_offset = int(config['GLOBALS']['mode_a_x_offset'])
		self.mode_a_y_offset = int(config['GLOBALS']['mode_a_y_offset'])
		# holds theme state for UI
		self.theme = [0]

		# sets the number of max sensors for user configuration
		# (is automatically set by the sensor module at startup)
		self.max_sensors = [0]

		#sets the upper and lower threshold for the alert
		self.TEMP_ALERT = (0,100)
		self.interpolate = [True]

		# flag to command the main loop
		self.sensor_ready = [False]
		self.screen_halt = [False]
		self.sensor_halt = [False]

		# An integer determines which sensor in the dataset to plot
		self.sensor1 = [0]
		self.sensor2 = [1]
		self.sensor3 = [2]
		self.sensors = [self.sensor1, self.sensor2, self.sensor3]

		# sets data logging mode.
		self.datalog = [self.str2bool(config['GLOBALS']['datalog'])]
		self.trim_buffer = [True]
		self.buffer_size = [0]
		self.graph_size = [0]
		self.logtime = [60]
		self.recall = [False]

		# used to control refresh speed.
		self.samples = int(config['GLOBALS']['samples'])

		self.samplerate=[float(config['GLOBALS']['samplerate'])]
		self.displayinterval=[float(config['GLOBALS']['displayinterval'])]

		# holds sensor data (issued by the sensor module at init)
		self.sensor_info = []

		self.sensor_data = []

		# holds the global state of the program (allows secondary modules to quit the program should we require it)
		self.status = ["startup"]
		self.last_status = ["startup"]

		# Enables/disables door detection
		self.dr = [self.str2bool(config['GLOBALS']['doordetection'])]

		# holds the physical status of the devices
		self.dr_open = [False]
		self.dr_closed = [False]
		self.dr_opening = [False]
		self.dr_closing = [False]

		# Settings for mode_a Graph_Screen for TR108
		self.graph_width = int(config['GLOBALS']['graph_width'])
		self.graph_height = int(config['GLOBALS']['graph_height'])
		self.graph_x = int(config['GLOBALS']['graph_x'])
		self.graph_y = int(config['GLOBALS']['graph_y'])


# create a shared object for global variables and settings.
configure = preferences()

# the following function maps a value from the target range onto the desination range
def translate(value, leftMin, leftMax, rightMin, rightMax):
	# Figure out how 'wide' each range is
	leftSpan = leftMax - leftMin
	if leftSpan == 0:
		leftSpan = 1
	rightSpan = rightMax - rightMin

	# Convert the left range into a 0-1 range (float)
	valueScaled = float(value - leftMin) / float(leftSpan)

	# Convert the 0-1 range into a value in the right range.
	return rightMin + (valueScaled * rightSpan)

# The following class is to handle interval timers.
# its used to handle concurrent program flow, but also for diagnostic.
class timer(object):

	# Constructor code logs the time it was instantiated.
	def __init__(self):
		self.timeInit = time.time()
		self.logtime()

	# The following funtion returns the first logged value. When the timer was first started.
	def timestart(self):
		return self.timeInit

	# the following function updates the time log with the current time.
	def logtime(self):
		self.lastTime = time.time()

	def event(self,caption):
		print(caption)
		self.logtime()

	# the following function returns the interval that has elapsed since the last log.
	def timelapsed(self):
		#print("comparing times")
		self.timeLapse = time.time() - self.lastTime
		#print("timelapse passed")
		#print(self.timeLapse)
		return self.timeLapse

	def stoplapsed(self):
		self.timelapsed()

	def post(self, caption):
		print(caption, "took: ", self.timelapsed(), "Seconds")
		self.logtime()
