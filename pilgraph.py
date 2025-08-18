import sys
from queue import Empty
import traceback

from objects import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import numpy
from array import *
from plars import *
from multiprocessing import Process,Queue,Pipe


# function to calculate onscreen coordinates of graph pixels as a process.
def graph_prep_process(conn,samples,datalist,auto,newrange,targetrange,sourcerange,linepoint,jump,sourcelow):
	newlist = []
	try:
		for i in range(samples):
			if i < len(datalist):
				indexer = (len(datalist) - i) - 1
				if auto == True:
					scaledata = abs(numpy.interp(datalist[indexer],newrange,targetrange))
				else:
					scaledata = abs(numpy.interp(datalist[indexer],sourcerange,targetrange))
				newlist.append((linepoint,scaledata))
			else:
				# This part now only executes if datalist is shorter than samples
				# If datalist is empty, sourcelow will be used.
				scaledata = abs(numpy.interp(sourcelow,sourcerange,targetrange))
				newlist.append((linepoint,scaledata))
			linepoint = linepoint + jump

		conn.put(newlist)
		sys.exit(0)

	except Exception as e:
		error_message = f"ERROR IN graph_prep_process: {e}\nTraceback:\n{traceback.format_exc()}"
		print(error_message, file=sys.stderr)
		with open("graph_prep_process_error.log", "a") as f:
			f.write(error_message + "\n")
		sys.exit(1)


class graph_area(object):
	def __init__(self, ident, graphcoords, graphspan, cycle = 0, colour = 0, width = 1, type = 0, samples = False):
		if not samples:
			try:
				self.samples = configure.samples
			except (NameError, AttributeError):
				print("ERROR: 'configure' object or 'configure.samples' not found. Defaulting samples to 100.", file=sys.stderr)
				self.samples = 100
		else:
			self.samples = samples

		self.cycle = cycle
		self.glist = array('f', [])
		self.dlist = array('f', [])
		self.colour = colour
		self.auto = True
		self.width = width
		self.dotw = 6
		self.doth = 6
		self.buff = array('f', [])
		self.type = type
		self.last_known_data = [] # Stores raw data for potential recalculation if last_known_cords is empty
		self.last_known_cords = [] # Stores calculated screen coordinates for direct redraw

		try:
			self.timeit = timer()
		except NameError:
			print("ERROR: 'timer' object not found. Skipping timer initialization.", file=sys.stderr)
			self.timeit = None

		self.datahigh = 0
		self.datalow = 0
		self.newrange = (self.datalow,self.datahigh)
		self.timelength = 0
		self.ident = ident
		self.x, self.y = graphcoords
		self.spanx,self.spany = graphspan
		self.targetrange = ((self.y + self.spany), self.y)

		for i in range(self.spanx):
			self.glist.append(self.y + self.spany)
			self.dlist.append(self.datalow)
			self.buff.append(self.datalow)


	def grabglist(self):
		return self.glist

	def grabdlist(self):
		return self.dlist

	def get_average(self):
		if not self.buff:
			return 0.0
		return sum(self.buff) / len(self.buff)

	def get_high(self):
		if not self.buff:
			return self.datahigh
		return max(self.buff)

	def get_low(self):
		if not self.buff:
			return self.datalow
		return min(self.buff)

	def giveperiod(self):
		self.period = (self.spanx * self.cycle) / 60
		return self.period


	def graphprep(self, datalist, ranger = None):
		try:
			index = configure.sensors[self.ident][0]
			dsc,dev,sym,maxi,mini = configure.sensor_info[index]
		except (NameError, AttributeError, IndexError) as e:
			print(f"PARENT(graphprep) ERROR: Failed to get sensor info from 'configure': {e}", file=sys.stderr)
			print("PARENT(graphprep): Using default sensor ranges due to error.", file=sys.stderr)
			dsc,dev,sym,maxi,mini = "default_sensor", "default_device", "SYM", 100.0, 0.0

		self.linepoint = self.spanx + self.x
		spacing = self.spanx / self.samples
		self.jump = -spacing

		if self.type == 0:
			sourcelow = mini
			sourcehigh = maxi
			self.sourcerange = [sourcelow,sourcehigh]
		else:
			sourcelow = -90
			sourcehigh = -5
			self.sourcerange = [sourcelow,sourcehigh]

		if len(datalist) > 0:
			self.datahigh = max(datalist)
			self.datalow = min(datalist)
		else:
			self.datahigh = sourcehigh
			self.datalow = sourcelow

		self.newrange = (self.datalow,self.datahigh)

		q = Queue()
		prep_process = Process(target=graph_prep_process, args=(q,self.samples,datalist,self.auto,self.newrange,self.targetrange,self.sourcerange,self.linepoint,self.jump,sourcelow,))
		prep_process.start()

		result = []
		try:
			result = q.get(timeout=5)

		except Empty:
			print("PARENT(graphprep) ERROR: graph_prep_process timed out or did not return data. Terminating child.", file=sys.stderr)
			prep_process.terminate()
		except Exception as e:
			error_message = f"PARENT(graphprep) ERROR: Exception getting result from graph_prep_process queue: {e}\nTraceback:\n{traceback.format_exc()}"
			print(error_message, file=sys.stderr)
			with open("graph_prep_process_error.log", "a") as f:
				f.write(error_message + "\n")
			prep_process.terminate()
		finally:
			try:
				prep_process.join(timeout=1)
				if prep_process.is_alive():
					prep_process.terminate()
			except Exception as e:
				error_message = f"PARENT(graphprep) ERROR: Exception during prep_process.join(): {e}\nTraceback:\n{traceback.format_exc()}"
				print(error_message, file=sys.stderr)
				with open("graph_prep_process_error.log", "a") as f:
					f.write(error_message + "\n")
				prep_process.terminate()

		return result


	def render(self, draw, auto = True, dot = True, ranger = None):
		return_value = 0

		try:
			self.auto = configure.auto[0]
		except (NameError, AttributeError, IndexError) as e:
			print(f"ERROR: 'configure.auto' not found or invalid. Defaulting auto to True: {e}", file=sys.stderr)
			self.auto = True

		dsc, dev = None, None
		
		current_data_retrieved = False
		recent_raw_data = [] # Temporary variable to hold newly fetched raw data

		if self.type == 0:
			try:
				index = configure.sensors[self.ident][0]
				dsc,dev,sym,maxi,mini = configure.sensor_info[index]
			except (NameError, AttributeError, IndexError) as e:
				print(f"ERROR: Failed to get sensor info for graph {self.ident} from 'configure': {e}", file=sys.stderr)
				dsc,dev,sym,maxi,mini = "default_sensor", "default_device", "SYM", 100.0, 0.0

			try:
				queried_recent, self.timelength = plars.get_recent(dsc,dev,num = self.samples, time = True)
				if queried_recent is not None and len(queried_recent) > 0:
					recent_raw_data = queried_recent
					current_data_retrieved = True
			except Exception as e:
				print(f"ERROR: Failed to query PLARS for recent data for {dsc}/{dev}: {e}", file=sys.stderr)

			if len(recent_raw_data) == 0:
				if self.last_known_data:
					return_value = self.last_known_data[-1]
				else:
					return_value = 47 
			else:
				return_value = recent_raw_data[-1]

		elif self.type == 1:
			try:
				queried_recent = plars.get_top_em_history(no = self.samples)
				if queried_recent is not None and len(queried_recent) > 0:
					recent_raw_data = queried_recent
					current_data_retrieved = True

			except Exception as e:
				print(f"ERROR: Failed to query PLARS for EM history: {e}", file=sys.stderr)

			if len(recent_raw_data) == 0:
				if self.last_known_data:
					return_value = self.last_known_data[-1]
				else:
					return_value = -999
			else:
				return_value = recent_raw_data[-1]

		elif self.type == 2:
			try:
				queried_recent = plars.get_recent(dsc,dev,num = self.samples)
				if queried_recent is not None and len(queried_recent) > 0:
					recent_raw_data = queried_recent
					current_data_retrieved = True
			except Exception as e:
				print(f"ERROR: Failed to query PLARS for type 2 data: {e}", file=sys.stderr)
			
			if len(recent_raw_data) == 0:
				if self.last_known_data:
					return_value = self.last_known_data[-1]
				else:
					return_value = 0 # Or some appropriate default for type 2
			else:
				return_value = recent_raw_data[-1]


		# Determine which data to use for drawing
		cords = []
		if current_data_retrieved and len(recent_raw_data) > 0:
			cords = self.graphprep(recent_raw_data)
			# Update last_known_data and last_known_cords if new data was successfully retrieved
			self.last_known_data = recent_raw_data
			if cords: # Only update last_known_cords if graphprep actually returned coordinates
				self.last_known_cords = cords
		elif self.last_known_cords:
			# Use previously calculated screen coordinates if no new data
			cords = self.last_known_cords
			#print(f"INFO: Using last known screen coordinates for graph {self.ident}.", file=sys.stderr)
		else:
			# If no new data and no last known cords, try to use last known raw data
			if self.last_known_data:
				#print(f"INFO: No new data, no last known cords. Recalculating from last known raw data for graph {self.ident}.", file=sys.stderr)
				cords = self.graphprep(self.last_known_data)
				if cords:
					self.last_known_cords = cords # Update last_known_cords after recalculation
			else:
				#print(f"WARNING: No new data, no last known cords, and no last known raw data for graph {self.ident}. Graph will be flat.", file=sys.stderr)
				# As a last resort, pass an empty list and let graphprep handle the flat line based on sourcelow.
				cords = self.graphprep([])


		self.buff = recent_raw_data # self.buff should reflect the raw data that was processed or intended for processing

		try:
			draw.line(cords,self.colour,self.width)
		except Exception as e:
			print(f"ERROR: Failed to draw line graph with cords (first 10): {cords[:10]}... Error: {e}", file=sys.stderr)
			print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)

		if dot:
			try:
				if len(cords) > 0:
					x1 = cords[0][0] - (self.dotw/2)
					y1 = cords[0][1] - (self.doth/2)
					x2 = cords[0][0] + (self.dotw/2)
					y2 = cords[0][1] + (self.doth/2)
					draw.ellipse([x1,y1,x2,y2],self.colour)
				else:
					pass
					#print("PILgraph: No cords to draw dot, skipping.", file=sys.stderr)
			except Exception as e:
				print(f"ERROR: Failed to draw dot with cords[0]: {cords[0] if len(cords)>0 else 'N/A'}. Error: {e}", file=sys.stderr)
				print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)

		return return_value