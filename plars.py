print("Loading Picorder Library Access and Retrieval System Module")
from objects import *
from multiprocessing import Process,Queue,Pipe


import json

#	PLARS (Picorder Library Access and Retrieval System) aims to provide a
#	single surface for storing and retrieving data for display in any of the
#	different Picorder screen modes.

import os
import numpy
import datetime
from array import *
import pandas as pd
import json
import contextlib
import threading

# Broken out functions for use with processing:

# organizes and returns a list of data as a multiprocess.
def get_recent_proc(conn,buffer,dsc,dev,num):

	result = buffer[buffer["dsc"] == dsc]


	untrimmed_data = result.loc[result['dev'] == dev]

	# trim it to length (num).
	trimmed_data = untrimmed_data.tail(num)

	# return a list of the values
	values = trimmed_data['value'].tolist()
	times = trimmed_data['timestamp'].tolist()
	result = [values,times]

	conn.put(result)

# updates the dataframe buffer as a multiprocess.
def update_proc(conn,buffer,data,cols):
	#listbuilder:
	fragdata = []
	
	for fragment in data:
		#
		item = fragment.get()
		fragdata.append(item)


	# creates a new dataframe to add new data to
	newdata = pd.DataFrame(fragdata, columns=cols)

	result = join_dataframes(buffer,newdata)


	conn.put(result)


# updates the dataframe buffer as a multiprocess.
def update_em_proc(conn,buffer,data,cols):

	# creates a new dataframe to add new data to
	newdata = pd.DataFrame(data, columns=cols)


	result = join_dataframes(buffer,newdata)

	conn.put(result)

def join_dataframes(buffer,newdata):
		# if the buffer isn't empty
	if len(buffer) > 0:

		# if the new data frame isn't empty
		if len(newdata) > 0:
			# appends the new data to the buffer

			result = pd.concat([buffer,newdata]).drop_duplicates().reset_index(drop=True)

		else:
			result = buffer
	#if the buffer IS EMPTY
	else:
		# if the new data frame isn't empty
		if len(newdata) > 0:
			result = newdata
			#just make the result the new data (nothing to join yet)
		else:
			result = buffer
	
	return result

class PLARS(object):

	def __init__(self):

		# add a lock to avoid race conditions
		self.lock = threading.Lock()

		# PLARS opens a data frame at initialization.
		# If the csv file exists it opens it, otherwise creates it.
		# self.core is used to refer to the archive on disk for sensor data
		# self.em_core is used to refer to the archive on disk for EM data
		# self.buffer is created as a truncated dataframe for drawing to screen.
		# self.buffer_em is created as a truncated dataframe for drawing  to screen.
			
		# create buffer
		self.file_path = "data/datacore.csv"
		self.em_file_path = "data/em_datacore.csv"



		if configure.datalog[0]:

			# make sure the data folder exist
			if not os.path.exists("data"):
					os.mkdir("data")

			# check if a datacore csv file exists
			if os.path.exists(self.file_path):
				self.core = pd.read_csv(self.file_path)
			else:
				self.core = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])
				self.core.to_csv(self.file_path)

			# check if an EM datacore csv file exists
			if os.path.exists(self.em_file_path):
				self.em_core = pd.read_csv(self.em_file_path)
			else:
				self.em_core = pd.DataFrame(columns=['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude'])
				self.em_core.to_csv(self.em_file_path)



		# Set floating point display to raw, instead of exponent
		pd.set_option('display.float_format', '{:.7f}'.format)

		#create a buffer object to hold screen data
		self.buffer = pd.DataFrame(columns=['value','min','max','dsc','sym','dev','timestamp','latitude','longitude'])

		#create a buffer for wifi/bt data
		self.buffer_em = pd.DataFrame(columns=['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude'])


		# variables for EM stats call
		# all unique MACs received during session
		self.em_idents = []
		
		# how many APs this scan
		self.current_em_no = 0

		# Max number APs detected in one scan this session
		self.max_em_no = 0


		# holds the thermal camera frame for display in other programs
		self.thermal_frame = []

		self.timer = timer()

	@contextlib.contextmanager

	def safe_lock(self):
		"""Context manager to ensure lock is always released."""
		try:
			self.lock.acquire()
			yield
		finally:
			self.lock.release()

	def get_plars_size(self):
		with self.safe_lock():
			main_size = len(self.buffer)
			em_size = len(self.buffer_em)
		return main_size, em_size

	def get_em_stats(self):
		with self.safe_lock():
			idents = self.em_idents
			current_em_no = self.current_em_no
			max_em_no = self.max_em_no
		return idents, current_em_no, max_em_no

	def shutdown(self):
		if configure.datalog[0]:
			self.append_to_core(self.buffer)
			self.append_to_em_core(self.buffer_em)

	# gets the latest CSV file
	def get_core(self):
		datacore = pd.read_csv(self.file_path)
		return datacore

	#appends a new set of data to the CSV file.
	def append_to_core(self, data):
		data.to_csv(self.file_path, mode='a', header=False)

	#appends a new set of data to the EM CSV file.
	def append_to_em_core(self, data):
		data.to_csv(self.em_file_path, mode='a', header=False)

	def get_recent_bt_list(self):
		with self.safe_lock():
			# get the most recent ssids discovered
			recent_em = self.get_bt_recent()
		return recent_em.values.tolist()


	# returns a list of every EM transciever that was discovered last scan.
	def get_recent_em_list(self):
		with self.safe_lock():
			# get the most recent ssids discovered
			recent_em = self.get_em_recent()
			# sort it by signal strength
			recent_em.sort_values(by=['signal'], ascending=False)
		return recent_em.values.tolist()

	def get_top_em_info(self):
		with self.safe_lock():
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
		with self.safe_lock():
			wifi_buffer = self.buffer_em.loc[self.buffer_em['dsc'] == "wifi"]

			# find the most recent timestamp
			time_column = wifi_buffer["timestamp"]
			most_recent = time_column.max()

		#limit focus to data from that timestamp
		return wifi_buffer.loc[wifi_buffer['timestamp'] == most_recent]
	
	# checks if a mac address has been seen already and if not adds it to list.
	def em_been_seen(self, seen):
		pass

	def get_bt_recent(self):
		with self.safe_lock():
			bt_buffer = self.buffer_em.loc[self.buffer_em['dsc'] == "bluetooth"]
			# find the most recent timestamp
			time_column = bt_buffer["timestamp"]
			most_recent = time_column.max()

			#limit focus to data from that timestamp
		return bt_buffer.loc[bt_buffer['timestamp'] == most_recent]

	def get_top_em_history(self, no = 5):
		# returns a list of Db values for whatever SSID is currently the strongest.
		# suitable to be fed into pilgraph for graphing.

		with self.safe_lock():

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




		return self.get_recent_em(dev,frq, num = no)


	def update_em(self,data):
		with self.safe_lock():
			# logs some data for statistics
			self.current_em_no = len(data)
			if self.current_em_no > self.max_em_no:
				self.max_em_no = self.current_em_no

			# Add identifiers
			for sample in data:
				if sample[6] not in self.buffer_em["dev"].values and sample[6] not in self.em_idents:
					self.em_idents.append(sample[6])

			# Process data safely
			try:
				q = Queue()
				get_process = Process(target=update_em_proc, args=(q, self.buffer_em, data, ['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude']))
				get_process.start()
				
				# Set timeout for q.get() to prevent hanging
				result = q.get(timeout=10)  # 10 second timeout
				get_process.join(timeout=5)  # 5 second timeout
				
				if get_process.is_alive():
					get_process.terminate()
					raise TimeoutError("Process timed out")
					
				# appends the new data to the buffer
				self.buffer_em = result

				# get buffer size to determine how many rows to remove from the end
				currentsize = len(self.buffer_em)

				if configure.trim_buffer[0]:
					# if buffer is larger than double the buffer size
					if currentsize >= configure.buffer_size[0]:
						self.buffer_em = self.trim_em_buffer(configure.buffer_size[0])
			except Exception as e:
				print(f"Error in update_em: {e}")
				# Handle the error appropriately


	# updates the thermal frame for display
	def update_thermal(self, frame):
		with self.safe_lock():
			self.thermal_frame = frame

	# updates the dataframe in memory with the most recent sensor values from each
	# initialized sensor.
	# Sensor data is taken in as Fragment() instance objects. Each one contains
	# the sensor value and context for it (scale, symbol, unit, etc).
	def update(self,data):
		with self.safe_lock():
			try:
				q = Queue()
				get_process = Process(target=update_proc, args=(q, self.buffer, data, ['value','min','max','dsc','sym','dev','timestamp','latitude','longitude']))
				get_process.start()
				
				# Set timeout for q.get() to prevent hanging
				result = q.get(timeout=10)  # 10 second timeout
				get_process.join(timeout=5)  # 5 second timeout
				
				if get_process.is_alive():
					get_process.terminate()
					raise TimeoutError("Process timed out")
				
				# sets the new dataframe as the buffer
				self.buffer = result

				# get buffer size to determine how many rows to remove from the end
				currentsize = len(self.buffer)

				if configure.trim_buffer[0]:
					# if buffer is larger than double the buffer size
					if currentsize >= configure.buffer_size[0] * 2:
						self.buffer = self.trimbuffer(configure.buffer_size[0])
			except Exception as e:
				print(f"Error in update: {e}")
				# Handle the error appropriately


	# return a list of n most recent data from specific sensor defined by keys
	def get_recent(self, dsc, dev, num = 5, time = False):
		with self.safe_lock():
			try:
				q = Queue()
				get_process = Process(target=get_recent_proc, args=(q, self.buffer, dsc, dev, num))
				get_process.start()
				
				# Set timeout for q.get() to prevent hanging
				result = q.get(timeout=10)  # 10 second timeout
				get_process.join(timeout=5)  # 5 second timeout
				
				if get_process.is_alive():
					get_process.terminate()
					raise TimeoutError("Process timed out")
					
				values = result[0]
				timelength = 0

				if len(result[1]) > 0:            
					timelength = max(result[1]) - min(result[1])
					
				return values, timelength
			except Exception as e:
				print(f"Error in get_recent: {e}")
				return [], 0


	def get_em(self,dev,frequency):
		result = self.buffer_em.loc[self.buffer_em['dev'] == dev]
		result2 = result.loc[result["frequency"] == frequency]

		return result2

	# returns all sensor data in the buffer for the specific sensor (dsc,dev)
	def get_sensor(self,dsc,dev):

		result = self.buffer[self.buffer["dsc"] == dsc]

		result2 = result.loc[result['dev'] == dev]

		return result2

	def get_thermal_frame(self):

		# sets/requests the thread lock to prevent other threads reading data.
		self.lock.acquire()

		thermalframe = self.thermal_frame

		# release the thread lock for other threads
		self.lock.release()

		return thermalframe

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

	def trim_em_buffer(self, targetsize):
		# should take the buffer in memory and trim some of it

		# get buffer size to determine how many rows to remove from the end
		currentsize = len(self.buffer_em)

		# determine difference between buffer and target size
		length = currentsize - targetsize

		# make a new dataframe of the most recent data to keep using
		newbuffer = self.buffer_em.tail(targetsize)

		# slice off the rows outside the buffer and backup to disk
		tocore = self.buffer_em.head(length)

		if configure.datalog[0]:
				self.append_to_em_core(tocore)

		# replace existing buffer with new trimmed buffer
		return newbuffer

	def trimbuffer(self, targetsize):
		# should take the buffer in memory and trim some of it

		# get buffer size to determine how many rows to remove from the end
		currentsize = len(self.buffer)

		# determine difference between buffer and target size
		length = currentsize - targetsize

		# make a new dataframe of the most recent data to keep using
		newbuffer = self.buffer.tail(targetsize)

		# slice off the rows outside the buffer and backup to disk
		tocore = self.buffer.head(length)

		if configure.datalog[0]:
				self.append_to_core(tocore)


		# replace existing buffer with new trimmed buffer
		return newbuffer


	def emrg(self):
		self.get_core()
		return self.df

	def convert_epoch(self, time):
		return datetime.datetime.fromtimestamp(time)

# create a process that can run seperately and handle requests
def plars_process(q_in, q_out):
	plars = PLARS()



# Creates a plars database object as soon as it is loaded.
plars = PLARS()
