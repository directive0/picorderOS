print("Loading Picorder Library Access and Retrieval System Module")
from objects import *

#	DataCore aims to provide a single surface for retrieving data for
#	display in any of the different Picorder screen modes.

#	TO DO
#	Create and open CSV storage file
#

import os.path
from os import path
import numpy
import pandas as pd




# Create a class that acts as the surface for all interactions with the data core
class PLARS(object):

	def __init__(self):
		# PLARS opens a data frame at program start up.
		# If the csv file exists it opens it, otherwise creates it.
		self.file_path = "data/datacore.csv"

		if path.exists(self.file_path):
			self.df = pd.read_csv(self.file_path)
		else:
			self.df = pd.DataFrame([columns=['value','min','max','desc','sym','dev','timestamp'])
			self.df.to_csv(self.file_path)

	# gets the latest CSV file
	def get_core(self):
		self.df = pd.read_csv(self.file_path)

	# appends a new set of data to the CSV file.
	def append_core(self, data):
		 df.to_csv(self.file_path, mode='a', header=False)

	# updates the data storage file with the most recent sensor fragments
	def update(self,data):
		self.get_core()
		self.append_core()
		pass

	# return a number of most recent data from specific sensor
	def get_recent(self, num = 5, key):
		#load csv file as dataframe

		pass

	# return a number of data from a specific sensor at a specific time interval
	def get_timed(self, num = 5, key, interval = 0):
		#load csv file as dataframe
		pass

	# dump all data to CSV
	def emrg(self):
		pass
