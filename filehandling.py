#!/usr/bin/python

print("Loading File Handling Module")

#import time
import datetime
#from datetime import time
import csv
import os
from objects import *

# Sensor data fragment array anatomy (All of this is wrong now):
# [0] - reading, in raw float
# [1] - unit as a string (°c, °f, etc)
# [2] - low end of sensor
# [3] - high end of sensor
# [4] - safe zone low
# [5] - safe zone high
# [6] - name of sensor
# [7] - arbitrary description
# [8] - Sensor ID
# [9] - time index

# example data fragment

#(32.1, "°c", -40, 200, 10, 24, "BME 680", "Ambient Temperature", 0)

class datalog(object):

	def __init__(self):
		try:
			self.attempt = open('datalog.csv', newline='')
			print("File Handler - Existing file found")
		except FileNotFoundError:
			initial = open('datalog.csv', mode='w', newline='')
			initial_write = csv.writer(initial, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
			#initial_write.writerow(['Reading']+['Lower Range']+['Upper Range']+['Unit']+['Symbol'])
			#+['Safe high']+["Sensor name"]+['Description']+["Time Index"])
			print("File Handler - New file created")

		self.sampletimer = timer()
		#self.d1 = str((time.strftime("%d-%m-%Y")))
		#file = open("log/" + self.d1 + '-loggedvals.csv', 'a')

		#file.write("Date, Time, Humidity, Pressure, Temperature, MagX, MagY, MagZ" + "\r")

	def read_data(self, lines = 1):
		print("File Handler - Reading datalog")
		with open('datalog.csv', newline='') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')

			cursor = 0
			selection = []
			timenow = datetime.datetime.now().time()
			for row in reversed(list(spamreader)):

				print(row[0].split(",")[0])
				thistime = datetime.time(10,10,10,10)
				print(thistime)
				break

				pass
				#print(', '.join(row))


	def write_data(self, fragment):
		#with open('datalog.csv', 'w', newline='') as csvfile:
		if self.sampletimer.timelapsed() > configure.samplerate[0] and configure.logdata:
			print("File Handler - Writing fragment to datalog")
			with open('datalog.csv', 'a', newline='') as csvfile:
					print(time.time())
					datawriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

					row = [datetime.datetime.now().time()]
					for i in range(len(fragment)):
						row.append(fragment[i][0])
					#datawriter.writerow([fragment[0]]+[fragment[1]]+[fragment[2]]+[fragment[3]]+[fragment[4]])
					datawriter.writerow(row)
			self.sampletimer.logtime()
			self.read_data()
	def end_file():
		pass
		#file.write("END OF LOG")

#new = datalog()
#new.write_data()
#new.read_data()
