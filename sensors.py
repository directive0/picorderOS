from objects import *
import time

# Todo:
# - Add possibility for multiple varied sensor loadouts.
# - merge with getcpu


# the following is a sensor module for use with the PicorderOS
print("Loading Unified Sensor Module")

if configure.bme:
	import bme680

if configure.sensehat:
	# instantiates and defines paramteres for the sensehat

	from sense_hat import SenseHat
	# instantiate a sensehat object,
	sense = SenseHat()

	# Initially clears the LEDs once loaded
	sense.clear()

	# Sets the IMU Configuration.
	sense.set_imu_config(True,False,False)

	# activates low light conditions to not blind the user.
	sense.low_light = True

if configure.amg8833:# and not configure.simulate:
	import busio
	import board
	import adafruit_amg88xx

	i2c = busio.I2C(board.SCL, board.SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c)

if configure.bme and not configure.simulate:
	import bme680

# These imports are for the Sin and Tan waveform generators
if configure.system_vitals:
	import psutil
	import math


class Sensor(object):
	# sensors should check the configuration flags to see which sensors are
	# selected and then if active should poll the sensor and append it to then
	# sensor array for the different panels.

	def __init__(self):

		#Init should set up the necessary info for the sensors that are active.

		# We make a sensor counter (for the rest of the program)
		sensorcount = 0

		# create a simple reference for the degree symbol since we use it a lot
		self.deg_sym = '\xB0'


		# add individual sensor module parameters below.

		if configure.system_vitals:
			self.step = 0.0
			self.step2 = 0.0
			self.steptan = 0.0


			self.infoa = [0,100,"CPU Percent","%"]
			self.infob = [0,float(psutil.virtual_memory().total) / 1024,"Virtual Memory", "b"]
			self.infoc = [0,100000,"Bytes Sent", "b"]
			self.infod = [0,100000,"Bytes Received", "b"]
			self.infoe = [-100,100,"Sine Wave", ""]
			self.infof = [-500,500,"Tangent Wave", ""]
			self.infog = [-100,100,"Cos Wave", ""]
			self.infoh = [-100,100,"Sine Wave2", ""]
			sensorcount += 8

			if configure.logdata[0]:
				self.filehandler = datalog()




		if configure.bme: # and not configure.simulate:

			self.bme = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

			# These oversampling settings can be tweaked to
			# change the balance between accuracy and noise in
			# the data.

			self.bme.set_humidity_oversample(bme680.OS_2X)
			self.bme.set_pressure_oversample(bme680.OS_4X)
			self.bme.set_temperature_oversample(bme680.OS_8X)
			self.bme.set_filter(bme680.FILTER_SIZE_3)


			#		self.sensor_name = "BME680"
			self.deg_sym = '\xB0'
			self.bme = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
			self.temp_info = [-40,85,"Temperature (BME)",self.deg_sym + "c"]
			self.humidity_info = [0,100,"Relative Humidity (BME)", "%"]
			self.pressure_info = [300,1100,"Barometric Pressure (BME)","hPa"]
			self.VOC_info = [300,1100,"Air Quality (BME)","hPa"]



		if configure.sensehat:
			# instantiate a sensehat object,
			self.sense = SenseHat()
			# Initially clears the LEDs once loaded
			self.sense.clear()
			# Sets the IMU Configuration.
			self.sense.set_imu_config(True,False,False)
			# activates low light conditions to not blind the user.
			self.sense.low_light = True
			self.temp_info = [0,65,"Thermometer (SH)",self.deg_sym + "c"]
			self.humidity_info = [20,80,"Hygrometer (SH)", "%"]
			self.pressure_info = [260,1260,"Barometer (SH)","hPa"]
			self.magnet_infox = [-500,500,"Magnetomer X (SH)","G"]
			self.magnet_infoy = [-500,500,"Magnetomer Y (SH)","G"]
			self.magnet_infoz = [-500,500,"Magnetomer Z (SH)","G"]
			self.accelerometer_infox = [-500,500,"Accelerometer X (SH)","g"]
			self.accelerometer_infoy = [-500,500,"Accelerometer Y (SH)","g"]
			self.accelerometer_infoz = [-500,500,"Accelerometer Z (SH)","g"]
			configure.max_sensors[0] = 9
			#self.filehandler = datalog()


		if configure.amg8833: # and not configure.simulate:
			self.amg_info = [0,80,"IR Thermal",self.deg_sym + "c"]

		if configure.envirophat: # and not configure.simulate:

			self.rgb = light.rgb()
			self.analog_values = analog.read_all()
			self.mag_values = motion.magnetometer()
			self.acc_values = [round(x, 2) for x in motion.accelerometer()]

			self.temp_info = [0,65,"Thermometer (EP)",self.deg_sym + "c"]
			self.humidity_info = [20,80,"Hygrometer (EP)", "%"]
			self.pressure_info = [260,1260,"Barometer (EP)","hPa"]
			self.magnet_infox = [-500,500,"Magnetomer X (EP)","G"]
			self.magnet_infoy = [-500,500,"Magnetomer Y (EP)","G"]
			self.magnet_infoz = [-500,500,"Magnetomer Z (EP)","G"]
			self.accelerometer_infox = [-500,500,"Accelerometer X (EP)","g"]
			self.accelerometer_infoy = [-500,500,"Accelerometer Y (EP)","g"]
			self.accelerometer_infoz = [-500,500,"Accelerometer Z (EP)","g"]
			configure.max_sensors[0] = 9
			#self.filehandler = datalog()


		configure.sensor_info = self.get()


#		sensordata = pd.DataFrame.append(self.get())#, columns=[self.get(),"min","max","desc","symbol"])
#		print(sensordata)
		#= self.get()

	def sin_gen(self):
		wavestep = math.sin(self.step)
		self.step += .1
		return wavestep

	def tan_gen(self):
		wavestep = math.tan(self.steptan)
		self.steptan += .1
		#print(wavestep)
		return wavestep

	def sin2_gen(self, offset = 0):
		wavestep = math.sin(self.step2)
		self.step2 += .05
		return wavestep

	def cos_gen(self, offset = 0):
		wavestep = math.cos(self.step)
		self.step += .1
		return wavestep


	def get(self):
		sensorlist = []
		if configure.system_vitals:
			dummyload = [float(psutil.cpu_percent())]
			dummyload2 = [float(psutil.virtual_memory().available) * 0.0000001]
			dummyload3 = [float(psutil.net_io_counters().bytes_sent) * 0.00001]
			dummyload4 = [float(psutil.net_io_counters().bytes_recv) * 0.00001]
			dummyload5 = [float(self.sin_gen()*100)]
			dummyload6 = [float(self.tan_gen()*100)]
			dummyload7 = [float(self.cos_gen()*100)]
			dummyload8 = [float(self.sin2_gen()*100)]

			item1 = dummyload + self.infoa
			item2 = dummyload2 + self.infob
			item3 = dummyload3 + self.infoc
			item4 = dummyload4 + self.infod
			item5 = dummyload5 + self.infoe
			item6 = dummyload6 + self.infof
			item7 = dummyload7 + self.infog
			item8 = dummyload8 + self.infoh

			sensorlist += [item1, item2, item3, item4, item5,item6, item7, item8]

			#return sensorlist

		#print("retrieving sensor data")
		if configure.bme and self.bme.get_sensor_data():# and not configure.simulate:

			sense_data = [self.bme.data.temperature]
			sense_data2 = [self.bme.data.pressure]
			sense_data3 = [self.bme.data.humidity]
			sense_data4 = [self.bme.data.gas_resistance]

			item1 = sense_data + self.temp_info
			item2 = sense_data2 + self.pressure_info
			item3 = sense_data3 + self.humidity_info
			item4 = sense_data4 + self.VOC_info

			sensorlist += [item1, item2, item3, item4]

			#print(sensorlist)
			configure.max_sensors[0] = len(sensorlist)
			#return sensorlist

		if configure.sensehat:# and not configure.simulate:
			sense_data = [sense.get_temperature()]
			sense_data2 = [sense.get_pressure()]
			sense_data3 = [sense.get_humidity()]
			sense_data4 = [sense.get_compass_raw()["x"]]
			sense_data5 = [sense.get_compass_raw()["y"]]
			sense_data6 = [sense.get_compass_raw()["z"]]
			sense_data7 = [sense.get_accelerometer_raw()["x"]]
			sense_data8 = [sense.get_accelerometer_raw()["y"]]
			sense_data9 = [sense.get_accelerometer_raw()["z"]]

			item1 = sense_data + self.temp_info
			item2 = sense_data2 + self.pressure_info
			item3 = sense_data3 + self.humidity_info

			item4 = sense_data4 + self.magnet_infox
			item5 = sense_data5 + self.magnet_infoy
			item6 = sense_data6 + self.magnet_infoz
			item7 = sense_data7 + self.accelerometer_infox
			item8 = sense_data8 + self.accelerometer_infoy
			item9 = sense_data9 + self.accelerometer_infoz
			sensorlist += [item1, item2, item3, item4, item5, item6, item7, item8, item9]


			#return sensorlist

		if configure.amg8833:# and not configure.simulate:
			sense_data = amg.pixels
			item1 = sense_data + self.amg_info

		if configure.envirophat:# and not configure.simulate:
			self.rgb = light.rgb()
			self.analog_values = analog.read_all()
			self.mag_values = motion.magnetometer()
			self.acc_values = [round(x, 2) for x in motion.accelerometer()]

			sense_data = [weather.temperature()]
			sense_data2 = [weather.pressure(unit='hpa')]
			sense_data3 = [light.light()]
			sense_data4 = [self.mag_values[0]]
			sense_data5 = [self.mag_values[1]]
			sense_data6 = [self.mag_values[2]]
			sense_data7 = [self.acc_values[0]]
			sense_data8 = [self.acc_values[1]]
			sense_data9 = [self.acc_values[2]]

			item1 = sense_data + self.temp_info
			item2 = sense_data2 + self.pressure_info
			item3 = sense_data3 + self.humidity_info

			item4 = sense_data4 + self.magnet_infox
			item5 = sense_data5 + self.magnet_infoy
			item6 = sense_data6 + self.magnet_infoz
			item7 = sense_data7 + self.accelerometer_infox
			item8 = sense_data8 + self.accelerometer_infoy
			item9 = sense_data9 + self.accelerometer_infoz
			sensorlist += [item1, item2, item3, item4, item5, item6, item7, item8, item9]

		return sensorlist
