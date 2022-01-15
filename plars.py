print("Loading Picorder Library Access and Retrieval System Module")
from objects import *

import json

#	PLARS (Picorder Library Access and Retrieval System) aims to provide a
#	single surface for storing and retrieving data for display in any of the
#	different Picorder screen modes.




#	TO DO:
#	- JSON api

import os
import numpy
import datetime
from array import *
import pandas as pd
import json

import threading

class PLARS(object):

	def __init__(self):

		# add a lock to avoid race conditions
		self.lock = threading.Lock()

		# PLARS opens a data frame at initialization.
		# If the csv file exists it opens it, otherwise creates it.
		# self.core is used to refer to the archive on disk
		# self.buffer is created as a truncated dataframe for drawing to screen.

		# create buffer
		self.file_path = "data/datacore.csv"

		if configure.recall[0]:
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
		self.buffer_em = pd.DataFrame(columns=['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp'])


		self.timer = timer()


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

	# returns a list of every EM transciever that was discovered last scan.
	def get_recent_em_list(self):

		# set the thread lock so other threads are unable to add data
		self.lock.acquire()

		# get the most recent ssids discovered
		recent_em = self.get_em_recent()

		# sort it by signal strength
		recent_em.sort_values(by=['signal'], ascending = False)

		# release the thread lock.
		self.lock.release()

		return recent_em.values.tolist()

	def get_top_em_info(self):

		#find the most recent timestamp to limit focus
		focus = self.get_em_recent()

		# find most powerful signal of the most recent transciever data
		db_column = focus["signal"]
		strongest = db_column.astype(int).max()

		# Identify the SSID of the strongest signal.
		self.identity = focus.loc[focus['signal'] == strongest]

		# Return the SSID of the strongest signal as a list.
		return self.identity.values.tolist()

	def get_em_recent(self):
		# find the most recent timestamp
		time_column = self.buffer_em["timestamp"]
		most_recent = time_column.max()

		#limit focus to data from that timestamp
		return self.buffer_em.loc[self.buffer_em['timestamp'] == most_recent]

	def get_top_em_history(self, no = 5):
		# returns a list of Db values for whatever SSID is currently the strongest.
		# suitable to be fed into pilgraph for graphing.

		# set the thread lock so other threads are unable to add data
		self.lock.acquire()

		#limit focus to data from that timestamp
		focus = self.get_em_recent()

		# find most powerful signal
		db_column = focus["signal"]
		strongest = db_column.astype(int).max()

		# Identify the SSID of the strongest signal.
		self.identity = focus.loc[focus['signal'] == strongest]


		# prepare markers to pull data
		# Wifi APs can have the same name and different paramaters
		# I use MAC and frequency to individualize a signal
		dev = self.identity["dev"].iloc[0]
		frq = self.identity["frequency"].iloc[0]


		# release the thread lock.
		self.lock.release()

		return self.get_recent_em(dev,frq, num = no)


	def update_em(self,data):
		#print("Updating EM Dataframe:")

		newdata = pd.DataFrame(data, columns=['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp'])


		# sets/requests the thread lock to prevent other threads reading data.
		self.lock.acquire()


		# appends the new data to the buffer
		self.buffer_em = self.buffer_em.append(newdata, ignore_index=True)


		self.lock.release()


	# updates the data storage file with the most recent sensor values from each
	# initialized sensor
	def update(self,data):

		# sets/requests the thread lock to prevent other threads reading data.
		self.lock.acquire()


		#listbuilder:
		fragdata = []

		for fragment in data:
			item = fragment.get()
			fragdata.append(item)


		# creates a new dataframe to add new data to
		newdata = pd.DataFrame(fragdata, columns=['value','min','max','dsc','sym','dev','timestamp'])

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

		# release the thread lock for other threads
		self.lock.release()

	def get_em(self,dev,frequency):
		result = self.buffer_em.loc[self.buffer_em['dev'] == dev]
		result2 = result.loc[result["frequency"] == frequency]

		return result2

	# returns all sensor data in the buffer for the specific sensor (dsc,dev)
	def get_sensor(self,dsc,dev):

		result = self.buffer[self.buffer["dsc"] == dsc]

		result2 = result.loc[result['dev'] == dev]

		return result2


	def index_by_time(self,df, ascending = False):
		df.sort_values(by=['timestamp'], ascending = ascending)
		return df


	# return a list of n most recent data from specific ssid defined by keys
	def get_recent_em(self, dev, frequency, num = 5):

		# get a dataframe of just the requested sensor
		untrimmed_data = self.get_em(dev,frequency)

		# trim it to length (num).
		trimmed_data = untrimmed_data.tail(num)

		# return a list of the values
		return trimmed_data['signal'].tolist()


	# return a list of n most recent data from specific sensor defined by keys
	def get_recent(self, dsc, dev, num = 5):

		# set the thread lock so other threads are unable to add sensor data
		self.lock.acquire()

		# get a dataframe of just the requested sensor
		untrimmed_data = self.get_sensor(dsc,dev)



		# trim it to length (num).
		trimmed_data = untrimmed_data.tail(num)



		# return a list of the values
		result = trimmed_data['value'].tolist()

		# release the thread lock.
		self.lock.release()

		return result


	def trimbuffer(self, save = True):
		# should take the buffer in memory and trim some of it

		# get buffer size to determine how many rows to remove from the end
		currentsize = len(self.buffer)
		targetsize = self.buffer_size

		# determine difference between buffer and target size
		length = currentsize - targetsize

		# make a new dataframe of the most recent data to keep using
		newbuffer = self.buffer.tail(targetsize)

		# slice off the rows outside the buffer and backup to disk
		tocore = self.buffer.head(length)

		if configure.recall[0]:
			self.append_to_core(tocore)

		# replace existing buffer with new trimmed buffer
		self.buffer = newbuffer


	def emrg(self):
		self.get_core()
		return self.df

	def convert_epoch(self, time):
		return datetime.datetime.fromtimestamp(time)

# Creates a plars database object as soon as it is loaded.
plars = PLARS()
