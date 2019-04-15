 #!/usr/bin/python

# This display module uses Pygame to draw picorder routines to the screen.

# The following are some necessary modules for the Picorder.
import pygame
import time
from objects import *
from gpiobasics import *
#
# The following commands initiate a pygame environment.
pygame.init()
pygame.font.init()
pygame.display.set_caption('PicorderOS')

# The following commands disable the mouse and cursor.
#pygame.event.set_blocked(pygame.MOUSEMOTION)
#pygame.mouse.set_visible(0)

# set the screen configuration
resolution = (320,240)
def_modes = 16
refreshrate = 1


# The following lists are for my colour standards.
red = (255,0,0)
green = (106,255,69)
blue = (99,157,255)
yellow = (255,221,5)
black = (0,0,0)
white = (255,255,255)

# The following are for LCARS colours from LCARScom.net
lcars_orange = (255,153,0)
lcars_pink = (204,153,204)
lcars_blue = (153,153,204)
lcars_red = (204,102,102)
lcars_peach = (255,204,153)
lcars_bluer = (153,153,255)
lcars_orpeach = (255,153,102)
lcars_pinker = (204,102,153)



# The following lists/objects are for UI elements.
titleFont = "assets/babs.otf"
titleFont = "assets/babs.otf"
blueInsignia = pygame.image.load('assets/icon.png')
pioslogo = pygame.image.load('assets/picorderOS_logo.png')
backplane = pygame.image.load('assets/background.png')
backgraph = pygame.image.load('assets/backgraph.png')
slidera = pygame.image.load('assets/slider.png')
sliderb = pygame.image.load('assets/slider2.png')
status = "startup"

# sets the icon for the program (will show up in docks/taskbars on PCs)
pygame.display.set_icon(blueInsignia)

# The following function defines button behaviours and allows the program to query the button events and act accordingly.
def butswitch(gpio_state):

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

	button_readings = gpio_state.read()

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

# the following class defines simple text labels
# todo: Make labels self center withr ref to screen or within envelope.
class Label(object):
	def __init__(self):
		self.x = 0
		self.y = 0
		self.color = white
		self.fontSize = 33
		self.myfont = pygame.font.Font(titleFont, self.fontSize)
		text = "hello"
		self.size = self.myfont.size(text)
		self.scaler = 3

	def update(self, content, fontSize, nx, ny, fontType, color):
		self.x = nx
		self.y = ny
		self.content = content
		self.fontSize = fontSize
		self.myfont = pygame.font.Font(fontType, self.fontSize)
		self.color = color
	
	def get_size(self, content):
		width, height = self.myfont.size(content)
		return width
		
	def center(self,w,h,x,y):
		size = self.getrect()
		xmid = x + w/2
		ymid = y + h/2
		textposx = xmid - (size[0]/2)
		textposy = ymid - (size[1]/2) + self.scaler
		self.update(self.content,self.fontSize,textposx,textposy,titleFont,self.color)

	def draw(self, surface):
		label = self.myfont.render(self.content, 1, self.color)

		surface.blit(label, (self.x, self.y))

	def getrect(self):
		label = self.myfont.render(self.content, 1, self.color)
		textw = label.get_width()
		texth = label.get_height()

		return textw,texth
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
		self.glist.append(data)
		#pop the oldest value off
		self.glist.pop(0)

	# the following pairs the list of values with coordinates on the X axis. The supplied variables are the starting X coordinates and spacing between each point.
	def graphprep(self,list):
		linepoint = 15
		jump = 2
		self.newlist = []
		for i in range(145):
			self.newlist.append((linepoint,list[i]))
			linepoint = linepoint + jump

		return self.newlist

# the following function runs the startup animation
def startUp(surface,timeSinceStart):
	#This function draws the opening splash screen for the program that provides the user with basic information.

	#Sets a black screen ready for our UI elements
	surface.fill(black)

	#Instantiates the components of the scene
	insignia = Image()
	mainTitle = Label()
	secTitle = Label()

	logoposx = (resolution[0]/2) - (226/2)
	#sets out UI objects with the appropriate data
	insignia.update(pioslogo, logoposx, 60)
	mainTitle.update("Picorder OS",25,22,181,titleFont,white)
	mainTitle.center(resolution[0],20,0,181)
	secTitle.update("Alpha Test Version - March 2019",19,37,210,titleFont,blue)
	secTitle.center(resolution[0],20,0,210)

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
	if (timenow - timeSinceStart) < 2:
	 return "startup"
	else:
	 return "ready"

# the following function draws the main sensor readout screen
def slider(surface,senseData,tock, a = "temp", b = "pressure", c = "humidity"):
	# This function draws the main 3-slider interface, modelled after McCoy's tricorder in "Plato's Stepchildren". It displays temperature, humidity and pressure.

	#checks time
	timenow = time.time()

	#compares time just taken with time of start to animate the apperance of text
	#print(timenow - tock.timed)
	# Sets a black screen ready for our UI elements
	surface.fill(black)

	# Instantiates the components of the scene
	a_label = Label()
	b_label = Label()
	c_label = Label()
	backPlane = Image()

	slider1 = Image()
	slider2 = Image()
	slider3 = Image()

	# Grabs data from our sensor/weather package (depends on what module is imported at the top)
	#senseData = sensorget()


	# parses dictionary of data from sensor/weather based on the
	a_data = str(int(senseData[a]))
	b_data = str(int(senseData[b]))
	c_data = str(int(senseData[c]))


	# data labels
	a_label.update(a_data + "\xb0",19,47,215,titleFont,yellow)
	b_label.update(b_data,19,152,215,titleFont,yellow)
	c_label.update(c_data,19,254,215,titleFont,yellow)

	#print(str(senseData['temp'])+" "+ str(senseData['pressure']) + " " + str(senseData['humidity']))
	# slider data adjustment
	# the routine takes the raw sensor data and converts it to screen coordinates to move the sliders
	a_slide = translate(senseData['temp'], -40, 120, 204, 15)
	b_slide = translate(senseData['pressure'], 260, 1260, 204, 15)
	c_slide = translate(senseData['humidity'], 0.0, 100.0, 204, 15)

	# Updates our UI objects with data parsed from sensor/weather
	backPlane.update(backplane, 0, 0)
	slider1.update(slidera, 70, a_slide)
	slider2.update(slidera, 172, b_slide)
	slider3.update(slidera, 276, c_slide)

	# draws the graphic UI to the buffer
	backPlane.draw(surface)
	slider1.draw(surface)
	slider2.draw(surface)
	slider3.draw(surface)

	# draws the labels to the buffer
	a_label.draw(surface)
	b_label.draw(surface)
	c_label.draw(surface)

	# draws UI to frame buffer
	#if (rot.read() == True): < can flip screen if necessary
	#surface.blit(pygame.transform.rotate(surface, 180), (0, 0))

	pygame.display.flip()
	#tock.timed = time.time()

	status = "mode_a"
		#returns state to main loop
	return status

# graphit is a quick tool to help prepare graphs
def graphit(data,new, auto = True):

	#puts a new sensor value at the end
	data.updatelist(new[0])

	#grabs our databuffer object.
	buffer = data.grablist()

	prep = []

	data_high = max(buffer)
	data_low = min(buffer)
	#print(new)
	for i in data.grablist():
		if auto:
			prep.append(translate(i, data_low, data_high, 204, 17))
		else:
			prep.append(translate(i, new[1], new[2], 204, 17))

	return data.graphprep(prep)


def keypress():
	pygame.event.get()
	#pygame.time.wait(50)
	key = pygame.key.get_pressed()

	return key

# A basic screen object. Is given parameters and displays them on a number of preset panels
class Screen(object):

	def __init__(self):
		screenSize = resolution

		# I forget, probably colour depth?
		smodes = pygame.display.list_modes(def_modes)

		# instantiate a pygame display with the name "surface",

		#for development use this one (windowed mode)
		self.surface = pygame.display.set_mode(screenSize)

		# on the picorder use this option.
		#self.surface = pygame.display.set_mode(screenSize, pygame.FULLSCREEN)

		self.timed = time.time()
		self.graphscreen = Graph_Screen(self.surface)
		
		self.io = debounce()
		self.lights = ripple()

	def startup_screen(self,start_time):
		pygame.event.get()
		#pygame.time.wait(50)
		key = pygame.key.get_pressed()

		status = startUp(self.surface,start_time)

		if key[pygame.K_q]:
			status = "quit"

		return status

	def slider_screen(self,sensors):

		status = slider(self.surface,sensors,self.timed)

		key = keypress()

		if key[pygame.K_q]:
			status = "quit"

		return status
		#return grapher(self.surface,sensors,self.data_a,self.data_b,self.data_c)

	def graph_screen(self,sensors):
		self.lights.cycle()
		status = self.graphscreen.frame(sensors)
		self.io.read()
		key = keypress()

		if key[pygame.K_q]:
			status = "quit"

		return status

	def modeb(self):
		pass

	def modec(self):
		pass

# The graph screen object is a self contained screen that is fed the surface and the sensor at the current moment and draws a frame when called.
class Graph_Screen(object):

	def __init__(self,surface):

		self.auto = True

		self.status = "mode_a"
		self.drawinterval = 1
		self.senseinterval = 10
		self.surface = surface


		#draws Background gridplane
		self.graphback = Image()
		self.graphback.update(backgraph, 0, 0)
		#self.graphback.draw(surface)

		#instantiates 3 labels for our readout
		self.a_label = Label()
		self.b_label = Label()
		self.c_label = Label()
		self.intervallabel = Label()
		self.intervallabelshadow = Label()

		self.slider1 = Image()
		self.slider2 = Image()
		self.slider3 = Image()

		self.data_a = graphlist()
		self.data_b = graphlist()
		self.data_c = graphlist()

		self.graphon1 = True
		self.graphon2 = True
		self.graphon3 = True

		self.visibility = [self.graphon1,self.graphon2,self.graphon3]


	def frame(self,sensors):
		# Because the graph screen is slow to update it needs to pop a reading onto screen as soon as it is initiated I draw a value once and wait for the interval to lapse for the next draw. Once the interval has lapsed pop another value on screen.
		#Sets a black screen ready for our UI elements
		self.surface.fill(black)

		#draws Background gridplane
		self.graphback.draw(self.surface)


		#a_info = sensors[0][1]
		#b_info = sensors[1][1]
		#c_info = sensors[2][1]

		#print(sensors)
		#converts data to float
		a_newest = float(sensors[0][0])

		# updates the data storage object and retrieves a fresh graph ready to
		a_cords = graphit(self.data_a,sensors[0], auto = self.auto)

		#repeat for each sensor
		b_newest = float(sensors[1][0])
		b_cords = graphit(self.data_b,sensors[1], auto = self.auto)

		c_newest = float(sensors[2][0])
		c_cords = graphit(self.data_c,sensors[2], auto = self.auto)

		a_content = str(int(a_newest))
		
		self.a_label.update(a_content + sensors[0][4],30,15,205,titleFont,red)

		c_content = str(int(c_newest))
		c_position = resolution[0] - (self.c_label.get_size(c_content + sensors[2][4])+15)
		self.c_label.update(c_content + sensors[2][4],30,c_position,205,titleFont,yellow)

		b_content = str(int(b_newest))
		self.b_label.update(b_content + sensors[1][4],30,114,205,titleFont,green)
		self.b_label.center(resolution[0],31,0,205)

		setting = str(float(self.drawinterval))
		intervaltext = (setting + ' sec')
		interx= (22)
		intery= (21)


		self.intervallabel.update(intervaltext,30,interx,intery,titleFont,white)
		self.intervallabelshadow.update(intervaltext, 30, interx + 2, intery + 2 ,titleFont,(100,100,100))



		a_slide = translate(a_newest, sensors[0][1], sensors[0][2], 194, 7)


		b_slide = translate(b_newest, sensors[1][1], sensors[1][2], 194, 7)


		c_slide = translate(c_newest, sensors[2][1], sensors[2][2], 194, 7)

		self.slider1.update(sliderb, 283, a_slide)
		self.slider2.update(sliderb, 283, b_slide)
		self.slider3.update(sliderb, 283, c_slide)


		#draw the lines
		if self.graphon1:
			pygame.draw.lines(self.surface, red, False, a_cords, 2)
			self.a_label.draw(self.surface)
			self.slider1.draw(self.surface)

		if self.graphon2:
			pygame.draw.lines(self.surface, green, False, b_cords, 2)
			self.b_label.draw(self.surface)
			self.slider2.draw(self.surface)

		if self.graphon3:
			pygame.draw.lines(self.surface, yellow, False, c_cords, 2)
			self.c_label.draw(self.surface)
			self.slider3.draw(self.surface)

		#
		#
		self.intervallabelshadow.draw(self.surface)
		self.intervallabel.draw(self.surface)

		#draws UI to frame buffer








		pygame.display.flip()

		#returns state to main loop
		return self.status

	def visible(self,item,option):
		self.visibility[item] = option







# # the following function plots the environment sensors to an onscreen graph. It represent one frame.
# def grapher(surface, sensors, data_a, data_b, data_c, a = "humidity", b = "temp", c = "pressure"):
# 	status = "mode_a"
# 	drawinterval = 1
# 	senseinterval = 10
#
# 	# Because the graph screen is slow to update it needs to pop a reading onto screen as soon as it is initiated I draw a value once and wait for the interval to lapse for the next draw. Once the interval has lapsed pop another value on screen.
# 	#Sets a black screen ready for our UI elements
# 	surface.fill(black)
#
# 	#draws Background gridplane
# 	graphback = Image()
# 	graphback.update(backgraph, 0, 0)
# 	graphback.draw(surface)
#
# 	#instantiates 3 labels for our readout
# 	a_label = Label()
# 	b_label = Label()
# 	c_label = Label()
# 	intervallabel = Label()
# 	intervallabelshadow = Label()
#
# 	slider1 = Image()
# 	slider2 = Image()
# 	slider3 = Image()
#
#
#
# 	#converts data to float
# 	a_newest = float(sensors[0][0])
#
# 	# updates the data storage object and retrieves a fresh graph ready to
# 	a_cords = graphit(data_a,sensors[0], auto = False)
#
# 	#repeat for each sensor
# 	b_newest = float(sensors[1][0])
# 	b_cords = graphit(data_b,sensors[1], auto = False)
#
# 	c_newest = float(sensors[2][0])
# 	c_cords = graphit(data_c,sensors[2], auto = False)
#
# 	a_content = str(int(b_newest))
# 	a_label.update(a_content + "\xb0" + " c",30,35,205,titleFont,red)
# 	c_content = str(int(c_newest))
# 	c_label.update(c_content + " hpa",30,114,205,titleFont,yellow)
# 	b_content = str(int(a_newest))
# 	b_label.update(b_content + " %",30,246,205,titleFont,green)
# 	#a_label.update(b_data + "\xb0",16,15,212,titleFont,yellow)
#
# 	setting = str(float(drawinterval))
# 	intervaltext = (setting + ' sec')
# 	interx= (22)
# 	intery= (21)
#
#
# 	intervallabel.update(intervaltext,30,interx,intery,titleFont,white)
# 	intervallabelshadow.update(intervaltext, 30, interx + 2, intery + 2 ,titleFont,(100,100,100))
#
#
# 	a_info = sensors[0][1]
# 	a_slide = translate(a_newest, a_info[0], a_info[1], 194, 7)
#
# 	b_info = sensors[1][1]
# 	b_slide = translate(b_newest, b_info[0], b_info[1], 194, 7)
#
# 	c_info = sensors[2][1]
# 	c_slide = translate(c_newest, c_info[0], c_info[1], 194, 7)
#
# 	slider1.update(sliderb, 283, a_slide)
# 	slider2.update(sliderb, 283, b_slide)
# 	slider3.update(sliderb, 283, c_slide)
#
#
# 	#draw the lines
# 	pygame.draw.lines(surface, green, False, a_cords, 2)
#
# 	pygame.draw.lines(surface, red, False, b_cords, 2)
#
# 	pygame.draw.lines(surface, yellow, False, c_cords, 2)
#
# 	a_label.draw(surface)
# 	c_label.draw(surface)
# 	b_label.draw(surface)
# 	intervallabelshadow.draw(surface)
# 	intervallabel.draw(surface)
#
# 	#draws UI to frame buffer
#
#
# 	slider1.draw(surface)
# 	slider2.draw(surface)
# 	slider3.draw(surface)
#
#
#
# 	pygame.display.flip()
#
# 	#returns state to main loop
# 	return status
