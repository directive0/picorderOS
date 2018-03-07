import time

# The following class is to handle interval timers.
class timer(object):

    # Constructor code logs the time it was instantiated.    
    def __init__(self):
        self.timeInit = time.time()

    # The following funtion returns the last logged value.        
    def timestart(self):
        return self.timeInit
        
    # the following function updates the time log with the current time.
    def logtime(self):
        self.lastTime = time.time()

    # the following function returns the interval that has elapsed since the last log.        
    def timelapsed(self):
        self.timeLapse = time.time() - self.lastTime
        #print(self.timeLapse)
        return self.timeLapse

