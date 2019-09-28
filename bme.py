#!/usr/bin/env python

# the following is a sensor module for use with the PicorderOS
print("Loading BME680 Sensor Module")
import bme680
from objects import *

class Sensor(object):
	def __init__(self):
		self.sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

		# These oversampling settings can be tweaked to
		# change the balance between accuracy and noise in
		# the data.

		self.sensor.set_humidity_oversample(bme680.OS_2X)
		self.sensor.set_pressure_oversample(bme680.OS_4X)
		self.sensor.set_temperature_oversample(bme680.OS_8X)
		self.sensor.set_filter(bme680.FILTER_SIZE_3)
		self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

		self.sensor.set_gas_heater_temperature(320)
		self.sensor.set_gas_heater_duration(150)
		self.sensor.select_gas_heater_profile(0)

		self.start_time = timer()
		self.start_time.logtime()

		self.curr_time = timer()
		self.curr_time.logtime()

		self.burn_in_time = 300
		self.burn_in_data = []

		self.sensor_name = "BME680"
		self.deg_sym = '\xB0'


		#0				1			2		3		4
		#info = (lower range, upper range, unit, symbol)
		self.temp_info = [-40,85,"Temperature",self.deg_sym + "c"]
		self.humidity_info = [0,100,"Relative Humidity", "%"]
		self.pressure_info = [300,1100,"Barometric Pressure","hPa"]
		self.VOC_info = [300,1100,"Air Quality","Ω","not_ready" ]



	def get(self):
		#print("retrieving sensor data")
		if self.sensor.get_sensor_data():

			dummyload = [self.sensor.data.temperature]
			dummyload2 = [self.sensor.data.pressure]
			dummyload3 = [self.sensor.data.humidity]
			dummyload4 = [self.sensor.data.gas_resistance]

			item1 = dummyload + self.temp_info
			item2 = dummyload2 + self.pressure_info
			item3 = dummyload3 + self.humidity_info
			item4 = dummyload4 + self.VOC_info

			sensorlist = [item1, item2, item3, item4]


			return sensorlist
