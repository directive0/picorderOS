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

	# Helper methods that DON'T acquire locks separately
	def _get_em_recent_no_lock(self):
		"""Get recent EM data WITHOUT acquiring lock."""
		wifi_buffer = self.buffer_em.loc[self.buffer_em['dsc'] == "wifi"]
		
		if len(wifi_buffer) == 0:
			return None
			
		# find the most recent timestamp
		time_column = wifi_buffer["timestamp"]
		if len(time_column) == 0:
			return None
			
		most_recent = time_column.max()
		return wifi_buffer.loc[wifi_buffer['timestamp'] == most_recent]
	def _get_bt_recent_no_lock(self):
		"""Get recent BT data WITHOUT acquiring lock."""
		bt_buffer = self.buffer_em.loc[self.buffer_em['dsc'] == "bluetooth"]
		
		if len(bt_buffer) == 0:
			return None
			
		# find the most recent timestamp
		time_column = bt_buffer["timestamp"]
		if len(time_column) == 0:
			return None
			
		most_recent = time_column.max()
		return bt_buffer.loc[bt_buffer['timestamp'] == most_recent]
		
	def _get_em_no_lock(self, dev, frequency):
		"""Get EM data WITHOUT acquiring lock."""
		result = self.buffer_em.loc[self.buffer_em['dev'] == dev]
		if len(result) == 0:
			return None
		result2 = result.loc[result["frequency"] == frequency]
		return result2

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
		"""Get list of recent Bluetooth devices."""
		with self.safe_lock():
			recent_em = self._get_bt_recent_no_lock()
			if recent_em is None or len(recent_em) == 0:
				return []
			return recent_em.values.tolist()

	# returns a list of every EM transciever that was discovered last scan.
	def get_recent_em_list(self):
		"""Get list of recent EM devices."""
		with self.safe_lock():
			recent_em = self._get_em_recent_no_lock()
			if recent_em is None or len(recent_em) == 0:
				return []
			# sort it by signal strength
			recent_em = recent_em.sort_values(by=['signal'], ascending=False)
			return recent_em.values.tolist()

# PUBLIC methods that DO acquire locks
	def get_em_recent(self):
		"""Get recent EM data with lock protection."""
		with self.safe_lock():
			return self._get_em_recent_no_lock()
	
	# checks if a mac address has been seen already and if not adds it to list.
	def em_been_seen(self, seen):
		pass

	def get_bt_recent(self):
		"""Get recent BT data with lock protection."""
		with self.safe_lock():
			return self._get_bt_recent_no_lock()
		
	def get_top_em_history(self, no=5):
		"""Get history of the strongest EM signal."""
		try:
			with self.safe_lock():
				# Get recent EM data
				focus = self._get_em_recent_no_lock()
				if focus is None or len(focus) == 0:
					return []
				
				# Find most powerful signal
				db_column = focus["signal"]
				if len(db_column) == 0:
					return []
					
				strongest = db_column.astype(int).max()
				
				# Identify the SSID of the strongest signal
				identity = focus.loc[focus['signal'] == strongest]
				if len(identity) == 0:
					return []
				
				# Prepare markers to pull data
				try:
					dev = identity["dev"].iloc[0]
					frq = identity["frequency"].iloc[0]
				except IndexError:
					return []
				
				# Get EM data for this device and frequency
				untrimmed_data = self._get_em_no_lock(dev, frq)
				if untrimmed_data is None or len(untrimmed_data) == 0:
					return []
					
				# Trim it to length (no)
				trimmed_data = untrimmed_data.tail(no)
				
				# Return signal values
				return trimmed_data['signal'].tolist()
		except Exception as e:
			print(f"Error in get_top_em_history: {e}")
			return []
	
	def update_em(self, data):
		"""Update EM data safely."""
		try:
			# Create process and queue BEFORE acquiring lock
			q = Queue()
			process = Process(target=update_em_proc, args=(q, self.buffer_em, data, 
				['ssid','signal','quality','frequency','encrypted','channel','dev','mode','dsc','timestamp','latitude','longitude']))
			process.start()
			
			# Wait for result with timeout BEFORE acquiring lock
			try:
				result = q.get(timeout=10)  # 10 second timeout
				process.join(timeout=5)     # 5 second timeout
				
				if process.is_alive():
					process.terminate()
					print("Process timed out in update_em")
					return
			except Exception as e:
				print(f"Error getting process result in update_em: {e}")
				if process.is_alive():
					process.terminate()
				return
				
			# AFTER process completes, acquire lock and update data
			with self.safe_lock():
				# Update statistics
				self.current_em_no = len(data)
				if self.current_em_no > self.max_em_no:
					self.max_em_no = self.current_em_no
				
				# Add identifiers
				for sample in data:
					if sample[6] not in self.buffer_em["dev"].values and sample[6] not in self.em_idents:
						self.em_idents.append(sample[6])
						
				# Update buffer with process result
				self.buffer_em = result
				
				# Trim buffer if needed
				currentsize = len(self.buffer_em)
				if configure.trim_buffer[0] and currentsize >= configure.buffer_size[0]:
					self.buffer_em = self.trim_em_buffer(configure.buffer_size[0])
		except Exception as e:
			print(f"Error in update_em: {e}")
	

	# updates the thermal frame for display
	def update_thermal(self, frame):
		with self.safe_lock():
			self.thermal_frame = frame

	# updates the dataframe in memory with the most recent sensor values from each
	# initialized sensor.
	# Sensor data is taken in as Fragment() instance objects. Each one contains
	# the sensor value and context for it (scale, symbol, unit, etc).
	def update(self, data):
		"""Update sensor data safely."""
		try:
			# Create process and queue BEFORE acquiring lock
			q = Queue()
			process = Process(target=update_proc, args=(q, self.buffer, data, 
				['value','min','max','dsc','sym','dev','timestamp','latitude','longitude']))
			process.start()
			
			# Wait for result with timeout BEFORE acquiring lock
			try:
				result = q.get(timeout=10)  # 10 second timeout
				process.join(timeout=5)     # 5 second timeout
				
				if process.is_alive():
					process.terminate()
					print("Process timed out in update")
					return
			except Exception as e:
				print(f"Error getting process result in update: {e}")
				if process.is_alive():
					process.terminate()
				return
				
			# AFTER process completes, acquire lock and update data
			with self.safe_lock():
				# Update buffer with process result
				self.buffer = result
				
				# Trim buffer if needed
				currentsize = len(self.buffer)
				if configure.trim_buffer[0] and currentsize >= configure.buffer_size[0] * 2:
					self.buffer = self.trimbuffer(configure.buffer_size[0])
		except Exception as e:
			print(f"Error in update: {e}")
			

	# return a list of n most recent data from specific sensor defined by keys
	def get_recent(self, dsc, dev, num=5, time=False):
		"""Get recent data for specified sensor."""
		try:
			# Create process and queue BEFORE acquiring lock
			q = Queue()
			process = Process(target=get_recent_proc, args=(q, self.buffer, dsc, dev, num))
			process.start()
			
			# Wait for result with timeout BEFORE acquiring lock
			try:
				result = q.get(timeout=10)  # 10 second timeout
				process.join(timeout=5)     # 5 second timeout
				
				if process.is_alive():
					process.terminate()
					print("Process timed out in get_recent")
					return [], 0
			except Exception as e:
				print(f"Error getting process result in get_recent: {e}")
				if process.is_alive():
					process.terminate()
				return [], 0
				
			# Process result WITHOUT holding lock
			values = result[0]
			timelength = 0
			
			if len(result[1]) > 0:            
				timelength = max(result[1]) - min(result[1])
				
			return values, timelength
		except Exception as e:
			print(f"Error in get_recent: {e}")
			return [], 0
		
	def get_em(self, dev, frequency):
		"""Get EM data for specific device and frequency."""
		with self.safe_lock():
			return self._get_em_no_lock(dev, frequency)

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

	def get_top_em_info(self):
		"""Get information about the strongest EM signal."""
		with self.safe_lock():
			focus = self._get_em_recent_no_lock()
			if focus is None or len(focus) == 0:
				return []
			
			# find most powerful signal
			db_column = focus["signal"]
			if len(db_column) == 0:
				return []
				
			strongest = db_column.astype(int).max()
			
			# Identify the SSID of the strongest signal
			self.identity = focus.loc[focus['signal'] == strongest]
			if len(self.identity) == 0:
				return []
				
			return self.identity.values.tolist()

	# return a list of n most recent data from specific ssid defined by keys
	def get_recent_em(self, dev, frequency, num=5):
		"""Get recent EM data for specific device and frequency."""
		with self.safe_lock():
			# Get EM data without acquiring another lock
			untrimmed_data = self._get_em_no_lock(dev, frequency)
			if untrimmed_data is None or len(untrimmed_data) == 0:
				return []
				
			# Trim it to length (num)
			trimmed_data = untrimmed_data.tail(num)
			
			# Return signal values
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
