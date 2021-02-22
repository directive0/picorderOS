# test file for pandas development

from sensors import *
from plars import *
import time
# create a PLARS object
testplars = PLARS()

sensordata = Sensor()

testplars.update(sensordata)
