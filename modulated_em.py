# PicorderOS Wifi Module Proto
print("Loading Modulated EM Signal Analysis")

from threading import Thread

import iwlist
import time
from plars import *
from objects import *
import socket
from bluetooth import *

def get_hostname():
	hostname = socket.gethostname()
	return hostname

# returns the current IP or an error
def get_IP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		s.connect(("8.8.8.8", 80))
		IPAddr = s.getsockname()[0]
	except:
		IPAddr = "No IP Found"

	return IPAddr

def get_ssid():
	return os.popen("iwgetid").readline()

class Wifi_Scan(object):

	timed = timer()

	def __init__(self):
		pass

	def get_list(self):
		if self.timed.timelapsed() > configure.em_samplerate:
			try:
				content = iwlist.scan(interface='wlan0')
				ap_list = iwlist.parse(content)
			except Exception as e:
				print("Wifi failed: ", e)
				ap_list = []
			self.timed.logtime()
			return ap_list

	def get_info(self,selection):
		ap_list = self.update()

		if selection <= (len(ap_list)-1):
			return (ap_list[selection].ssid, int(ap_list[selection].signal), ap_list[selection].quality, ap_list[selection].frequency, ap_list[selection].bitrates, ap_list[selection].encrypted, ap_list[selection].channel, ap_list[selection].address, ap_list[selection].mode)


	def dump_data(self):
		ap_list = self.get_list()
		return self.plars_package(ap_list)

	def plars_package(self, ap_list):
		timestamp = time.time()
		ap_fragments = []

		if ap_list != None:
			if len(ap_list) > 0:
				for ap in ap_list:
					details = [ap["essid"], 
							int(ap["signal_level_dBm"]),
							int(ap["signal_quality"]), 
							float(ap["frequency"]), 
							ap["encryption"], 
							ap["channel"], 
							ap["mac"], 
							ap["mode"], 
							'wifi', 
							timestamp,
							configure.position[0],
							configure.position[1]]
					ap_fragments.append(details)
			else:
				ap_fragments = None

		return ap_fragments


	def update_plars(self):
		data = self.dump_data()
		if data != None:
			plars.update_em(data)

	def get_ssid_list(self):

		title_list = []

		ap_list = self.get_list()
		for ap in ap_list:
			name = ap.ssid
			title_list.append(name)

		return title_list



class BT_Scan(object):

	timed = timer()

	def __init__(self):
		pass

	def get_list(self):
		return discover_devices(lookup_names = True, lookup_class = True)

	def dump_data(self):
		bt_list = self.get_list()
		return self.plars_package(bt_list)

	def plars_package(self, bt_list):
		timestamp = time.time()
		bt_fragments = []

		for bt in bt_list:
			details = [bt[1], "n/a", "n/a", "n/a", "n/a", "n/a", bt[0], bt[2], 'bluetooth', timestamp]
			bt_fragments.append(details)

		return bt_fragments

	def update_plars(self):
		plars.update_em(self.dump_data())

def threaded_wifi():
	
	if configure.EM:
		wifitimer = timer()
		wifi = Wifi_Scan()


	while not configure.status == "quit":

		#grab wifi and BT data
		if configure.EM and wifitimer.timelapsed() > configure.em_samplerate:
			wifi.update_plars()
			wifitimer.logtime() 



# The following code sets up the various threads that the rest of the program will use
#start the sensor loop
wifi_thread = Thread(target = threaded_wifi, args = ())
wifi_thread.start()


