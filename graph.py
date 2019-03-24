from objects import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw





# The following class is used to prepare sensordata for display on the graph.     
class graphlist(object):

    # the following is constructor code to give each object a list suitable for storing all our graph data.
    def __init__(self, sourcerange, graphcoords, graphspan, cycle = 10):
        
        self.cycle = cycle
        self.tock = timer()
        self.tock.logtime()
        self.glist = []
        self.dlist = []
        
        self.auto = True
        
        # collect data for translating sensor readings into pixel locations
        self.sourcerange = sourcerange
        self.low,self.high = self.sourcerange
        
        #collect data for where the graph should be drawn to screen.
        self.x, self.y = graphcoords
        self.spanx,self.spany = graphspan
        
        self.targetrange = (self.y,(self.y + self.spany))
        
        # seeds a list with the coordinates for 0 to give us a list that we can put our scaled graph values in
        for i in range(self.spanx):
            self.glist.append(self.y + self.spany)
        
        # seeds a list with sourcerange zero so we can put our sensor readings into it.
        for i in range(self.spanx):
            self.dlist.append(self.low)
        

    # the following function returns the graph list.    
    def grabglist(self):
        return self.glist
    # the following function returns the data list.
    def grabdlist(self):
        return self.dlist
    
    # this function calculates the approximate time scale of the graph
    def giveperiod(self):
        self.period = (self.spanx * self.cycle) / 60
        
        return self.period
    
    # the following appends data to the list.        
    
    def update(self, data):

        #grabs a simple 15 wide tuple for our values
        self.buff = self.grabdlist()

        # if the time elapsed has reached the set interval then collect data
        if self.tock.timelapsed() >= self.cycle: 
            
            # we load new data from the caller
            self.cleandata = data
            
            #append it to our list of clean data
            self.buff.append(self.cleandata)
            
            #pop the oldest value off
            # may remove this
            self.buff.pop(0)
            self.tock.logtime()


    # the following pairs the list of values with coordinates on the X axis. The supplied variables are the starting X coordinates and spacing between each point.    
    # if the auto flad is set then the class will autoscale the graph so that the highest and lowest currently displayed values are presented.
    def graphprep(self,datalist):
        self.linepoint = self.x
        self.jump = 1
        self.newlist = []
        
        if self.auto == True:
            self.datahigh = max(self.dlist)
            self.datalow = min(self.dlist)
            self.newrange = (self.datalow,self.datahigh)
        
        for i in range(self.spanx):
            if self.auto == True:
                scaledata = self.translate(datalist[i], self.newrange, self.targetrange)
            else:
                scaledata = self.translate(datalist[i], self.sourcerange, self.targetrange)
                
            self.newlist.append((self.linepoint,scaledata))
            self.linepoint = self.linepoint + self.jump
    
        return self.newlist
        
    # the following function maps a value from the target range onto the desination range   
    def translate(self,value,source,target):
        # Figure out how 'wide' each range is
        
        leftMax,leftMin = source
        rightMin,rightMax = target
        
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin
    
        # Convert the left range into a 0-1 range (float)
        if leftSpan == 0:
            return rightMin + rightSpan / 2
            
        valueScaled = float(value - leftMin) / float(leftSpan)
    
        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)
        
    def render(self, draw, auto = True):
        
        self.auto = auto
        #preps the list by adding the X coordinate to every sensor value
        cords = self.graphprep(self.buff)
        
        draw.line(cords,0,1)
        #for i in range(self.spanx):
            #curx,cury = cords[i]
            #draw.chord(cords[i-1],curx,cury,0)
            #draw.point(cords[i],0)
            
