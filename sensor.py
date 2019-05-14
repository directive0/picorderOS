#!/usr/bin/env python

# the following is a sensor module for use with the PicorderOS
print("Loading Shared Sensor module")

if configure.tr108:
	from sense_hat import SenseHat
	# instantiate a sensehat object,
	sense = SenseHat()

if configure.tr108:
	import bme680


import objects
import time




class Sensor(object):
	def __init__(self):

		self.deg_sym = '\xB0'


		#The sensor object

		if configure.tr108:

			self.sensor_name = "Sensehat"

			#0				1			2		3		4
			#info = (lower range, upper range, unit, symbol)
			self.temp_info = [0,65,"Temperature",self.deg_sym + "c"]
			self.humidity_info = [20,80,"Relative Humidity", "%"]
			self.pressure_info = [260,1260,"Barometric Pressure","hPa"]
			self.magnet_info = [-500,500,"Magnetomer","G"]
			self.accelerometer_info = [-500,500,"Acceleration","G"]

		if configure.tr109:

			self.sensor_name = "BME680"
			self.sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

			# These oversampling settings can be tweaked to
			# change the balance between accuracy and noise in
			# the data.

			self.sensor.set_humidity_oversample(bme680.OS_2X)
			self.sensor.set_pressure_oversample(bme680.OS_4X)
			self.sensor.set_temperature_oversample(bme680.OS_8X)
			self.sensor.set_filter(bme680.FILTER_SIZE_3)



			#0				1			2		3		4
			#info = (lower range, upper range, unit, symbol)
			self.temp_info = [-40,85,"Temperature",self.deg_sym + "c"]
			self.humidity_info = [0,100,"Relative Humidity", "%"]
			self.pressure_info = [300,1100,"Barometric Pressure","hPa"]
			self.VOC_info = []




		self.sensor_name = "BME680"
		self.deg_sym = '\xB0'


		#0				1			2		3		4
		#info = (lower range, upper range, unit, symbol)
		self.temp_info = [-40,85,"Temperature",self.deg_sym + "c"]
		self.humidity_info = [0,100,"Relative Humidity", "%"]
		self.pressure_info = [300,1100,"Barometric Pressure","hPa"]
		self.VOC_info = []



	def get(self):
		#print("retrieving sensor data")
		if self.sensor.get_sensor_data():

			dummyload = [self.sensor.data.temperature]
			dummyload2 = [self.sensor.data.pressure]
			dummyload3 = [self.sensor.data.humidity]


			item1 = dummyload + self.temp_info
			item2 = dummyload2 + self.pressure_info
			item3 = dummyload3 + self.humidity_info

			sensorlist = [item1, item2, item3]


			return sensorlist
