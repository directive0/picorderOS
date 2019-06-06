#!/usr/bin/python

#	This file fetches CPU load values and relates them to the caller.
#	It is used in place of the various sensor modules to demonstrate functionality.

import psutil

from objects import *


class Sensor(object):
	def __init__(self):
		self.sensor_name = "CPU Sensor Dummy"
		self.deg_sym = '\xB0'

		#0 (reading)		1			2			3		4
		#info = 		(lower range, upper range, unit, symbol)
		self.infoa = [0,100,"CPU Percent","%"]
		self.infob = [0,float(psutil.virtual_memory().total) / 1024,"Virtual Memory", "b"]
		self.infoc = [0,100000,"Bytes Sent", "b"]
		self.infod = [0,100000,"Bytes Received", "b"]
		self.VOC_info = []
		configure.max_sensors[0] = 4
		configure.sensor_info = self.get()
		#self.filehandler = datalog()


	def get(self):

		dummyload = [float(psutil.cpu_percent())]
		dummyload2 = [float(psutil.virtual_memory().available) * 0.0000001]
		dummyload3 = [float(psutil.net_io_counters().bytes_sent) * 0.00001]
		dummyload4 = [float(psutil.net_io_counters().bytes_recv) * 0.00001]

		item1 = dummyload + self.infoa
		item2 = dummyload2 + self.infob
		item3 = dummyload3 + self.infoc
		item4 = dummyload4 + self.infod


		sensorlist = [item1, item2, item3, item4]

		return sensorlist
