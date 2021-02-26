print("Loading Picorder Library Access and Retrieval System Module")
from objects import *

#	PLARS (Picorder Library Access and Retrieval System) aims to provide a
#	single surface for retrieving data for display in any of the different
#	Picorder screen modes.



#	TO DO:
#	pull from saved data
#		All data of a certain sensor
#		All data of a certain time scale
#			Data at set intervals (last day, last hour, last minute)
# 	Incorporate short term memory

import os.path
import numpy
from array import *
import pandas as pd





# Create a class that acts as the surface for all interactions with the data core
class PLARS(object):

	def __init__(self):

		# PLARS opens a data frame at initialization.
		# If the csv file exists it opens it, otherwise creates it.
		# self.df is the dataframe for the class

		self.file_path = "data/datacore.csv"

		if path.exists(self.file_path):
			self.df = pd.read_csv(self.file_path)
		else:
			if not path.exists("data"):
				os.mkdir("data")
			self.df = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp'])
			self.df.to_csv(self.file_path)

		# Set floating point display to raw, instead of exponent
		pd.set_option('display.float_format', '{:.7f}'.format)

	# gets the latest CSV file
	def get_core(self):
		self.df = pd.read_csv(self.file_path)

	# appends a new set of data to the CSV file.
	def append_to_core(self, data):
		 data.to_csv(self.file_path, mode='a', header=False)

	# updates the data storage file with the most recent sensor fragments
	def update(self,data):
		newdata = pd.DataFrame(data,columns=['value','min','max','dsc','sym','dev','timestamp'])
		print(newdata)
		self.append_to_core(newdata)

	# returns the last "num"ber of sensor readings, filtered by description and device
	def get_sensor(self,dsc,dev,num):
		sensor_data = self.df[(self.df['dsc'] == dsc) & self.df['dev'] == dev]
		return sensor_data.tail(num)

	def index_by_time(self):
		self.df.sort_values(by=['timestamp'])

	# return a "num"ber of most recent data from specific sensor (dsc,dev)
	def get_recent(self, dsc, dev, num):
		self.get_core()
		self.index_by_time()
		self.get_sensor(dsc,dev,num)


	# return a number of data from a specific sensor at a specific time interval
	def get_timed(self, key, interval = 0, num = 5):
		#load csv file as dataframe
		pass

	# returns the entire datacore
	def emrg(self):
		self.get_core()
		return self.df
