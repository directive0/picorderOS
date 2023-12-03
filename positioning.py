import serial,time
from pynmeagps import NMEAReader
from multiprocessing import Process,Queue,Pipe

# Serial UART address
port = '/dev/ttyUSB0'
baud = 9600

serialPort = serial.Serial(port, baudrate = baud, timeout = 0.5)

# function to collect GPS data as a process.
def GPS_process(conn):
	while True:
		lat = 47.98
		lon = 47.98
		stream = serial.Serial(port, 9600, timeout=3)
		nmr = NMEAReader(stream)
		(raw_data, parsed_data) = nmr.read()

		if hasattr(parsed_data, "lat"):

			if parsed_data.lat != '':
				lat = float(parsed_data.lat)

			if parsed_data.lon != '':
				lon = float(parsed_data.lon)

		conn.send([lat,lon])

def threaded_GPS(conn):

	item = parent_conn.recv()

	if hasattr(item, "lat"):
			print(item.lat, ",",  item.lon)

def test_GPS():
	parent_conn,child_conn = Pipe()
	gps_process = Process(target=GPS_process, args=(child_conn,))
	gps_process.start()


	while True:
		threaded_GPS(parent_conn)