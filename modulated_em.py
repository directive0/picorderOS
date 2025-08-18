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
import math


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
	
	# Split the output by Cell entries
	cells = re.split(r"Cell \d+ - ", iwlist_output)[1:]  # Skip the first empty element
	
	for cell in cells:
		try:
			# Extract the basic information with more precise regex patterns
			mac_match = re.search(r"Address: ([0-9A-F:]{17})", cell, re.IGNORECASE)
			essid_match = re.search(r"ESSID:\"(.*?)\"", cell)
			channel_match = re.search(r"Channel:(\d+)", cell)
			frequency_match = re.search(r"Frequency:(\d+\.\d+) GHz", cell)
			quality_match = re.search(r"Quality=(\d+)/\d+", cell)
			signal_match = re.search(r"Signal level=(-?\d+) dBm", cell)
			encryption_match = re.search(r"Encryption key:(on|off)", cell)
			mode_match = re.search(r"Mode:(.*?)$", cell, re.MULTILINE)
			
			# Extract values or use defaults
			mac = mac_match.group(1) if mac_match else 'n/a'
			essid = essid_match.group(1) if essid_match else ''
			channel = channel_match.group(1) if channel_match else 'n/a'
			frequency = float(frequency_match.group(1)) if frequency_match else 0.0
			quality = int(quality_match.group(1)) if quality_match else 0
			signal_level = int(signal_match.group(1)) if signal_match else -100
			encryption = 'WEP' if (encryption_match and encryption_match.group(1) == 'on') else 'None'
			mode = mode_match.group(1).strip() if mode_match else 'n/a'
			
			# Create the details list
			details = [
				essid,
				signal_level,
				quality,
				frequency,
				encryption,
				channel,
				mac,
				mode,
				'wifi',
				timestamp
			]
			ap_fragments.append(details)
		except Exception as e:
			print(f"Error parsing cell: {e}")
			continue
	
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
		
		time.sleep(1)

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
					for item in result:
						item.append(configure.position[0])
						item.append(configure.position[1])
					plars.update_em(result)
			except queue.Empty:
				# No data available, just continue
				pass
			#time.sleep(0.1)  # Small delay to prevent CPU hogging

def trilaterate_and_direct(signal_data, current_location):
    """
    Estimates the probable location of a Wi-Fi access point transmitter
    and the direction of travel based on simplified RSSI data.

    **Disclaimer:** This function uses highly simplified models for RSSI-to-distance
    conversion and location estimation. It does NOT provide accurate or reliable
    results for real-world scenarios due to the complex nature of radio signals
    and environmental factors. This is for illustrative purposes only.

    Args:
        signal_data (list of lists): A list where each inner list contains:
                                     [RSSI (int), latitude (float), longitude (float)]
                                     Example: [[-50, 43.7, -79.4], [-60, 43.701, -79.399]]
        current_location (list): Your current location [latitude (float), longitude (float)]
                                 Example: [43.702, -79.401]

    Returns:
        tuple: A tuple containing:
               - estimated_ap_location (list or None): [latitude, longitude] of the
                                                      probable AP location, or None if
                                                      not enough data.
               - direction_of_travel_description (str): A descriptive string of the
                                                        direction of travel relative to the AP.
    """

    if len(signal_data) < 2:
        return None, "Not enough data points to estimate direction or AP location accurately."

    # --- Step 1: Estimate Access Point Location (Simplified) ---
    # We'll assume a simple inverse relationship between RSSI and distance.
    # Higher RSSI (less negative) means closer.
    # We'll normalize RSSI to a positive scale and use it as an inverse "weight" for distance.
    # A common propagation model is Path Loss = P0 - 10 * n * log10(d)
    # where P0 is RSSI at 1 meter, n is path loss exponent.
    # For simplification, we'll just use a direct "distance factor" from RSSI.

    # Normalize RSSI to a more manageable scale (e.g., -30 dBm is very strong, -90 dBm is weak)
    # Let's say a baseline strong signal is -30 dBm and a weak is -90 dBm.
    # We can create a "proximity score": (RSSI_val - MIN_RSSI) / (MAX_RSSI - MIN_RSSI)
    # Higher proximity score means closer. We'll then invert this for a 'distance_weight'.

    # A simple approach for distance: distance = 10^((Measured_RSSI - A) / (-10 * N))
    # where A is the RSSI at 1 meter, N is the path loss exponent (2 for free space)
    # Since we don't have A or N, we'll just use RSSI directly as an inverse indicator of distance.
    # We'll assume an 'ideal' RSSI (e.g., -30 dBm) means '0' distance, and a very low RSSI means max distance.

    # Find the range of RSSI values to normalize
    min_rssi = min([d[0] for d in signal_data])
    max_rssi = max([d[0] for d in signal_data])

    if max_rssi == min_rssi: # Avoid division by zero
        # If all RSSI are the same, AP is likely very close or very far, can't pinpoint
        return None, "All RSSI values are identical, cannot estimate AP location reliably."

    # To convert degrees to radians for distance calculations
    DEG_TO_RAD = math.pi / 180

    # Earth's radius in meters for Haversine formula approximation
    R_EARTH = 6371000

    estimated_lat_sum = 0
    estimated_lon_sum = 0
    total_weight = 0

    # For a very rough 'weighted average' location of the AP
    for rssi, lat, lon in signal_data:
        # Higher RSSI (closer to 0) means more weight
        # Normalize RSSI to a positive scale where higher is better for weighting
        # Example: RSSI -50 -> 40, RSSI -80 -> 10 if max_rssi_consider = -30, min_rssi_consider = -90
        # A simple linear normalization:
        weight = (rssi - min_rssi) / (max_rssi - min_rssi) # 0 to 1, higher is stronger
        weight = weight**2 # Exaggerate the effect of stronger signals

        estimated_lat_sum += lat * weight
        estimated_lon_sum += lon * weight
        total_weight += weight

    if total_weight == 0: # Should not happen if data has varying RSSI
         estimated_ap_location = None
    else:
        estimated_ap_lat = estimated_lat_sum / total_weight
        estimated_ap_lon = estimated_lon_sum / total_weight
        estimated_ap_location = [estimated_ap_lat, estimated_ap_lon]

    # --- Step 2: Estimate Direction of Travel ---
    # We'll compare the first and last recorded data points to infer movement.
    first_rssi, first_lat, first_lon = signal_data[0]
    last_rssi, last_lat, last_lon = signal_data[-1]

    # Calculate distance moved by the receiver
    def haversine_distance(lat1, lon1, lat2, lon2):
        dlat = (lat2 - lat1) * DEG_TO_RAD
        dlon = (lon2 - lon1) * DEG_TO_RAD
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + \
            math.cos(lat1 * DEG_TO_RAD) * math.cos(lat2 * DEG_TO_RAD) * \
            math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R_EARTH * c # Distance in meters

    # Calculate distance from receiver to estimated AP for first and last points
    if estimated_ap_location:
        dist_first_to_ap = haversine_distance(first_lat, first_lon,
                                             estimated_ap_location[0], estimated_ap_location[1])
        dist_last_to_ap = haversine_distance(last_lat, last_lon,
                                            estimated_ap_location[0], estimated_ap_location[1])
    else:
        # If AP location can't be estimated, we can't infer direction relative to AP
        return None, "Cannot estimate AP location, thus cannot infer direction relative to AP."


    direction_description = ""
    # Compare RSSI change
    rssi_change = last_rssi - first_rssi # Positive means stronger signal

    # Compare distance change
    distance_change = dist_last_to_ap - dist_first_to_ap # Positive means farther from AP

    # Heuristics for direction of travel relative to AP
    if rssi_change > 0: # Signal got stronger
        direction_description += "You were likely moving **towards** the access point. "
        if distance_change < 0: # Also got physically closer (good consistency)
            direction_description += "Your path suggests getting closer to the AP. "
        else:
            direction_description += "Even though the signal strengthened, your estimated physical distance changed inconsistently, possibly due to signal fluctuations. "
    elif rssi_change < 0: # Signal got weaker
        direction_description += "You were likely moving **away from** the access point. "
        if distance_change > 0: # Also got physically farther (good consistency)
            direction_description += "Your path suggests getting farther from the AP. "
        else:
            direction_description += "Even though the signal weakened, your estimated physical distance changed inconsistently, possibly due to signal fluctuations. "
    else: # RSSI stayed the same
        direction_description += "Your signal strength remained constant. "
        if abs(distance_change) < 1: # Very little movement
            direction_description += "This suggests you either didn't move much relative to the AP, or you moved along an arc equidistant from it. "
        elif distance_change > 0:
            direction_description += "You moved farther away, despite constant RSSI, indicating highly complex signal environment. "
        else:
            direction_description += "You moved closer, despite constant RSSI, indicating highly complex signal environment. "

    # To provide a cardinal direction of travel (e.g., North, East) we need to calculate bearing.
    # This assumes true north, as magnetic declination would require an external library or lookup.
    def calculate_bearing(lat1, lon1, lat2, lon2):
        phi1 = math.radians(lat1)
        lambda1 = math.radians(lon1)
        phi2 = math.radians(lat2)
        lambda2 = math.radians(lon2)

        y = math.sin(lambda2 - lambda1) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - \
            math.sin(phi1) * math.cos(phi2) * math.cos(lambda2 - lambda1)

        bearing_rad = math.atan2(y, x)
        bearing_deg = (math.degrees(bearing_rad) + 360) % 360
        return bearing_deg

    if len(signal_data) >= 2:
        bearing = calculate_bearing(first_lat, first_lon, last_lat, last_lon)

        cardinal_direction = ""
        if 337.5 <= bearing < 22.5:
            cardinal_direction = "North"
        elif 22.5 <= bearing < 67.5:
            cardinal_direction = "Northeast"
        elif 67.5 <= bearing < 112.5:
            cardinal_direction = "East"
        elif 112.5 <= bearing < 157.5:
            cardinal_direction = "Southeast"
        elif 157.5 <= bearing < 202.5:
            cardinal_direction = "South"
        elif 202.5 <= bearing < 247.5:
            cardinal_direction = "Southwest"
        elif 247.5 <= bearing < 292.5:
            cardinal_direction = "West"
        elif 292.5 <= bearing < 337.5:
            cardinal_direction = "Northwest"

        direction_description += f"Your overall movement from the first to the last recorded point was approximately **{cardinal_direction}** (True North reference, {bearing:.1f}°). "

    return estimated_ap_location, direction_description


# The following code sets up the various threads that the rest of the program will use
#start the sensor loop
wifi_thread = Thread(target = threaded_wifi, args = ())
wifi_thread.start()


