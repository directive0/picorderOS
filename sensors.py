from objects import *
import time


    # the following is a sensor module for use with the PicorderOS
    print("Loading BME680 Sensor Module")
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

if configure.amg8833:
	import busio
	import board
	import adafruit_amg88xx

	i2c = busio.I2C(board.SCL, board.SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c)



class Sensor(object):
	def __init__(self):


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


		#0				1			2			3			4
		#info = (lower range, upper range, description, symbol)

		if configure.bme:
			self.temp_info = [-40,85,"Temperature (BME)",self.deg_sym + "c"]
			self.humidity_info = [0,100,"Relative Humidity (BME)", "%"]
			self.pressure_info = [300,1100,"Barometric Pressure (BME)","hPa"]
			self.VOC_info = [300,1100,"Air Quality (BME)","hPa"]
		if configure.sensehat:
			self.temp_info = [0,65,"Thermometer (SH)",self.deg_sym + "c"]
			self.humidity_info = [20,80,"Hygrometer (SH)", "%"]
			self.pressure_info = [260,1260,"Barometer (SH)","hPa"]
			self.magnet_infox = [-500,500,"Magnetomer X (SH)","G"]
			self.magnet_infoy = [-500,500,"Magnetomer Y (SH)","G"]
			self.magnet_infoz = [-500,500,"Magnetomer Z (SH)","G"]
			self.accelerometer_infox = [-500,500,"Accelerometer X","g"]
			self.accelerometer_infoy = [-500,500,"Accelerometer Y","g"]
			self.accelerometer_infoz = [-500,500,"Accelerometer Z","g"]
		if configure.amg8833:
			pass



		configure.sensor_info = self.get()


	def get(self):
		#print("retrieving sensor data")
		if configure.bme and self.bme.get_sensor_data():

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

		if configure.sensehat:
			dummyload = [sense.get_temperature()]
			dummyload2 = [sense.get_pressure()]
			dummyload3 = [sense.get_humidity()]
			dummyload4 = [sense.get_compass_raw()["x"]]
			dummyload5 = [sense.get_compass_raw()["y"]]
			dummyload6 = [sense.get_compass_raw()["z"]]
			dummyload7 = [sense.get_accelerometer_raw()["x"]]
			dummyload8 = [sense.get_accelerometer_raw()["y"]]
			dummyload9 = [sense.get_accelerometer_raw()["z"]]

			item1 = dummyload + self.temp_info
			item2 = dummyload2 + self.pressure_info
			item3 = dummyload3 + self.humidity_info

			item4 = dummyload4 + self.magnet_infox
			item5 = dummyload5 + self.magnet_infoy
			item6 = dummyload6 + self.magnet_infoz
			item7 = dummyload7 + self.accelerometer_infox
			item8 = dummyload8 + self.accelerometer_infoy
			item9 = dummyload9 + self.accelerometer_infoz
			sensorlist = [item1, item2, item3, item4, item5, item6, item7, item8, item9]

			return sensorlist
