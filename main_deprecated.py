#!/usr/bin/python

# Picorder - Version 2a!
# Program collects sensor data and displays it in sliders and graphs.
# Plays a video using OMX
# Displays modes using three LEDs
# Changes modes using three microswitches
# Uses interval timers to direct flow of program



# The following are some necessary modules for the Picorder.
import pygame
import os
import time
from filehandling import *

# If running on Pi use these imports:
#from gpiobasics import *
#from sensehatbasics import *

# If testing on PC use these imports:
from gpiodummy import *
from getcpu import *
from screens import *
from graph import *

# The following commands initiate a pygame environment.
pygame.init()
pygame.font.init()

# The following commands disable the mouse and cursor.
pygame.event.set_blocked(pygame.MOUSEMOTION)
pygame.mouse.set_visible(0)

# The following lists are for my colour standards.
red = (255,0,0)
green = (106,255,69)
blue = (99,157,255)
yellow = (255,221,5)
black = (0,0,0)
white = (255,255,255)

# The following lists/objects are for UI elements.
titleFont = "assets/babs.otf"
titleFont = "assets/babs.otf"
blueInsignia = pygame.image.load('assets/insigniablue.png')
backplane = pygame.image.load('assets/background.png')
backgraph = pygame.image.load('assets/backgraph.png')
slider = pygame.image.load('assets/slider.png')
sliderb = pygame.image.load('assets/slider2.png')
status = "startup"


pygame.display.set_icon(blueInsignia)

set_logging = False

# The following is a simple object that I can use to maintain toggled states. There's probably a better way to do it, but this is what I did!
class toggle(object):
    def __init__(self):
        self.setting = False

    def read(self):
        return self.setting

    def flip(self):
            if self.setting == True:
                self.setting = False
            else:
                self.setting = True

# The following class is used to display text
class Label(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.color = white
        self.fontSize = 33
        self.myfont = pygame.font.Font(titleFont, self.fontSize)

    def update(self, content, fontSize, nx, ny, fontType, color):
        self.x = nx
        self.y = ny
        self.content = content
        self.fontSize = fontSize
        self.myfont = pygame.font.Font(fontType, self.fontSize)
        self.color = color

    def draw(self, surface):
        label = self.myfont.render(self.content, 1, self.color)
        surface.blit(label, (self.x, self.y))

# the following class is used to display images
class Image(object):
    def __init__(self):
        self.x = 258
        self.y = 66
        self.Img = blueInsignia

    def update(self, image, nx, ny):
        self.x = nx
        self.y = ny
        self.Img = image


    def draw(self, surface):
        surface.blit(self.Img, (self.x,self.y))

# The following class is to keep track of whether a graph has been initiated or is to be reset. This allows me to refresh graphs if need be.
class initial(object):
        def __init__(self):
            self.go = 0

        def logstart(self):
            self.go = 1

        def reset(self):
            self.go = 0

        def get(self):
            return self.go

# the following class is used to make items flash by providing a timed pulse bit object.
class flash(object):
    def __init__(self):
     self.value = 0
     self.timelast = 0
     self.timenow = 0

    def pulse(self):

     if (self.timelast == 0):
         self.timelast = time.time()

     self.timenow = time.time()

     if ((self.timenow - self.timelast) >= 1):

         if (self.value == 1):
             self.value = 0
         else:
             self.value = 1

         self.timelast = time.time()

    def display(self):
     return self.value

# The following class is used to prepare sensordata for display on the graph.
class graphlist(object):

    # the following is constructor code to give each object a list suitable for storing all our graph data, in this case it is 145 spaces.
    def __init__(self):
        self.glist = []
        for i in range(145):
            self.glist.append(110.5)

    # the following function returns the list.
    def grablist(self):
        return self.glist

    # the following appends data to the list.
    def updatelist(self, data):
        #grabs a simple 15 wide tuple for our values
        #puts a new sensor value at the end
        self.buffer.append(data)
        #pop the oldest value off
        self.buffer.pop(0)

    # the following pairs the list of values with coordinates on the X axis. The supplied variables are the starting X coordinates and spacing between each point.
    def graphprep(self,list):
        linepoint = 15
        jump = 2
        self.newlist = []
        for i in range(145):
            self.newlist.append((linepoint,list[i]))
            linepoint = linepoint + jump

        return self.newlist

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

# The following function defines button behaviours and allows the program to query the button events and act accordingly.
def butswitch(status,graphinit,moire,rot,buttons):

	pygame.event.get()
	key = pygame.key.get_pressed()

	if key[pygame.K_RIGHT]:
		if (status == "slidergo"):
				graphinit.reset()
				status = "graphgo"
		elif(status == "graphgo"):
				graphinit.reset()
				status = "magnetgo"
		elif (status == "magnetgo"):
				graphinit.reset()
				status = "slidergo"

	if key[pygame.K_LEFT]:
		if (status == "slidergo"):
				graphinit.reset()
				status = "magnetgo"
		elif(status == "graphgo"):
				graphinit.reset()
				status = "slidergo"
		elif (status == "magnetgo"):
				graphinit.reset()
				status = "graphgo"

	button_readings = buttons.read()

	if (button_readings['buta']==True) and (button_readings['butb']==False) and (button_readings['butc']==False):
			if (status == "graphgo") or (status == "magnetgo"):
					graphinit.reset()
					status = "slidergo"


	if (button_readings['buta']==False) and (button_readings['butb']==True) and (button_readings['butc']==False):
			if (status == "slidergo"):
					graphinit.reset()
					status = "graphgo"
			elif(status == "graphgo"):
					graphinit.reset()
					status = "magnetgo"
			elif (status == "magnetgo"):
					graphinit.reset()
					status = "graphgo"

	if (button_readings['butc']==True):
			if (status == "slidergo"):
					rot.flip()
			elif(status == "graphgo"):
					moire.toggle()
			elif (status == "magnetgo"):
					moire.toggle()



		#os.system("omxplayer ekmd.mov")

	if (button_readings['buta']==False) and (button_readings['butb']==True) and (button_readings['butc']==True):
			os.system("omxplayer ekmd.mov")

	if (button_readings['buta']==True) and (button_readings['butb']==False) and (button_readings['butc']==True):
			moire.toggle()


	return status

# the following function maps a value from the target range onto the desination range
def translate(value, leftMin, leftMax, rightMin, rightMax):
	# Figure out how 'wide' each range is
	leftSpan = leftMax - leftMin
	rightSpan = rightMax - rightMin

	# Convert the left range into a 0-1 range (float)
	valueScaled = float(value - leftMin) / float(leftSpan)

	# Convert the 0-1 range into a value in the right range.
	return rightMin + (valueScaled * rightSpan)

# the following function runs the startup animation
def startUp(surface, timeSinceStart):
	#This function draws the opening splash screen for the program that provides the user with basic information.

	#Sets a black screen ready for our UI elements
	surface.fill(black)

	#Instantiates the components of the scene
	insignia = Image()
	mainTitle = Label()
	secTitle = Label()

	#sets out UI objects with the appropriate data
	insignia.update(blueInsignia, 115, 24)
	mainTitle.update("TR-108 Environmental Tricorder",25,22,181,titleFont,white)
	secTitle.update("STARFLEET R&D - Toronto - CLASS M ONLY",19,37,210,titleFont,blue)

	#writes our objects to the buffer
	insignia.draw(surface)

	#checks time
	timenow = time.time()

	#compares time just taken with time of start to animate the apperance of text
	if (timenow - timeSinceStart) > .5:
	 mainTitle.draw(surface)

	if (timenow - timeSinceStart) > 1:
	 secTitle.draw(surface)

	pygame.display.flip()

	#waits for 2 seconds to elapse before returning the state that will take us to the sensor readout
	if (timenow - timeSinceStart) < 2.5:
	 return "startup"
	else:
	 return "slidergo"

# the following function draws the main sensor readout screen
def sliderScreen(surface,moire,tock,buttons,csvfile,rot,graphinit,humidGraph,tempGraph,pressGraph,graphtock):
	# This function draws the main 3-slider interface, modelled after McCoy's tricorder in "Plato's Stepchildren". It displays temperature, humidity and pressure.
	if (tock.timelapsed() >= 0.4):

		# Sets a black screen ready for our UI elements
		surface.fill(black)

		# Cycles the Moire
		moire.animate()

		# Instantiates the components of the scene
		templabel = Label()
		presslabel = Label()
		humidlabel = Label()
		backPlane = Image()
		slider1 = Image()
		slider2 = Image()
		slider3 = Image()

		# Grabs data from our sensor/weather package (depends on what module is imported at the top)
		senseData = sensorget()


		# parses dictionary of data from sensor/weather
		tempData = str(int(senseData['temp']))
		pressData = str(int(senseData['pressure']))
		humidData = str(int(senseData['humidity']))


		# data labels
		templabel.update(tempData + "\xb0",19,47,215,titleFont,yellow)
		presslabel.update(pressData,19,152,215,titleFont,yellow)
		humidlabel.update(humidData,19,254,215,titleFont,yellow)

		# slider data adjustment
		tempslide = translate(senseData['temp'], -40, 120, 204, 15)
		pressslide = translate(senseData['pressure'], 260, 1260, 204, 15)
		humidslide = translate(senseData['humidity'], 0, 100, 204, 15)

		# Updates our UI objects with data parsed from sensor/weather
		backPlane.update(backplane, 0, 0)
		slider1.update(slider, 70, tempslide)
		slider2.update(slider, 172, pressslide)
		slider3.update(slider, 276, humidslide)

		# draws the graphic UI to the buffer
		backPlane.draw(surface)
		slider1.draw(surface)
		slider2.draw(surface)
		slider3.draw(surface)

		# draws the labels to the buffer
		templabel.draw(surface)
		presslabel.draw(surface)
		humidlabel.draw(surface)

		# draws UI to frame buffer
		if (rot.read() == True):
			surface.blit(pygame.transform.rotate(surface, 180), (0, 0))

		pygame.display.flip()
		tock.logtime()

		if graphtock.timelapsed() >= 64:
			humidData = float(senseData['humidity'])
			#scales the data to the limits of our screen
			humidgraph = translate(humidData, 0, 100, 204, 17)
			#grabs a simple 61 wide tuple for our values
			humidbuffer = humidGraph.grablist()
			#puts a new sensor value at the end
			humidbuffer.append(humidgraph)
			#pop the oldest value off
			humidbuffer.pop(0)
			#preps the list by adding the X coordinate to every sensor value
			humidcords = humidGraph.graphprep(humidbuffer)

			tempData = float(senseData['temp'])
			tempgraph = translate(tempData, -40, 120, 204, 17)
			tempbuffer = tempGraph.grablist()
			tempbuffer.append(tempgraph)
			tempbuffer.pop(0)
			tempcords = tempGraph.graphprep(tempbuffer)

			pressData = float(senseData['pressure'])
			pressgraph = translate(pressData, 260, 1260, 204, 17)
			pressbuffer = pressGraph.grablist()
			pressbuffer.append(pressgraph)
			pressbuffer.pop(0)
			presscords = pressGraph.graphprep(pressbuffer)

			if set_logging == True:
				csvfile.logvalues(senseData)

			graphtock.logtime()



	status = "slidergo"
	status = butswitch(status,graphinit,moire,rot,buttons)



		#returns state to main loop
	return status


# The following function plots the magneto sensors to an onscreen graph
def magnetScreen(surface,xGraph,yGraph,zGraph,moire,tock,graphinit,buttons,csvfile,rot):
	interval = (1)

	if (tock.timelapsed() >= interval):


		moire.animate()
		#Sets a black screen ready for our UI elements
		surface.fill(black)

		#draws Background gridplane
		graphback = Image()
		graphback.update(backgraph, 0, 0)
		graphback.draw(surface)

		#instantiates 3 labels for our readout
		xlabel = Label()
		ylabel = Label()
		zlabel = Label()
		intervallabel = Label()
		intervallabelshadow = Label()

		slider1 = Image()
		slider2 = Image()
		slider3 = Image()

		#gets our data
		senseData = sensorget()["compass"]
		if set_logging == True:
			csvfile.logvalues(senseData)

		#parses dictionary of data from sensor/weather

		#converts humid data to float
		xData = float(senseData['x'])
		#scales the data to the limits of our screen
		xgraph = translate(xData, -500, 500, 204, 17)
		#grabs a simple 61 wide tuple for our values
		xbuffer = xGraph.grablist()

		#puts a new sensor value at the end
		xbuffer.append(xgraph)
		#pop the oldest value off
		xbuffer.pop(0)

		#preps the list by adding the X coordinate to every sensor value
		xcords = xGraph.graphprep(xbuffer)

		#repeat for each sensor

		yData = float(senseData['y'])
		ygraph = translate(yData, -500, 500, 204, 17)
		ybuffer = yGraph.grablist()
		ybuffer.append(ygraph)
		ybuffer.pop(0)
		ycords = yGraph.graphprep(ybuffer)

		zData = float(senseData['z'])
		zgraph = translate(zData, -500, 500, 204, 17)
		zbuffer = zGraph.grablist()
		zbuffer.append(zgraph)
		zbuffer.pop(0)
		zcords = zGraph.graphprep(zbuffer)

		xslide = translate(senseData['x'], -500, 500, 194, 7)
		yslide = translate(senseData['y'], -500, 500, 194, 7)
		zslide = translate(senseData['z'], -500, 500, 194, 7)

		slider1.update(sliderb, 283, xslide)
		slider2.update(sliderb, 283, yslide)
		slider3.update(sliderb, 283, zslide)

		xcontent = str(int(xData))
		xlabel.update(xcontent + ' uT',30,35,205,titleFont,blue)
		ycontent = str(int(yData))
		ylabel.update(ycontent + ' uT',30,145,205,titleFont,green)
		zcontent = str(int(zData))
		zlabel.update(zcontent + ' uT',30,235,205,titleFont,white)
		#templabel.update(tempData + "\xb0",16,15,212,titleFont,yellow)

		##setting = str(float((interval/60)*64))
		setting = str(float(interval))

		intervaltext = (setting + ' sec')
		interx= (22)
		intery= (21)
		# intervallabel.update("~"+setting + " Hrs",30,22,167,titleFont,white)
		#intervallabelshadow.update(setting + " Hrs",30,24,169,titleFont,(100,100,100))
		intervallabel.update(intervaltext,30,interx,intery,titleFont,white)
		intervallabelshadow.update(intervaltext, 30, interx + 2, intery + 2 ,titleFont,(100,100,100))





		#draw the lines
		pygame.draw.lines(surface, blue, False, xcords, 3)
		pygame.draw.lines(surface, green, False, ycords, 3)
		pygame.draw.lines(surface, white, False, zcords, 3)

		slider1.draw(surface)
		slider2.draw(surface)
		slider3.draw(surface)

		xlabel.draw(surface)
		ylabel.draw(surface)
		zlabel.draw(surface)
		intervallabelshadow.draw(surface)
		intervallabel.draw(surface)

		#draws UI to frame buffer

		if (rot.read() == True):
			surface.blit(pygame.transform.rotate(surface, 180), (0, 0))

		pygame.display.flip()

	status = "magnetgo"
	#returns state to main loop

	status = butswitch(status,graphinit,moire,rot,buttons)

	#returns state to main loop
	return status

# the following function plots the environment sensors to an onscreen graph
def graphaScreen(surface,humidGraph,tempGraph,pressGraph,moire,tock,graphinit,buttons,csvfile,rot):
	status = "graphgo"
	drawinterval = 1 #64
	senseinterval = 10
	#337

	# Because the graph screen is slow to update it needs to pop a reading onto screen as soon as it is initiated I draw a value once and wait for the interval to lapse for the next draw. Once the interval has lapsed pop another value on screen.

	moire.animate()

	if (graphinit.get() == 0) or (tock.timelapsed() >= drawinterval):
		#Sets a black screen ready for our UI elements
		surface.fill(black)

		#draws Background gridplane
		graphback = Image()
		graphback.update(backgraph, 0, 0)
		graphback.draw(surface)

		#instantiates 3 labels for our readout
		templabel = Label()
		humidlabel = Label()
		presslabel = Label()
		intervallabel = Label()
		intervallabelshadow = Label()


		slider1 = Image()
		slider2 = Image()
		slider3 = Image()


		#gets our data
		senseData = sensorget()
		if set_logging == True:
			csvfile.logvalues(senseData)

		#parses dictionary of data from sensor/weather.

		#converts humid data to float
		humidData = float(senseData['humidity'])
		#scales the data to the limits of our screen
		humidgraph = translate(humidData, 0, 100, 204, 17)
		#grabs a simple 61 wide tuple for our values
		humidbuffer = humidGraph.grablist()

		#puts a new sensor value at the end
		humidbuffer.append(humidgraph)
		#pop the oldest value off
		humidbuffer.pop(0)

		#preps the list by adding the X coordinate to every sensor value
		humidcords = humidGraph.graphprep(humidbuffer)

		#repeat for each sensor

		tempData = float(senseData['temp'])
		tempgraph = translate(tempData, -40, 120, 204, 17)
		tempbuffer = tempGraph.grablist()
		tempbuffer.append(tempgraph)
		tempbuffer.pop(0)
		tempcords = tempGraph.graphprep(tempbuffer)

		pressData = float(senseData['pressure'])
		pressgraph = translate(pressData, 260, 1260, 204, 17)
		pressbuffer = pressGraph.grablist()
		pressbuffer.append(pressgraph)
		pressbuffer.pop(0)
		presscords = pressGraph.graphprep(pressbuffer)

		tempcontent = str(int(tempData))
		templabel.update(tempcontent + "\xb0" + " c",30,35,205,titleFont,red)
		presscontent = str(int(pressData))
		presslabel.update(presscontent + " hpa",30,114,205,titleFont,yellow)
		humidcontent = str(int(humidData))
		humidlabel.update(humidcontent + " %",30,246,205,titleFont,green)
		#templabel.update(tempData + "\xb0",16,15,212,titleFont,yellow)

		setting = str(float(drawinterval))
		intervaltext = (setting + ' sec')
		interx= (22)
		intery= (21)
	 # intervallabel.update("~"+setting + " Hrs",30,22,167,titleFont,white)
		#intervallabelshadow.update(setting + " Hrs",30,24,169,titleFont,(100,100,100))
		intervallabel.update(intervaltext,30,interx,intery,titleFont,white)
		intervallabelshadow.update(intervaltext, 30, interx + 2, intery + 2 ,titleFont,(100,100,100))

		tempslide = translate(senseData['temp'], -40, 120, 194, 7)
		pressslide = translate(senseData['pressure'], 260, 1260, 194, 7)
		humidslide = translate(senseData['humidity'], 0, 100, 194, 7)

		slider1.update(sliderb, 283, tempslide)
		slider2.update(sliderb, 283, pressslide)
		slider3.update(sliderb, 283, humidslide)


		#draw the lines

		pygame.draw.lines(surface, red, False, tempcords, 3)
		pygame.draw.lines(surface, green, False, humidcords, 3)
		pygame.draw.lines(surface, yellow, False, presscords, 3)

		templabel.draw(surface)
		presslabel.draw(surface)
		humidlabel.draw(surface)
		intervallabelshadow.draw(surface)
		intervallabel.draw(surface)

		#draws UI to frame buffer


		slider1.draw(surface)
		slider2.draw(surface)
		slider3.draw(surface)

		if (rot.read() == True):
			surface.blit(pygame.transform.rotate(surface, 180), (0, 0))

		pygame.display.flip()

		if (graphinit.get() == 0):
			graphinit.logstart()

		if (tock.timelapsed() >= 10):
			tock.logtime()

	#status = "graphgo"
	#returns state to main loop

	status = butswitch(status,graphinit,moire,rot,buttons)

	#button_readings = buttons.read()



	#returns state to main loop
	return status



# the following function is our main object, it contains all the flow for our program.
class Main(object):

    # set up an interval timer object, one for logging values, the other for drawing the screen.
    tock = timer()
    graphtock = timer()

    rot = toggle()

    # set up a file to store our sensor values to disk.
    csvfile = write_values()

    # set the screen resolution
    screenSize = (320,240)

    # I forget, probably colour depth?
    modes = pygame.display.list_modes(16)

    # instantiate a pygame display with the name "surface"
    surface = pygame.display.set_mode(screenSize)
#    surface = pygame.display.set_mode(screenSize, pygame.FULLSCREEN)

    # Create a time index to work from for the splash screen.
    timeSinceStart = time.time()

    # The Moire object controls the SenseHat's 8x8 LED Display.
    moire = led_display()

    # The Buttons object handles button events.
    buttons = debounce()

    # I put the sensor data into objects so they can be passed into functions and retain information outside the scope.
    humidGraph = graphlist()
    tempGraph = graphlist()
    pressGraph = graphlist()

    xGraph = graphlist()
    yGraph = graphlist()
    zGraph = graphlist()

    # tock.logtime() logs a starting point for my program. It could replace timeSinceStart and probably will one day.
    tock.logtime()
    graphtock.logtime()

    # graphinit is an object to make sure the graph screen never shows up blank or lags on being displayed when you switch to it.
    graphinit = initial()

    # The following while loop catches ctrl-c exceptions. I use this structure so that status changes will loop back around and have a chance to activate different functions. It gets a little weird going forward, bear with me.
    while (status != "quit"):
		try:

			# Using this loop as an example. This loop runs the startup animation played when you first boot the program.
			while(status == "startup"):
				# We activate each LED for a nice lamp test.
				leda_on()
				ledb_on()
				ledc_on()

				# A simple pygame.time.wait allows the program to take a break through the cycle so it's not loading up the CPU with draws to screen. I just saved 75% of my CPU by switching to this.
				pygame.time.wait(33)
				# This next item grabs the pygame events, which includes keyboard events.
				pygame.event.get()
				# this next item checks to see if the q key was pressed
				key = pygame.key.get_pressed()
				# and if so breaks the loop and gets us to the shut down commands.
				if key[pygame.K_q]:
					cleangpio()
					clearled()
					status = "quit"
				else:
					# otherwise it updates the status by calling on the startUp function, which is passed our pygame display object, and the time since we booted our program.
					status = startUp(surface,timeSinceStart)

			# The rest of these loops all handle a different mode, switched by buttons within the functions.
			while(status == "slidergo"):
				leda_on()
				ledb_off()
				ledc_off()
				pygame.event.get()
				pygame.time.wait(50)
				key = pygame.key.get_pressed()

				if key[pygame.K_q]:
					cleangpio()
					clearled()
					status = "quit"
				else:
					status = sliderScreen(surface,moire,tock,buttons,csvfile,rot,graphinit,humidGraph,tempGraph,pressGraph,graphtock)



			while(status == "graphgo"):
				leda_off()
				ledb_on()
				ledc_off()
				pygame.event.get()
				pygame.time.wait(50)
				key = pygame.key.get_pressed()
				if key[pygame.K_q]:
					cleangpio()
					clearled()
					status = "quit"
				else:
					status = graphScreen(surface,humidGraph,tempGraph,pressGraph,moire,graphtock,graphinit,buttons,csvfile,rot)


			while (status == "magnetgo"):
				leda_off()
				ledb_on()
				ledc_off()
				pygame.event.get()
				pygame.time.wait(50)
				key = pygame.key.get_pressed()
				if key[pygame.K_q]:
					cleangpio()
					clearled()
					status = "quit"
				else:
					#timeStart=time.time()
					status = magnetScreen(surface,xGraph,yGraph,zGraph,moire,tock,graphinit,buttons,csvfile,rot)

		# If CTRL-C is received the program gracefully turns off the LEDs and resets the GPIO.
		except KeyboardInterrupt:
			clearled()
			cleangpio()
			status = "quit"

# the following call starts our program
Main()
