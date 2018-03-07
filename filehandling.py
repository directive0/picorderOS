#!/usr/bin/python
import time

class write_values(object):
    
    def __init__(self):    
        self.d1 = str((time.strftime("%d-%m-%Y")))
        file = open("log/" + self.d1 + '-loggedvals.csv', 'a')

        file.write("Date, Time, Humidity, Pressure, Temperature, MagX, MagY, MagZ" + "\r")
    
    def logvalues(self, sensors):
        self.d1 = str((time.strftime("%d-%m-%Y")))
        file = open("log/" + self.d1 + '-loggedvals.csv', 'a')
        self.t = str((time.strftime("%H:%M:%S")))
        self.d = str((time.strftime("%d/%m/%Y")))
        self.temp = str(sensors['temp'])
        self.press = str(sensors['pressure'])
        self.humid = str(sensors['humidity'])
        self.x = str(sensors['x'])
        self.y = str(sensors['y'])
        self.z = str(sensors['z'])
#        file.write("/log/" + self.d + "," + self.t + "," + str(sensors['humidity']) + "," + str(sensors['pressure']) + str(sensors['temp']) + "\r")
        file.write( self.d + "," + self.t + "," + self.humid + "," + self.press + "," + self.temp + ","+ self.x + "," + self.y + "," + self.z + "\r")
        print('logged a value to file!' + "\r")
        print( "Time: " + self.d + " Date: " + self.t + " Humdity:" + self.humid + " Pressure:" + self.press + " Temperature:" + self.temp + " X:"+ self.x + " Y:" + self.y + " Z:" + self.z + "\r")
        
    def end_file():
        file.write("END OF LOG")
    