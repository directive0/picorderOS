import sys
from queue import Empty
import traceback

from objects import * # Assuming 'objects.py' exists and is in PYTHONPATH
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import numpy
from array import *
from plars import * # Assuming 'plars.py' exists and is in PYTHONPATH
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
				scaledata = abs(numpy.interp(sourcelow,sourcerange,targetrange))
				newlist.append((linepoint,scaledata))
			linepoint = linepoint + jump

		conn.put(newlist)
		# Keep this print for confirmation of child process completion, useful for diagnosing hangs
		# if the parent is waiting for q.get()
		sys.exit(0) # Explicitly exit the child process immediately after putting data.

	except Exception as e:
		error_message = f"ERROR IN graph_prep_process: {e}\nTraceback:\n{traceback.format_exc()}"
		print(error_message, file=sys.stderr)
		with open("graph_prep_process_error.log", "a") as f:
			f.write(error_message + "\n")
		sys.exit(1) # Ensure the child process exits with an error code


class graph_area(object):
	def __init__(self, ident, graphcoords, graphspan, cycle = 0, colour = 0, width = 1, type = 0, samples = False):
		# print("graph_area.__init__ called", file=sys.stderr) # Removed non-essential print

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
		# print("PARENT(graphprep): Starting graph_prep_process...", file=sys.stderr) # Removed non-essential print
		prep_process = Process(target=graph_prep_process, args=(q,self.samples,datalist,self.auto,self.newrange,self.targetrange,self.sourcerange,self.linepoint,self.jump,sourcelow,))
		prep_process.start()

		result = []
		try:
			# print("PARENT(graphprep): Waiting for result from queue (timeout 5s)...", file=sys.stderr) # Removed non-essential print
			result = q.get(timeout=5)
			# print("PARENT(graphprep): Successfully received result from queue.", file=sys.stderr) # Removed non-essential print
			# Keep these prints if you ever need to inspect the data coming from the child
			# print(f"PARENT(graphprep): Type of result: {type(result)}", file=sys.stderr)
			# print(f"PARENT(graphprep): Length of result: {len(result)}", file=sys.stderr)
			# if len(result) > 0:
			#     print(f"PARENT(graphprep): First 5 elements of result: {result[:5]}", file=sys.stderr)
			# else:
			#     print("PARENT(graphprep) WARNING: Result list is empty from child process.", file=sys.stderr)

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
			# print("PARENT(graphprep): Process status before join:", prep_process.is_alive(), file=sys.stderr) # Removed non-essential print
			try:
				# print("PARENT(graphprep): Joining graph_prep_process...", file=sys.stderr) # Removed non-essential print
				prep_process.join(timeout=1)
				if prep_process.is_alive():
					print("PARENT(graphprep) WARNING: Child process still alive after join timeout. Forcing termination.", file=sys.stderr)
					prep_process.terminate()
				# print("PARENT(graphprep): graph_prep_process joined.", file=sys.stderr) # Removed non-essential print
			except Exception as e:
				error_message = f"PARENT(graphprep) ERROR: Exception during prep_process.join(): {e}\nTraceback:\n{traceback.format_exc()}"
				print(error_message, file=sys.stderr)
				with open("graph_prep_process_error.log", "a") as f:
					f.write(error_message + "\n")
				prep_process.terminate()

		# print("PARENT(graphprep): Returning result from graphprep.", file=sys.stderr) # Removed non-essential print
		return result


	def render(self, draw, auto = True, dot = True, ranger = None):

		# print("entered pilgraph render", file=sys.stderr) # Removed non-essential print
		return_value = 0

		# print("gets auto status", file=sys.stderr) # Removed non-essential print
		try:
			self.auto = configure.auto[0]
		except (NameError, AttributeError, IndexError) as e:
			print(f"ERROR: 'configure.auto' not found or invalid. Defaulting auto to True: {e}", file=sys.stderr)
			self.auto = True

		# print("determining graph type", file=sys.stderr) # Removed non-essential print
		dsc, dev = None, None
		if self.type == 0:
			# print("getting this graphs sensor info: ", self.ident, file=sys.stderr) # Removed non-essential print
			try:
				index = configure.sensors[self.ident][0]
				dsc,dev,sym,maxi,mini = configure.sensor_info[index]
			except (NameError, AttributeError, IndexError) as e:
				print(f"ERROR: Failed to get sensor info for graph {self.ident} from 'configure': {e}", file=sys.stderr)
				dsc,dev,sym,maxi,mini = "default_sensor", "default_device", "SYM", 100.0, 0.0

			# print("query PLARS for data", file=sys.stderr) # Removed non-essential print
			try:
				recent, self.timelength = plars.get_recent(dsc,dev,num = self.samples, time = True)
				if recent is None:
					print("WARNING: plars.get_recent returned None. Initializing recent as empty list.", file=sys.stderr)
					recent = []
			except Exception as e:
				print(f"ERROR: Failed to query PLARS for recent data for {dsc}/{dev}: {e}", file=sys.stderr)
				recent = []

			# print("assigning 47 if no data", file=sys.stderr) # Removed non-essential print
			if len(recent) == 0:
				return_value = 47
			else:
				return_value = recent[-1]

		elif self.type == 1:
			# print("query PLARS for top EM history data.", file=sys.stderr) # Removed non-essential print
			try:
				recent = plars.get_top_em_history(no = self.samples)
				if recent is None:
					print("WARNING: plars.get_top_em_history returned None. Initializing recent as empty list.", file=sys.stderr)
					recent = []
			except Exception as e:
				print(f"ERROR: Failed to query PLARS for EM history: {e}", file=sys.stderr)
				recent = []

			if len(recent) == 0:
				return_value = -999
			else:
				return_value = recent[-1]

		elif self.type == 2:
			# print("query PLARS for new graph type 2 data.", file=sys.stderr) # Removed non-essential print
			try:
				recent = plars.get_recent(dsc,dev,num = self.samples)
				if recent is None:
					print("WARNING: plars.get_recent for type 2 returned None. Initializing recent as empty list.", file=sys.stderr)
					recent = []
			except Exception as e:
				print(f"ERROR: Failed to query PLARS for type 2 data: {e}", file=sys.stderr)
				recent = []


		# print("sending data to graphprep", file=sys.stderr) # Removed non-essential print
		cords = self.graphprep(recent)
		# print("returned from graphprep", file=sys.stderr) # Removed non-essential print

		self.buff = recent

		# print("drawing graph", file=sys.stderr) # Removed non-essential print
		try:
			draw.line(cords,self.colour,self.width)
		except Exception as e:
			print(f"ERROR: Failed to draw line graph with cords: {cords[:10]}... Error: {e}", file=sys.stderr)
			print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)


		# print("drawing dots", file=sys.stderr) # Removed non-essential print
		if dot:
			try:
				if len(cords) > 0:
					x1 = cords[0][0] - (self.dotw/2)
					y1 = cords[0][1] - (self.doth/2)
					x2 = cords[0][0] + (self.dotw/2)
					y2 = cords[0][1] + (self.doth/2)
					draw.ellipse([x1,y1,x2,y2],self.colour)
				else:
					print("PILgraph: No cords to draw dot, skipping.", file=sys.stderr) # Retained this warning
			except Exception as e:
				print(f"ERROR: Failed to draw dot with cords[0]: {cords[0] if len(cords)>0 else 'N/A'}. Error: {e}", file=sys.stderr)
				print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)


		# print("returning from pilgraph", file=sys.stderr) # Removed non-essential print
		return return_value