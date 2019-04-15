#!/usr/bin/python

## This file fetches CPU load values and relates them to the caller. This file is used in place of the

#from __future__ import division
#import copy
#import math
#import sys
#import os
import psutil
from filehandling import *
#import time

from objects import *


class Sensor(object):
	def __init__(self):
		self.sensor_name = "CPU Sensor Dummy"
		self.deg_sym = '\xB0'

		#0 (reading)		1			2			3		4
		#info = 		(lower range, upper range, unit, symbol)
		self.infoa = [0,100,"CPU Percent","%"]
		self.infob = [0,float(psutil.virtual_memory().total) / 1024,"Virtual Memory", ""]
		self.infoc = [0,100000,"Bytes Sent", ""]
		self.VOC_info = []

		self.filehandler = datalog()


	def get(self):
		dummyload = [float(psutil.cpu_percent())]
		dummyload2 = [float(psutil.virtual_memory().available) / 1024]
		dummyload3 = [float(psutil.net_io_counters().bytes_sent) / (1024 * 64)]

		item1 = dummyload + self.infoa
		item2 = dummyload2 + self.infob
		item3 = dummyload3 + self.infoc

		sensorlist = [item1, item2, item3]
		#sensorlist = [[dummyload,self.infoa],[dummyload2,self.infob],[dummyload3,self.infoc]]

		#self.filehandler.write_data(item1)
		#self.filehandler.write_data(item2)
		#self.filehandler.write_data(item3)
		#self.filehandler.write_data()
		return sensorlist

#
# def sensorget():
# 	statusram = psutil.virtual_memory()
#
# 	sensordict = {'humidity': 0, 'temp':0, 'humidtemp':0, 'pressuretemp':0,'pressure':0,'compass':0}
# 	sensordict['humidity'] = psutil.cpu_percent()
#
# 	if psutil.OSX:
# 		#print("think mac")
# 		sensordict['temp'] = (psutil.net_io_counters().bytes_sent,0,100000000000)
# 	else:
# 		#print("think other")
# 		sensordict['temp'] = psutil.sensors_temperatures()['acpitz'][0].current
#
# 	#sensordict['humidtemp'] = psutil.cpu_percent()
# 	#sensordict['pressuretemp'] = psutil.cpu_percent()
# 	#sensordict['pressure'] = translate(statusram.percent, 0, 100, 260, 1260)
# 	#psutil.disk_usage('/').percent + 260
# 	#sensordict['compass'] = {"x" : 2, "y" : 2, "z" : 3}
# 	return sensordict
#
# def printscreen(sensordict):
# 	print("Temperature: %s C" % sensordict['temp'])
# 	print("Temperature from humidity: %s C" % sensordict['humidtemp'])
# 	print("Temperature from pressure: %s C" % sensordict['pressuretemp'])
# 	print("Pressure: %s Millibars" % sensordict['pressure'])
# 	print("Humidity: %s %%rH" % sensordict['humidity'])
# 	print("North: %s" % sensordict['compass'])
