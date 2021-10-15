print("Loading Picorder Library Access and Retrieval System Module")
from objects import *

import json

#	PLARS (Picorder Library Access and Retrieval System) aims to provide a
#	single surface for storing and retrieving data for display in any of the
#	different Picorder screen modes.



#	TO DO:

#   - buffer trimming
#	- JSON api

import os
import numpy
import datetime
from array import *
import pandas as pd
import json


class PLARS(object):

	def __init__(self):

		# PLARS opens a data frame at initialization.
		# If the csv file exists it opens it, otherwise creates it.
		# self.core is used to refer to the archive on disk
		# self.buffer is created as a truncated dataframe for drawing to screen.

		# create buffer
		self.file_path = "data/datacore.csv"


		if os.path.exists(self.file_path):
			if configure.datalog:
				self.core = pd.read_csv(self.file_path)
		else:
			if not os.path.exists("data"):
				os.mkdir("data")
			self.core = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp'])
			self.core.to_csv(self.file_path)


		# Set floating point display to raw, instead of exponent
		pd.set_option('display.float_format', '{:.7f}'.format)

		#create a buffer object to hold screen data
		self.buffer_size = 15
		self.buffer = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp'])

		#create a buffer for wifi/bt data
		self.buffer_em = pd.DataFrame(columns=['ssid','db','max','dsc','sym','dev','timestamp'])


		self.timer = timer()

	# provide status of database (how many entries, how many devices, size, length)
	def status(self):
		pass

	def shutdown(self):
		self.append_to_core(self.buffer)

	# gets the latest CSV file
	def get_core(self):
		datacore = pd.read_csv(self.file_path)
		return datacore

	def merge_with_core(self):
		print("PLARS - merging to core")
		# open the csv
		core = self.get_core()
		copydf = self.buffer.copy()
		newcore = pd.concat([core,copydf]).drop_duplicates().reset_index(drop=True)
		newcore = self.index_by_time(newcore)
		newcore.to_csv(self.file_path,index=False)

	#pends a new set of data to the CSV file.
	def append_to_core(self, data):
		data.to_csv(self.file_path, mode='a', header=False)

	# sets the size of the standard screen buffer
	def set_buffer(self,size):
		print("buffer size set to: ", size)
		self.buffer_size = size


	def update_em(self,data):
		pass
	# updates the data storage file with the most recent sensor values from each
	# initialized sensor
	def update(self,data):

		try:
			# creates a new dataframe for the new information to add to the buffer
			newdata = pd.DataFrame(data,columns=['value','min','max','dsc','sym','dev','timestamp'])

			# appends the new data to the buffer
			self.buffer = self.buffer.append(newdata, ignore_index=True)


			# get buffer size to determine how many rows to remove from the end
			currentsize = len(self.buffer)

			targetsize = self.buffer_size


			# determine difference between buffer and target size
			length = currentsize - targetsize


			# if buffer is larger than target
			if length > 0:
				self.trimbuffer()
				self.timer.logtime()

		except:
			print("Plars failed to update. Dumping data:")
			print(data)
			print("Dumping buffer:")
			print(self.buffer)




	# returns all sensor data in the buffer for the specific sensor (dsc,dev)
	def get_sensor(self,dsc,dev):

		try:
			result = self.buffer.loc[self.buffer['dsc'] == dsc]

			result2 = result.loc[self.buffer['dev'] == dev]
			return result2
		except:
			print("attempting to re-acquire sensor")
			return self.get_sensor(dsc,dev)

	def index_by_time(self,df, ascending = False):
		df.sort_values(by=['timestamp'], ascending = ascending)
		return df

	# return a list of n most recent data from specific sensor defined by key
	def get_recent(self, dsc, dev, num = 5):

		# organize it by time.
		#self.index_by_time(self.buffer)
		# get a dataframe of just the requested sensor
		untrimmed_data = self.get_sensor(dsc,dev)
		# trim it to length (num).
		trimmed_data = untrimmed_data.tail(num)
		# return a list of the values
		return trimmed_data['value'].tolist()


	def trimbuffer(self, save = True):
		# should take the buffer in memory and trim some of it

		# get buffer size to determine how many rows to remove from the end
		currentsize = len(self.buffer)

		targetsize = self.buffer_size


		# determine difference between buffer and target size
		length = currentsize - targetsize


		# make a new dataframe of the most recent data to keep using
		newbuffer = self.buffer.tail(targetsize)
		test1 = newbuffer["timestamp"]


		# slice off the rows outside the buffer and backup to disk
		tocore = self.buffer.head(length)

		self.append_to_core(tocore)

		test2 = tocore["timestamp"]

		# replace existing buffer with new trimmed buffer
		self.buffer = newbuffer



	# return a number of data from a specific sensor at a specific time interval
	def get_timed(self, key, interval = 0, num = 5):
		#load csv file as dataframe
		pass

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
