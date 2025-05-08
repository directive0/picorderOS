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

def plars_package_direct(iwlist_output):
    """
    Parses the raw iwlist output and packages it directly into the 'plars' format.
    """
    timestamp = time.time()
    ap_fragments = []
    cell_pattern = re.compile(r"Cell \d+ - Address: (.*?\n(?:.*?Signal level=(.*?)\s+dBm)?[\s\S]*?ESSID:\"(.*?)\"(?:[\s\S]*?Mode:(.*?))?(?:[\s\S]*?Channel:(.*?))?(?:[\s\S]*?Frequency:(.*?) GHz)?(?:[\s\S]*?Encryption key:(.*?))?)", re.MULTILINE)
    quality_pattern = re.compile(r"Quality=(\d+/\d+)")
    encryption_pattern = re.compile(r"Encryption key:(on|off)")


    for cell_match in cell_pattern.finditer(iwlist_output):
        mac = cell_match.group(1).strip()
        signal_level_str = cell_match.group(2)
        essid = cell_match.group(3)
        mode = cell_match.group(4).strip() if cell_match.group(4) else 'n/a'
        channel = cell_match.group(5).strip() if cell_match.group(5) else 'n/a'
        frequency_str = cell_match.group(6)
        frequency = float(frequency_str) if frequency_str else 0.0
        encryption_status = cell_match.group(7)
        encryption = 'WEP' if encryption_status == 'on' else 'None' if encryption_status == 'off' else 'n/a'

        quality_match = quality_pattern.search(cell_match.group(0))
        quality = quality_match.group(1).split('/')[0] if quality_match else '0'

        signal_level = int(signal_level_str) if signal_level_str else -100 # Default low signal

        details = [essid,
                   signal_level,
                   int(quality),
                   frequency,
                   encryption,
                   channel,
                   mac,
                   mode,
                   'wifi',
                   timestamp]
        ap_fragments.append(details)

    return ap_fragments


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

def threaded_wifi():
	
	if configure.EM:
		output_queue = multiprocessing.Queue()
		wifi_process = multiprocessing.Process(target=get_wifi_scan_root_process, args=(output_queue,))
		wifi_process.start()
		wifi_process.join()
	


	while True:

		#grab wifi and BT data
		if configure.EM:
			result = output_queue.get()
			if result != None:
				for ssid in result:
					ssid.append(configure.position[0])
					ssid.append(configure.position[1])
				plars.update_em(result)




# The following code sets up the various threads that the rest of the program will use
#start the sensor loop
wifi_thread = Thread(target = threaded_wifi, args = ())
wifi_thread.start()


