from objects import *
import time



# the following is a sensor module for use with the PicorderOS
print("Loading Unified Sensor Module")

if not configure.pc:
	import os

if configure.bme:
	#import bme680

	#Using adafruit circuitpython.
	import board
	from busio import I2C
	import adafruit_bme680



if configure.sensehat:
	# instantiates and defines paramteres for the sensehat

	from sense_hat import SenseHat

	# instantiate a sensehat object,
	sense = SenseHat()

	# Initially clears the LEDs once loaded
	sense.clear()

	# Sets the IMU Configuration.
	sense.set_imu_config(True,False,False)



if configure.amg8833: # and not configure.simulate:
	import busio
	import board
	import adafruit_amg88xx

	i2c = busio.I2C(board.SCL, board.SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c)

if configure.envirophat:
	from envirophat import light, weather, motion, analog

# support for the MLX90614 IR Thermo
if configure.ir_thermo:
	import board
	import busio as io
	import adafruit_mlx90614

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
		#0				1			2		3		4
		#info = (lower range, upper range, unit, symbol)


		if configure.system_vitals:
			self.step = 0.0
			self.step2 = 0.0
			self.steptan = 0.0

			self.cputemp = [0,100,"CPU Temp",self.deg_sym + "c","Raspberry Pi"]
			self.infoa = [0,100,"CPU Percent","%","Raspberry Pi"]
			self.infob = [0,float(psutil.virtual_memory().total) / 1024,"Virtual Memory", "b","Raspberry Pi"]
			self.infoc = [0,100000,"Bytes Sent", "b","Raspberry Pi"]
			self.infod = [0,100000,"Bytes Received", "b","Raspberry Pi"]
			self.infoe = [-100,100,"Sine Wave", "","Raspberry Pi"]
			self.infof = [-500,500,"Tangent Wave", "","Raspberry Pi"]
			self.infog = [-100,100,"Cos Wave", "","Raspberry Pi"]
			self.infoh = [-100,100,"Sine Wave2", "","Raspberry Pi"]



		if configure.sensehat:
			self.ticks = 0
			self.onoff = 1
			# activates low light conditions to not blind the user.
			sense.low_light = True
			# instantiate a sensehat object,
			self.sense = SenseHat()
			# Initially clears the LEDs once loaded
			self.sense.clear()
			# Sets the IMU Configuration.
			self.sense.set_imu_config(True,False,False)
			# activates low light conditions to not blind the user.
			self.sense.low_light = True
			self.temp_info = [0,65,"Thermometer (SH)",self.deg_sym + "c"]
			self.humidity_info = [20,80,"Hygrometer", "%", "SenseHat"]
			self.pressure_info = [260,1260,"Barometer","hPa", "SenseHat"]
			self.magnet_infox = [-500,500,"Magnet X","G", "SenseHat"]
			self.magnet_infoy = [-500,500,"Magnet Y","G", "SenseHat"]
			self.magnet_infoz = [-500,500,"Magnet Z","G", "SenseHat"]
			self.accelerometer_infox = [-500,500,"Accel X","g", "SenseHat"]
			self.accelerometer_infoy = [-500,500,"Accel Y","g", "SenseHat"]
			self.accelerometer_infoz = [-500,500,"Accel Z","g", "SenseHat"]


		if configure.amg8833: # and not configure.simulate:
			self.amg_info = [0,80,"IR [amg]",self.deg_sym + "c"]


		if configure.ir_thermo:
			i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
			self.mlx = adafruit_mlx90614.MLX90614(i2c)
			self.ir_thermo_ambient = [0,80,"IR ambient [mlx]",self.deg_sym + "c"]
			self.ir_thermo_object = [0,80,"IR object [mlx]",self.deg_sym + "c"]

		if configure.envirophat: # and not configure.simulate:

			self.rgb = light.rgb()
			self.analog_values = analog.read_all()
			self.mag_values = motion.magnetometer()
			self.acc_values = [round(x, 2) for x in motion.accelerometer()]

			self.temp_info = [0,65,"Thermometer",self.deg_sym + "c","Envirophat"]
			self.humidity_info = [20,80,"Hygrometer", "%","Envirophat"]
			self.pressure_info = [260,1260,"Barometer","hPa","Envirophat"]
			self.magnet_infox = [-500,500,"Magnetomer X","G","Envirophat"]
			self.magnet_infoy = [-500,500,"Magnetomer Y","G","Envirophat"]
			self.magnet_infoz = [-500,500,"Magnetomer Z","G","Envirophat"]
			self.accelerometer_infox = [-500,500,"Accelerometer X (EP)","g","Envirophat"]
			self.accelerometer_infoy = [-500,500,"Accelerometer Y (EP)","g","Envirophat"]
			self.accelerometer_infoz = [-500,500,"Accelerometer Z (EP)","g","Envirophat"]


		if configure.amg8833:
			self.amg_info = [0,80,"IR Thermal Array",self.deg_sym + "c"]

		self.sensor_data = []
		for i in range(configure.max_sensors[0]):
			self.sensor_data.append()


		if configure.bme:
			# Create library object using our Bus I2C port
			i2c = I2C(board.SCL, board.SDA)
			self.bme = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)

			self.temp_info = [-40,85,"Thermometer",self.deg_sym + "c", "BME680"]
			self.humidity_info = [0,100,"Hygrometer", "%", "BME680"]
			self.pressure_info = [300,1100,"Barometer","hPa", "BME680"]
			self.VOC_info = [300000,1100000,"VOC","KOhm", "BME680"]

		configure.sensor_info = self.get()

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
		timestamp = [time.time()]

		if configure.bme:

			sense_data = [self.bme.temperature]
			sense_data2 = [self.bme.pressure]
			sense_data3 = [self.bme.humidity]
			sense_data4 = [self.bme.gas / 1000]

			item1 = sense_data + self.temp_info + timestamp
			item2 = sense_data2 + self.pressure_info + timestamp
			item3 = sense_data3 + self.humidity_info + timestamp
			item4 = sense_data4 + self.VOC_info + timestamp

			sensorlist += [item1, item2, item3, item4]

		if configure.sensehat:# and not configure.simulate:

			if configure.moire:
				for x in range(8):
					for y in range(8):
						# it's this cool plasma effect from demoscene I stole from
						# somewhere.
						cx = x + 0.5*math.sin(self.ticks/5.0)
						cy = y + 0.5*math.cos(self.ticks/3.0)
						v = math.sin(math.sqrt(1.0*(math.pow(cx, 2.0)+math.pow(cy, 2.0))+1.0)+self.ticks)
						#v = v + math.sin(x*10.0+self.ticks)
						v = (v + 1.0)/2.0
						v = int(v*255.0)
						sense.set_pixel(x,y,v,v,v)
				self.ticks = self.ticks+1
			else:
				sense.clear()  # no arguments defaults to off


			sense_data = [sense.get_temperature()]
			sense_data2 = [sense.get_pressure()]
			sense_data3 = [sense.get_humidity()]
			sense_data4 = [sense.get_compass_raw()["x"]]
			sense_data5 = [sense.get_compass_raw()["y"]]
			sense_data6 = [sense.get_compass_raw()["z"]]
			sense_data7 = [sense.get_accelerometer_raw()["x"]]
			sense_data8 = [sense.get_accelerometer_raw()["y"]]
			sense_data9 = [sense.get_accelerometer_raw()["z"]]

			item1 = sense_data + self.temp_info + timestamp
			item2 = sense_data2 + self.pressure_info + timestamp
			item3 = sense_data3 + self.humidity_info + timestamp

			item4 = sense_data4 + self.magnet_infox + timestamp
			item5 = sense_data5 + self.magnet_infoy + timestamp
			item6 = sense_data6 + self.magnet_infoz + timestamp
			item7 = sense_data7 + self.accelerometer_infox + timestamp
			item8 = sense_data8 + self.accelerometer_infoy + timestamp
			item9 = sense_data9 + self.accelerometer_infoz + timestamp
			sensorlist += [item1, item2, item3, item4, item5, item6, item7, item8, item9]

		if configure.amg8833:
			sense_data = amg.pixels
			item1 = sense_data + self.amg_info + timestamp

		if configure.envirophat:
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

			item1 = sense_data + self.temp_info + timestamp
			item2 = sense_data2 + self.pressure_info + timestamp
			item3 = sense_data3 + self.humidity_info + timestamp

			item4 = sense_data4 + self.magnet_infox + timestamp
			item5 = sense_data5 + self.magnet_infoy + timestamp
			item6 = sense_data6 + self.magnet_infoz + timestamp
			item7 = sense_data7 + self.accelerometer_infox + timestamp
			item8 = sense_data8 + self.accelerometer_infoy + timestamp
			item9 = sense_data9 + self.accelerometer_infoz + timestamp
			sensorlist += [item1, item2, item3, item4, item5, item6, item7, item8, item9]

		# provides the basic definitions for the system vitals sensor readouts
		if configure.system_vitals:

			if not configure.pc:
				res = os.popen("vcgencmd measure_temp").readline()
				t = float(res.replace("temp=","").replace("'C\n",""))
			else:
				t = float(0)

			systemtemp = [t]
			dummyload = [float(psutil.cpu_percent())]
			dummyload2 = [float(psutil.virtual_memory().available) * 0.0000001]
			dummyload3 = [float(psutil.net_io_counters().bytes_sent) * 0.00001]
			dummyload4 = [float(psutil.net_io_counters().bytes_recv) * 0.00001]
			dummyload5 = [float(self.sin_gen()*100)]
			dummyload6 = [float(self.tan_gen()*100)]
			dummyload7 = [float(self.cos_gen()*100)]
			dummyload8 = [float(self.sin2_gen()*100)]

			item0 = systemtemp + self.cputemp + timestamp
			item1 = dummyload + self.infoa + timestamp
			item2 = dummyload2 + self.infob + timestamp
			item3 = dummyload3 + self.infoc + timestamp
			item4 = dummyload4 + self.infod + timestamp
			item5 = dummyload5 + self.infoe + timestamp
			item6 = dummyload6 + self.infof + timestamp
			item7 = dummyload7 + self.infog + timestamp
			item8 = dummyload8 + self.infoh + timestamp

			sensorlist += [item0, item1, item2, item3, item4, item5,item6, item7, item8]
		configure.max_sensors[0] = len(sensorlist)

		return sensorlist

class MLX90614():

	MLX90614_RAWIR1=0x04
	MLX90614_RAWIR2=0x05
	MLX90614_TA=0x06
	MLX90614_TOBJ1=0x07
	MLX90614_TOBJ2=0x08

	MLX90614_TOMAX=0x20
	MLX90614_TOMIN=0x21
	MLX90614_PWMCTRL=0x22
	MLX90614_TARANGE=0x23
	MLX90614_EMISS=0x24
	MLX90614_CONFIG=0x25
	MLX90614_ADDR=0x0E
	MLX90614_ID1=0x3C
	MLX90614_ID2=0x3D
	MLX90614_ID3=0x3E
	MLX90614_ID4=0x3F

	comm_retries = 5
	comm_sleep_amount = 0.1

	def __init__(self, address=0x5a, bus_num=1):
		self.bus_num = bus_num
		self.address = address
		self.bus = smbus.SMBus(bus=bus_num)

	def read_reg(self, reg_addr):
		err = None
		for i in range(self.comm_retries):
			try:
				return self.bus.read_word_data(self.address, reg_addr)
			except IOError as e:
				err = e
				#"Rate limiting" - sleeping to prevent problems with sensor
				#when requesting data too quickly
				sleep(self.comm_sleep_amount)
		#By this time, we made a couple requests and the sensor didn't respond
		#(judging by the fact we haven't returned from this function yet)
		#So let's just re-raise the last IOError we got
		raise err

	def data_to_temp(self, data):
		temp = (data*0.02) - 273.15
		return temp

	def get_amb_temp(self):
		data = self.read_reg(self.MLX90614_TA)
		return self.data_to_temp(data)

	def get_obj_temp(self):
		data = self.read_reg(self.MLX90614_TOBJ1)
		return self.data_to_temp(data)
