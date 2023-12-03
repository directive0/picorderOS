import serial,time
from pynmeagps import NMEAReader
from multiprocessing import Process,Queue,Pipe

# Serial UART address
port = '/dev/ttyUSB0'
baud = 9600

serialPort = serial.Serial(port, baudrate = baud, timeout = 0.5)

def GPS_function():
		

		gps_update = {"lat" : 47.98, "lon" : 47.98, "speed" : 0.00, "track" : 0.00}

		stream = serial.Serial(port, 9600, timeout=3)
		nmr = NMEAReader(stream)
		(raw_data, parsed_data) = nmr.read()

		if hasattr(parsed_data, "lat"):

			if parsed_data.lat != '':
				gps_update["lat"] = float(parsed_data.lat)

			if parsed_data.lon != '':
				gps_update["lon"] = float(parsed_data.lon)
		return gps_update


# function to collect GPS data as a process.
def GPS_process(conn):
	while True:
		lat,lon = GPS_function()
		conn.send([lat,lon])

def threaded_GPS(conn):
	item = conn.recv()

def test_GPS():
	parent_conn,child_conn = Pipe()
	gps_process = Process(target=GPS_process, args=(child_conn,))
	gps_process.start()


	while True:
		threaded_GPS(parent_conn)