#!/usr/bin/python

#	This file fetches CPU load values and relates them to the caller.
#	It is used in place of the various sensor modules to demonstrate functionality.
print("Loading GetCPU/sensor dummy")

import psutil
import math


from objects import *

if configure.logdata[0]:
	from filehandling import *


class Sensor(object):
	def __init__(self):
		self.step = 0.0
		self.step2 = 0.0
		self.steptan = 0.0


		self.sensor_name = "CPU Sensor Dummy"
		self.deg_sym = '\xB0'

		#0 (reading)		1			2			3		4
		#info = 		(lower range, upper range, desc, symbol)
		self.infoa = [0,100,"CPU Percent","%"]
		self.infob = [0,float(psutil.virtual_memory().total) / 1024,"Virtual Memory", "b"]
		self.infoc = [0,100000,"Bytes Sent", "b"]
		self.infod = [0,100000,"Bytes Received", "b"]
		self.infoe = [-100,100,"Sine Wave", ""]
		self.infof = [-500,500,"Tangent Wave", ""]
		self.infog = [-100,100,"Cos Wave", ""]
		self.infoh = [-100,100,"Sine Wave2", ""]
		self.VOC_info = []
		#configure.max_sensors[0] = 8

		if configure.logdata[0]:
			self.filehandler = datalog()

		configure.sensor_info = self.get()




	def get(self):

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

		sensorlist = [item1, item2, item3, item4, item5,item6, item7, item8]

		if configure.logdata[0]:
			self.filehandler.write_data(sensorlist)

		configure.max_sensors[0] = len(sensorlist)
		return sensorlist

	def sin_gen(self, offset = 0):
		wavestep = math.sin(self.step)
		self.step += .1
		return wavestep

	def sin2_gen(self, offset = 0):
		wavestep = math.sin(self.step2)
		self.step2 += .05
		return wavestep

	def cos_gen(self, offset = 0):
		wavestep = math.cos(self.step)
		self.step += .1
		return wavestep


	def tan_gen(self):
		wavestep = math.tan(self.steptan)
		self.steptan += .1
		#print(wavestep)
		return wavestep
