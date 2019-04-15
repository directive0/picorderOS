#!/usr/bin/python


import pyowm
import time


def sensorget():
   sensordict = {'humidity': 0, 'temp':0, 'humidtemp':0, 'pressuretemp':0,'pressure':0,'compass':0} 

   owm = pyowm.OWM('f8c43bbd601d39c177afabec2d050d04')
   observation = owm.weather_at_place('Toronto,CA')
   w = observation.get_weather()
   temp = w.get_temperature('celsius')
   humidity = w.get_humidity()
   pressure = w.get_pressure()
   timelast = timenow
    

   sensordict['humidity'] = humidity
   sensordict['temp'] = temp['temp']
   sensordict['pressure'] = pressure['press']

   return sensordict

def printscreen(sensordict):
   print("Temperature: %s C" % sensordict['temp'])
   print("Temperature from humidity: %s C" % sensordict['humidtemp'])
   print("Temperature from pressure: %s C" % sensordict['pressuretemp'])
   print("Pressure: %s Millibars" % sensordict['pressure'])
   print("Humidity: %s %%rH" % sensordict['humidity'])
   print("North: %s" % sensordict['compass'])

