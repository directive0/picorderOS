#!/usr/bin/python

from sense_hat import SenseHat
import time
from objects import *
import math

# instantiate a sensehat object,
sense = SenseHat()

# Initially clears the LEDs once loaded
sense.clear()

# Sets the IMU Configuration.
sense.set_imu_config(True,False,False)

# activates low light conditions to not blind the user.
sense.low_light = True

class Sensor(object):
	def __init__(self):

		self.sensor_name = "Sensehat"
		self.deg_sym = '\xB0'

		#0				1			2		3		4
		#info = (lower range, upper range, unit, symbol)
		self.temp_info = [0,65,"Thermometer",self.deg_sym + "c"]
		self.humidity_info = [20,80,"Hygrometer", "%"]
		self.pressure_info = [260,1260,"Barometer","hPa"]
		self.magnet_infox = [-500,500,"Magnetomer X","G"]
		self.magnet_infoy = [-500,500,"Magnetomer Y","G"]
		self.magnet_infoz = [-500,500,"Magnetomer Z","G"]
		self.accelerometer_infox = [-500,500,"Accelerometer X","g"]
		self.accelerometer_infoy = [-500,500,"Accelerometer Y","g"]
		self.accelerometer_infoz = [-500,500,"Accelerometer Z","g"]
		configure.max_sensors[0] = 9
		configure.sensor_info = self.get()

	def get(self):

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

# function polls the magentometer
def magnetoget():
    sensordict = sense.get_compass_raw()
    return sensordict

# function prints the sensor data to the CLI (obsolete)
def printsensors(sensordict):
    print("Temperature: %s C" % sensordict['temp'])
    print("Temperature from humidity: %s C" % sensordict['humidtemp'])
    print("Temperature from pressure: %s C" % sensordict['pressuretemp'])
    print("Pressure: %s Millibars" % sensordict['pressure'])
    print("Humidity: %s %%rH" % sensordict['humidity'])
    print("North: %s" % sensordict['compass'])

# function clears the 8x8 display.
def clearled():
    sense.clear()  # no arguments defaults to off

# function draws a pattern to the display.
class led_display(object):
    def __init__(self):
        sense.clear()  # no arguments defaults to off
        self.ticks = 0
        self.onoff = 1

    def toggle(self):
        if self.onoff == 1:
            self.onoff = 0
        else:
            self.onoff = 1

    # Function to draw a pretty pattern to the display.
    def animate(self):
        if configure.moire:
            for x in range(8):
                for y in range(8):
                    cx = x + 0.5*math.sin(self.ticks/5.0)
                    cy = y + 0.5*math.cos(self.ticks/3.0)
                    v = math.sin(math.sqrt(1.0*(math.pow(cx, 2.0)+math.pow(cy, 2.0))+1.0)+self.ticks)
              		#v = v + math.sin(x*10.0+self.ticks)
                    v = (v + 1.0)/2.0
                    v = int(v*255.0)
                    sense.set_pixel(x,y,v,v,v)
            self.ticks = self.ticks+1
        else:
            clearled()
