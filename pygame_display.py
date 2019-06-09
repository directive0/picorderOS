 #!/usr/bin/python

# This display module uses Pygame to draw picorder routines to the screen.

# The following are some necessary modules for the Picorder.
import pygame
import time
from objects import *
from input import *
#from gpiobasics import *
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
orange = (255,192,2)
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
blueInsignia = pygame.image.load('assets/icon.png')
pioslogo = pygame.image.load('assets/picorderOS_logo.png')
backplane = pygame.image.load('assets/background.png')
backgraph = pygame.image.load('assets/backgraph.png')
slidera = pygame.image.load('assets/slider.png')
sliderb = pygame.image.load('assets/slider2.png')
status = "startup"
last_status = "startup"

# sets the icon for the program (will show up in docks/taskbars on PCs)
pygame.display.set_icon(blueInsignia)



# The following function defines button behaviours and allows the program to query the button events and act accordingly.
def butswitch():
	pygame.event.get()
	key = pygame.key.get_pressed()
	message = []

	if key[pygame.K_RIGHT]:
		message += ["right"]

	if key[pygame.K_LEFT]:
		message += ["left"]

	if key[pygame.K_UP]:
		message += ["up"]

	if key[pygame.K_a]:
		print("key a")
		configure.auto[0] = not configure.auto[0]

	return message

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

class SelectableLabel(Label):
	def __init__(self, oper, special = 0):
		self.special = special
		self.x = 0
		self.y = 0
		self.color = white
		self.fontSize = 33
		self.myfont = pygame.font.Font(titleFont, self.fontSize)
		text = "Basic Item"
		self.size = self.myfont.size(text)
		self.scaler = 3
		self.selected = False
		self.indicator = Image()
		self.content = "default"
		self.oper = oper

	def update(self, content, fontSize, nx, ny, fontType, color):
		self.x = nx
		self.y = ny
		self.content = content
		self.fontSize = fontSize
		self.myfont = pygame.font.Font(fontType, self.fontSize)
		self.color = color
		self.indicator.update(sliderb, nx - 23, ny+1)

	def toggle(self):
		print(self.oper)
		if isinstance(self.oper[0], bool):
			self.oper[0] = not self.oper[0]
		elif isinstance(self.oper[0], int):
			self.oper[0] += 1
			if self.oper[0] > configure.max_sensors[0]-1:
				self.oper[0] = 0
		return self.oper[0]

	def draw(self, surface):
		if self.selected:
			self.indicator.draw(surface)

		label = self.myfont.render(self.content, 1, self.color)


		status_text = "dummy"
		if self.special == 0:
			status_text = str(self.oper[0])
		else:
			#print(configure.sensor_info)
			status_text = configure.sensor_info[self.oper[0]][3]

		pos = resolution[0] - (self.get_size(status_text) + 37)
		state = self.myfont.render(status_text, 1, self.color)


		surface.blit(label, (self.x, self.y))
		surface.blit(state, (pos, self.y))

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
		if configure.auto[0]:
			prep.append(translate(i, data_low, data_high, 204, 17))
		else:
			prep.append(translate(i, new[1], new[2], 204, 17))

	return data.graphprep(prep)


class Settings_Panel(object):

	def __init__(self,surface,input):

		self.left_margin = 37
		self.input = input
		self.index = 0
		self.surface = surface

		self.titlelabel = Label()
		self.titlelabel.update("Picorder OS Control Panel",25,17,15,titleFont,orange)


		self.option1 = SelectableLabel(configure.sensor1, special = 1)
		self.option1.update("Graph 1: ",20,self.left_margin,47,titleFont,red)

		self.option2 = SelectableLabel(configure.sensor2, special = 1)
		self.option2.update("Graph 2: ", 20, self.left_margin, 68, titleFont, green)

		self.option3 = SelectableLabel(configure.sensor3, special = 1)
		self.option3.update("Graph 3: ", 20, self.left_margin, 90, titleFont, yellow)

		self.option4 = SelectableLabel(configure.auto)
		self.option4.update("Auto Ranging:  ", 20, self.left_margin, 111, titleFont, orange)

		self.option5 = SelectableLabel(configure.leds)
		self.option5.update("Moire: ", 20, self.left_margin, 132, titleFont, orange)

		self.options = [self.option1,self.option2,self.option3,self.option4,self.option5]

	def frame(self):

		self.surface.fill(black)

		self.titlelabel.draw(self.surface)

		#self.options[self.index].selected = True

		for i in range(len(self.options)):
			if i == self.index:
				self.options[i].selected = True
			else:
				self.options[i].selected = False

			self.options[i].draw(self.surface)

		# for i in range(len(self.statuses)):
		# 	self.statuses[i].draw(self.surface,sensors)


		pygame.display.flip()

		result = "settings"
		print(configure.last_status[0])
		# draws UI to frame buffer
		#if (rot.read() == True): < can flip screen if necessary
		#surface.blit(pygame.transform.rotate(surface, 180), (0, 0))

		keys = self.input.read()
		#print(self.input.read())
		if keys[0]:
			if self.input.is_down(0):
				self.index += 1

				if self.index > (len(self.options) - 1):
					self.index = 0

		if keys[1]:
			if self.input.is_down(1):
				self.options[self.index].toggle()

		if keys[2]:
			if self.input.is_down(2):
				result = configure.last_status[0]

		return result


# The graph screen object is a self contained screen that is fed the surface and the sensor at the current moment and draws a frame when called.
class Graph_Screen(object):

	# Draws three graphs in a grid and three corresponding labels.

	def __init__(self,surface,input):

		self.input = input
		# State variable
		self.status = "mode_a"

		# An fps controller
		self.drawinterval = timer()

		# Sample rate controller
		self.senseinterval = 10

		# Pygame drawing surface.
		self.surface = surface


		# Draws Background gridplane
		self.graphback = Image()
		self.graphback.update(backgraph, 0, 0)
		#self.graphback.draw(surface)

		# Instantiates 3 labels for our readout
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

		#converts data to float
		a_newest = float(sensors[configure.sensor1[0]][0])

		# updates the data storage object and retrieves a fresh graph ready to store the positions of each segment for the line drawing
		a_cords = graphit(self.data_a,sensors[configure.sensor1[0]])

		#repeat for each sensor
		b_newest = float(sensors[configure.sensor2[0]][0])
		b_cords = graphit(self.data_b,sensors[configure.sensor2[0]])

		c_newest = float(sensors[configure.sensor3[0]][0])
		c_cords = graphit(self.data_c,sensors[configure.sensor3[0]])

		a_content = str(int(a_newest))
		self.a_label.update(a_content + sensors[configure.sensor1[0]][4],30,15,205,titleFont,red)

		c_content = str(int(c_newest))
		c_position = resolution[0] - (self.c_label.get_size(c_content + sensors[configure.sensor3[0]][4])+15)
		self.c_label.update(c_content + sensors[configure.sensor3[0]][4],30,c_position,205,titleFont,yellow)

		b_content = str(int(b_newest))
		self.b_label.update( b_content + sensors[configure.sensor2[0]][4],30,114,205,titleFont,green)
		self.b_label.center(resolution[0],31,0,205)

		intervaltime = float(self.drawinterval.timelapsed())
		lapse = format(intervaltime, '.2f')
		self.drawinterval.logtime()
		intervaltext = (lapse + ' sec')
		interx= (22)
		intery= (21)


		self.intervallabel.update(intervaltext,30,interx,intery,titleFont,white)
		self.intervallabelshadow.update(intervaltext, 30, interx + 2, intery + 2 ,titleFont,(100,100,100))


		if not configure.auto[0]:
			a_slide = translate(a_newest, sensors[0][1], sensors[0][2], 194, 7)

			b_slide = translate(b_newest, sensors[1][1], sensors[1][2], 194, 7)

			c_slide = translate(c_newest, sensors[2][1], sensors[2][2], 194, 7)

			self.slider1.update(sliderb, 283, a_slide)
			self.slider2.update(sliderb, 283, b_slide)
			self.slider3.update(sliderb, 283, c_slide)
		else:
			self.slider1.update(sliderb, 283, a_cords[-1][1]-10)
			self.slider2.update(sliderb, 283, b_cords[-1][1]-10)
			self.slider3.update(sliderb, 283, c_cords[-1][1]-10)


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

		status  = "mode_a"

		keys = self.input.read()
		#print(self.input.read())
		if keys[1]:
			if self.input.is_down(1):
				status =  "mode_b"

		if keys[2]:
			if self.input.is_down(2):
				print("set status to settings")
				configure.last_status[0] = "mode_a"
				status = "settings"

		return status

	def visible(self,item,option):
		self.visibility[item] = option




class Slider_Screen(object):
	def __init__(self, surface,input):
		# This function draws the main 3-slider interface, modelled after McCoy's tricorder in "Plato's Stepchildren". It displays temperature, humidity and pressure.
		self.surface = surface
		#checks time
		self.timenow = time.time()
		#compares time just taken with time of start to animate the apperance of text
		#print(timenow - tock.timed)
		# Sets a black screen ready for our UI elements
		self.surface.fill(black)

		# Instantiates the components of the scene
		self.a_label = Label()
		self.b_label = Label()
		self.c_label = Label()
		self.backPlane = Image()

		self.slider1 = Image()
		self.slider2 = Image()
		self.slider3 = Image()
		self.status = "mode_b"
		self.input = input

	def frame(self,sensors):

		# parses dictionary of data from sensor/weather based on the
		a_newest = float(sensors[0][0])
		b_newest = float(sensors[1][0])
		c_newest = float(sensors[2][0])


		# data labels
		self.a_label.update(str(int(a_newest)) + "\xb0",19,47,215,titleFont,yellow)
		self.b_label.update(str(int(b_newest)),19,152,215,titleFont,yellow)
		self.c_label.update(str(int(c_newest)),19,254,215,titleFont,yellow)

		# slider data adjustment
		# the routine takes the raw sensor data and converts it to screen coordinates to move the sliders
		a_slide = translate(float(sensors[0][0]), sensors[0][1], sensors[0][2], 204, 15)
		b_slide = translate(float(sensors[1][0]), sensors[1][1], sensors[1][2], 204, 15)
		c_slide = translate(float(sensors[2][0]), sensors[2][1], sensors[2][2], 204, 15)

		# Updates our UI objects with data parsed from sensor/weather
		self.backPlane.update(backplane, 0, 0)
		self.slider1.update(slidera, 70, a_slide)
		self.slider2.update(slidera, 172, b_slide)
		self.slider3.update(slidera, 276, c_slide)

		# draws the graphic UI to the buffer
		self.backPlane.draw(self.surface)
		self.slider1.draw(self.surface)
		self.slider2.draw(self.surface)
		self.slider3.draw(self.surface)

		# draws the labels to the buffer
		self.a_label.draw(self.surface)
		self.b_label.draw(self.surface)
		self.c_label.draw(self.surface)

		# draws UI to frame buffer
		#if (rot.read() == True): < can flip screen if necessary
		#surface.blit(pygame.transform.rotate(surface, 180), (0, 0))
		status  = "mode_b"

		keys = self.input.read()
		#print(self.input.read())
		if keys[0]:
			if self.input.is_down(0):
				status =  "mode_a"

		if keys[2]:
			if self.input.is_down(2):
				print("set status to settings")
				configure.last_status[0] = "mode_b"
				status = "settings"


		pygame.display.flip()
		#tock.timed = time.time()

			#returns state to main loop
		return status


# A basic screen object. Is given parameters and displays them on a number of preset panels
class Screen(object):

	def __init__(self, debounce):
		screenSize = resolution

		# I forget, probably colour depth?
		smodes = pygame.display.list_modes(def_modes)

		# instantiate a pygame display with the name "surface",

		if configure.pc:
			#for development use this one (windowed mode)
			self.surface = pygame.display.set_mode(screenSize)
		else:
			# on the picorder use this option.
			self.surface = pygame.display.set_mode(screenSize, pygame.FULLSCREEN)
			pygame.event.set_blocked(pygame.MOUSEMOTION)
			pygame.mouse.set_visible(False)

		self.timed = time.time()
		self.input = Inputs()
		self.graphscreen = Graph_Screen(self.surface,self.input)
		self.slidescreen = Slider_Screen(self.surface,self.input)
		self.settings_screen = Settings_Panel(self.surface,self.input)


	def startup_screen(self,start_time):

		status = startUp(self.surface,start_time)
		return status

	def slider_screen(self,sensors):
		status = self.slidescreen.frame(sensors)
		return status
		#return grapher(self.surface,sensors,self.data_a,self.data_b,self.data_c)

	def graph_screen(self,sensors):
		status = self.graphscreen.frame(sensors)
		return status


	def settings(self):
		status = self.settings_screen.frame()
		return status
