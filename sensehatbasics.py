#!/usr/bin/python

import math
from sense_hat import SenseHat 
import time

# instantiate a sensehat object, 
sense = SenseHat()

# Initially clears the LEDs once loaded
sense.clear()

# Sets the IMU Configuration.
sense.set_imu_config(True,False,False)

# activates low light conditions to not blind the user.
sense.low_light = True


# function polls the sensors and drops the values into a neat little dictionary so it can be easily parsed.

def sensorget():
    sensordict = {'humidity': 0, 'temp':0, 'humidtemp':0, 'pressuretemp':0,'pressure':0,'compass':0} 
    sensordict['humidity'] = sense.get_humidity()
    sensordict['temp'] = sense.get_temperature()
    sensordict['humidtemp'] = sense.get_temperature_from_humidity()
    sensordict['pressuretemp'] = sense.get_temperature_from_pressure()
    sensordict['pressure'] = sense.get_pressure()
    sensordict['compass'] = sense.get_compass()
    magnetdict = sense.get_compass_raw()
    sensordict.update(magnetdict)
    
    return sensordict

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
        if self.onoff == 1:
            for x in range(8):
                for y in range(8):
                    cx = x + 0.5*math.sin(self.ticks/5.0)
                    cy = y + 0.5*math.cos(self.ticks/3.0)
                    v = math.sin(math.sqrt(1.0*(math.pow(cx, 2.0)+math.pow(cy, 2.0))+1.0)+self.ticks)
              #      v = v + math.sin(x*10.0+self.ticks)
                    v = (v + 1.0)/2.0
                    v = int(v*255.0)
                    sense.set_pixel(x,y,v,v,v)
            self.ticks = self.ticks+1
        else:
            clearled()



