# PicorderOS Wifi Module Proto
print("Loading Modulated EM Signal Analysis")

from threading import Thread

import re
import time
from plars import *
from objects import *
import socket
from bluetooth import *
import multiprocessing
import subprocess
import re
import queue


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
		try:
			ap_list = iwlist.scan(interface='wlan0')
		except Exception as e:
			print("Wifi failed: ", e)
			ap_list = []

		return ap_list

	def dump_data(self):
		ap_list = self.parse_iwlist_output(self.get_list())
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

	def parse_iwlist_output(self, iwlist_output):
		# Regular expression patterns for parsing iwlist output
		ap_list = []
		ap_pattern = re.compile(r"Cell (\d+):\n\s*Address: (.*)\n\s*ESSID:\"(.*?)\"\n\s*Mode:(.*)\n\s*Channel:(\d+)\n\s*Frequency:(\d+\.\d+) GHz\n\s*Quality=(\d+/\d+)\s*Signal level=(\-?\d+) dBm\n\s*Encryption key:(\w+)\n", re.DOTALL)

		# Loop over all APs in the output
		matches = ap_pattern.findall(iwlist_output)
		for match in matches:
			ap = {
				"mac": match[1],
				"essid": match[2],
				"mode": match[3].strip(),
				"channel": match[4],
				"frequency": float(match[5]),
				"signal_quality": match[6].split('/')[0],  # Extract quality from "Quality=XX/XX"
				"signal_level_dBm": match[7],
				"encryption": 'WEP' if match[8] == 'on' else 'None'  # Assuming 'on' indicates WEP encryption
			}
			ap_list.append(ap)
		
		return ap_list

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

def plars_package_direct(output):
	"""Parses the output of 'iwlist wlan0 scanning' into a list of dictionaries."""
	aps = []
	current_ap = {}
	for line in output.strip().split('\n'):
		line = line.strip()
		if line.startswith("Cell"):
			if current_ap:
				aps.append(current_ap)
			current_ap = {}
			match = re.search(r"Address: (([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})", line)
			if match:
				current_ap['mac'] = match.group(1)
		elif line.startswith("ESSID:"):
			current_ap['ssid'] = line.split('"')[1]
		elif line.startswith("Channel:"):
			current_ap['channel'] = int(line.split(':')[1])
		elif line.startswith("Frequency:"):
			match = re.search(r"(\d+\.\d+) GHz", line)
			if match:
				current_ap['frequency'] = float(match.group(1))
		elif line.startswith("Quality="):
			match = re.search(r"Quality=(\d+/\d+)\s+Signal level=(-?\d+) dBm", line)
			if match:
				quality_parts = match.group(1).split('/')
				current_ap['quality'] = int(quality_parts[0]) / int(quality_parts[1]) if quality_parts[1] != '0' else 0
				current_ap['signal_level_dbm'] = int(match.group(2))
		elif line.startswith("Encryption key:"):
			current_ap['encryption'] = "on" if line.endswith("on") else "off"

	if current_ap:
		aps.append(current_ap)
	return aps



def get_wifi_scan_root_process(output_queue):
	while True:
		"""
		Scans Wi-Fi networks with root privileges and returns a list of SSIDs
		with detailed information as dictionaries via a multiprocessing Queue.
		"""
		try:
			# Execute iwlist with sudo to get root privileges
			output = subprocess.check_output(['sudo', 'iwlist', 'wlan0', 'scanning'], text=True, stderr=subprocess.PIPE)
			ap_list = plars_package_direct(output)
			output_queue.put(ap_list)
		except subprocess.CalledProcessError as e:
			error_message = f"Error scanning Wi-Fi: {e.stderr}"
			output_queue.put({"error": error_message})
		except FileNotFoundError:
			error_message = "Error: iwlist not found. Ensure it's in your system's PATH."
			output_queue.put({"error": error_message})
		except Exception as e:
			error_message = f"An unexpected error occurred: {e}"
			output_queue.put({"error": error_message})
		
		time.sleep(5)

def threaded_wifi():
	
	if configure.EM:
		output_queue = multiprocessing.Queue()
		wifi_process = multiprocessing.Process(target=get_wifi_scan_root_process, args=(output_queue,))
		wifi_process.daemon = True
		wifi_process.start()
		#wifi_process.join()
	


	while True:

		#grab wifi and BT data
		if configure.EM:
			try:
				# Non-blocking get with timeout
				result = output_queue.get(timeout=1)
				if result is not None:
					for ssid in result:
						ssid.append(configure.position[0])
						ssid.append(configure.position[1])
					plars.update_em(result)
			except queue.Empty:
				# No data available, just continue
				pass
			time.sleep(0.1)  # Small delay to prevent CPU hogging




# The following code sets up the various threads that the rest of the program will use
#start the sensor loop
wifi_thread = Thread(target = threaded_wifi, args = ())
wifi_thread.start()


