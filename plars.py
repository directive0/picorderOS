print("Loading Picorder Library Access and Retrieval System Module")
from objects import *

import json

#	PLARS (Picorder Library Access and Retrieval System) aims to provide a
#	single surface for retrieving data for display in any of the different
#	Picorder screen modes.



#	TO DO:
#	pull from saved data
#		All data of a certain sensor
#		All data of a certain time scale
#			Data at set intervals (last day, last hour, last minute)
# 	Incorporate short term memory
# 	JSON api

import os
import numpy
import datetime
from array import *
import pandas as pd
import json




# Create a class that acts as the surface for all interactions with the data core
class PLARS(object):

	def __init__(self):

		# PLARS opens a data frame at initialization.
		# If the csv file exists it opens it, otherwise creates it.
		# self.df is the dataframe for the class

		# create buffer
		self.file_path = "data/datacore.csv"

		if os.path.exists(self.file_path):
			if configure.datalog:
				self.df = pd.read_csv(self.file_path)
		else:
			if not os.path.exists("data"):
				os.mkdir("data")
			self.df = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp'])
			self.df.to_csv(self.file_path)


		# Set floating point display to raw, instead of exponent
		pd.set_option('display.float_format', '{:.7f}'.format)

		#create a buffer object to hold screen data
		self.buffer_size = 15
		self.buffer = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp'])


		self.timer = timer()

	# provide status of database (how many entries, how many devices, size, length)
	def status(self):
		pass

	# gets the latest CSV file
	def get_core(self):
		datacore = pd.read_csv(self.file_path)
		return datacore

	def merge_with_core(self):
		print("PLARS - merging to core")
		# open the csv
		core = self.get_core()
		copydf = self.df.copy()
		newcore = pd.concat([core,copydf]).drop_duplicates().reset_index(drop=True)
		newcore = self.index_by_time(newcore)
		newcore.to_csv(self.file_path,index=False)

	#pends a new set of data to the CSV file.
	def append_to_core(self, data):
		data.to_csv(self.file_path, mode='a', header=False)

	# sets the size of the standard screen buffer
	def set_buffer(self,size):
		self.buffer_size = size

	# updates the data storage file with the most recent sensor values from each
	# initialized sensor
	def update(self,data):

		newdata = pd.DataFrame(data,columns=['value','min','max','dsc','sym','dev','timestamp'])
		self.df = self.df.append(newdata, ignore_index=True)

		if self.timer.timelapsed() > configure.logtime[0] and configure.datalog[0]:
			self.merge_with_core()
			self.timer.logtime()


	# returns all sensor data in the core for the specific sensor (dsc,dev)
	def get_sensor(self,dsc,dev):
		#self.get_core()

		result = self.df.loc[self.df['dsc'] == dsc]

		result2 = result.loc[self.df['dev'] == dev]
		return result2

	def index_by_time(self,df):
		df.sort_values(by=['timestamp'])
		return df

	# return a list of n most recent data from specific sensor defined by key
	def get_recent(self, dsc, dev, num = 5):
		# organize it by time.
		self.index_by_time(self.df)
		# get a dataframe of just the requested sensor
		untrimmed_data = self.get_sensor(dsc,dev)
		# trim it to length (num).
		trimmed_data = untrimmed_data.tail(num)
		# return a list of the values
		return trimmed_data['value'].tolist()

	def trimbuffer(self):
		# should take the buffer in memory and trim some of it
		pass

	# return a number of data from a specific sensor at a specific time interval
	def get_timed(self, key, interval = 0, num = 5):
		#load csv file as dataframe
		pass

	# returns the entire datacore
	def emrg(self):
		self.get_core()
		return self.df

	def convert_epoch(self, time):
		return datetime.datetime.fromtimestamp(time)

	# request accepts a JSON object and returns a JSON response. Obviously not working yet.
	def request(self, request):
		pass

# Creates a plars database object as soon as it is loaded.
plars = PLARS()
