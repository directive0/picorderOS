#!/usr/bin/python
import time
import csv
import os

# Sensor data fragment array anatomy:
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
			print("file found")
		except FileNotFoundError:
			initial = open('datalog.csv', mode='w', newline='')
			initial_write = csv.writer(initial, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
			initial_write.writerow(['Reading']+['Lower Range']+['Upper Range']+['Unit']+['Symbol'])
			#+['Safe high']+["Sensor name"]+['Description']+["Time Index"])
			print("file written")
		#self.d1 = str((time.strftime("%d-%m-%Y")))
		#file = open("log/" + self.d1 + '-loggedvals.csv', 'a')

		#file.write("Date, Time, Humidity, Pressure, Temperature, MagX, MagY, MagZ" + "\r")

	def read_data(self, lines = 1):
		with open('datalog.csv', newline='') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
			for row in spamreader:
				pass
				#print(', '.join(row))

	def write_data(self, fragment = (100,0,100,"CPU Percent","%")):
		#with open('datalog.csv', 'w', newline='') as csvfile:
		with open('datalog.csv', 'a', newline='') as csvfile:
				print(time.time())
				datawriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
				datawriter.writerow([fragment[0]]+[fragment[1]]+[fragment[2]]+[fragment[3]]+[fragment[4]])
				#datawriter.writerow([randoval]+["°c"]+[-40]+[200]+[10]+[24]+["BME680"]+["Ambient Temperature"])
				print("writing")

		#self.d1 = str((time.strftime("%d-%m-%Y")))
		#file = open("log/" + self.d1 + '-loggedvals.csv', 'a')
		#self.t = str((time.strftime("%H:%M:%S")))
		#self.d = str((time.strftime("%d/%m/%Y")))
		#self.temp = str(sensors['temp'])
		#self.press = str(sensors['pressure'])
		#self.humid = str(sensors['humidity'])
		#self.x = str(sensors['x'])
		#self.y = str(sensors['y'])
		#self.z = str(sensors['z'])
##        file.write("/log/" + self.d + "," + self.t + "," + str(sensors['humidity']) + "," + str(sensors['pressure']) + str(sensors['temp']) + "\r")
		#file.write( self.d + "," + self.t + "," + self.humid + "," + self.press + "," + self.temp + ","+ self.x + "," + self.y + "," + self.z + "\r")
		#print('logged a value to file!' + "\r")
		#print( "Time: " + self.d + " Date: " + self.t + " Humdity:" + self.humid + " Pressure:" + self.press + " Temperature:" + self.temp + " X:"+ self.x + " Y:" + self.y + " Z:" + self.z + "\r")

	def end_file():
		pass
		#file.write("END OF LOG")

new = datalog()
new.write_data()
new.read_data()
