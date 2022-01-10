 #!/usr/bin/python

# This display module uses Pygame to draw picorder routines to the screen.
# It is built upon the original Picorder UI and is intended to be used for TOS
# styled tricorders.
print("Loading 320x240 Duotronic Interface")
# The following are some necessary modules for the Picorder.
import pygame
import time


from plars import *
from objects import *
from input import *

if not configure.pc:
	if configure.tr108:
		import os
		# runs a CLI command to disable the raspberry pi's screen blanking
		#os.system('xset -display :0 -dpms')

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
refreshrate = 0

# controls the margins to adjust for adjusting text positioning.
marginright = 16
marginleft = 16

# The following lists are for my colour standards.
red = (255,0,0)
green = (106,255,69)
blue = (99,157,255)
yellow = (255,221,5)
orange = (255,192,2)
black = (0,0,0)
white = (255,255,255)

theme1 = [red,green,yellow]
theme2 = [blue,green,white]
theme3 = [blue, white, red]
themes = [theme1,theme2, theme3]
themenames = ["alpha", "beta", "delta"]

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
#pygame.display.set_icon(blueInsignia)



# The following function defines button behaviours and allows the program to
# query the button events and act accordingly. This function is deprecated.
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
		configure.auto[0] = not configure.auto[0]

	return message

# the following class defines simple text labels

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

	# Sets the paramaters of the text, used when ready to push the text.
	def update(self, content, fontSize, nx, ny, fontType, color):
		self.x = nx
		self.y = ny
		self.content = content
		self.fontSize = fontSize
		self.myfont = pygame.font.Font(fontType, self.fontSize)
		self.color = color

	def r_align(self,x,y):
		size = self.getrect()
		textposx = x-size[0]
		textposy = y
		self.update(self.content,self.fontSize,textposx,textposy,titleFont,self.color)

	# centers the text within an envelope
	def center(self,w,h,x,y):
		size = self.getrect()
		xmid = x + w/2
		ymid = y + h/2
		textposx = xmid - (size[0]/2)
		textposy = ymid - (size[1]/2) + self.scaler
		self.update(self.content,self.fontSize,textposx,textposy,titleFont,self.color)

	# returns the width and height of the desired text (useful for justifying)
	def getrect(self):
		label = self.myfont.render(self.content, 1, self.color)
		textw = label.get_width()
		texth = label.get_height()
		return textw,texth

	# returns only the width of the text.
	def get_size(self, content):
		width, height = self.myfont.size(content)
		return width

	# finally draws the text to screen
	def draw(self, surface):
		label = self.myfont.render(self.content, 1, self.color)
		surface.blit(label, (self.x, self.y))

# this class provides functionality for interactive text labels.
class SelectableLabel(Label):

	def __init__(self, oper, special = 0):

		# special determines the behaviour of the label for each type of
		# operator the class is supplied. There may be multiple types of int or
		# boolean based configuration parameters so this variable helps make
		# new options

		self.special = special

		# coordinates
		self.x = 0
		self.y = 0

		# basic graphical parameters
		self.color = white
		self.fontSize = 33
		self.myfont = pygame.font.Font(titleFont, self.fontSize)
		text = "Basic Item"
		self.size = self.myfont.size(text)
		self.scaler = 3
		self.selected = False
		self.indicator = Image()
		self.content = "default"

		# this variable is a reference to a list stored in "objects.py"
		# containing either a boolean or an integer. This allows the Selectable
		# Lable to actually change settings on the fly.
		self.oper = oper

	def update(self, content, fontSize, nx, ny, fontType, color):
		self.x = nx
		self.y = ny
		self.content = content
		self.fontSize = fontSize
		self.myfont = pygame.font.Font(fontType, self.fontSize)
		self.color = color
		self.indicator.update(sliderb, nx - 23, ny+1)

	# this function is called when the user decides to change a setting.
	def toggle(self):

		# if the parameter supplied is a boolean
		if isinstance(self.oper[0], bool):
			#toggle its state
			self.oper[0] = not self.oper[0]

		#if the parameter supplied is an integer
		elif isinstance(self.oper[0], int):

			# increment the integer.
			self.oper[0] += 1

			# if the integer is larger than the pool of available sensors.
			# this assumes this selectable label is being used to control
			# sensor selection.
			if self.special == 1 and self.oper[0] > configure.max_sensors[0]-1:
				self.oper[0] = 0

			if self.special == 2 and self.oper[0] > (len(themes) - 1):
				self.oper[0] = 0

		return self.oper[0]

	def draw(self, surface):
		if self.selected:
			self.indicator.draw(surface)

		label = self.myfont.render(self.content, 1, self.color)


		status_text = "dummy"
		if self.special == 0:
			status_text = str(self.oper[0])
		elif self.special == 1:
			status_text = configure.sensor_info[self.oper[0]][3]
		elif self.special == 2:
			status_text = themenames[self.oper[0]]

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

# a bit ambitious. A function to draw scales for the slider screen
def make_scale(high,low,grads,lrlow,lrhigh,lylow,lyhigh,grnlow,grnhigh,hylow,hyhigh,hrlow,hrhigh,labels):

	# create a surface to save our background.

	backSurface = pygame.display.set_mode(resolution)

	# draw the lines from top to bottom

	# draw the graduations


	# draw labels

	# r	eturn pygame screen

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
	secblurb = Label()

	logoposx = (resolution[0]/2) - (226/2)
	#sets out UI objects with the appropriate data
	insignia.update(pioslogo, logoposx, 60)
	#mainTitle.update("Picorder OS",25,22,181,titleFont,white)
	#mainTitle.center(resolution[0],20,0,181)
	secTitle.update(configure.version,19,37,210,titleFont,blue)
	secTitle.center(resolution[0],20,0,190)
	secblurb.update("Skurfsoft - Toronto",15,37,210,titleFont,blue)
	secblurb.center(resolution[0],20,0,210)

	#writes our objects to the buffer
	insignia.draw(surface)

	#checks time
	timenow = time.time()

	#compares time just taken with time of start to animate the apperance of text
	#if (timenow - timeSinceStart) > .5:
	 #mainTitle.draw(surface)

	#if (timenow - timeSinceStart) > 1:
	secTitle.draw(surface)
	secblurb.draw(surface)

	pygame.display.flip()
	elapsed = timenow - timeSinceStart
	print("elapsed: ", elapsed)
	#waits for 2 seconds to elapse before returning the state that will take us to the sensor readout
	if elapsed > 10:
	 return "mode_a"
	else:
	 return "startup"

# the following function displays version information about the program
def about(surface):

	#Sets a black screen ready for our UI elements
	surface.fill(black)

	#Instantiates the components of the scene
	insignia = Image()
	mainTitle = Label()
	version = Label()
	secTitle = Label()
	secblurb = Label()

	logoposx = (resolution[0]/2) - (226/2)

	insignia.update(pioslogo, logoposx, 30)
	version.update(configure.version,17,37,210,titleFont,blue)
	version.center(resolution[0],20,0,90)

	secTitle.update(configure.author,17,37,210,titleFont,blue)
	secTitle.center(resolution[0],20,0,110)

	mainTitle.update("Written in Python",17,37,210,titleFont,blue)
	mainTitle.center(resolution[0],20,0,125)
	secblurb.update("Developed By Chris Barrett",15,37,210,titleFont,blue)
	secblurb.center(resolution[0],20,0,210)

	#writes our objects to the buffer
	insignia.draw(surface)


	version.draw(surface)
	mainTitle.draw(surface)
	secTitle.draw(surface)
	secblurb.draw(surface)

	pygame.display.flip()


# graphit is a quick tool to help prepare graphs
def graphit(data,new, auto = True):

	#puts a new sensor value at the end
	data.updatelist(new[0])

	#grabs our databuffer object.
	buffer = data.grablist()

	prep = []

	data_high = max(buffer)
	data_low = min(buffer)

	for i in data.grablist():
		if configure.auto[0]:
			prep.append(translate(i, data_low, data_high, 204, 17))
		else:
			prep.append(translate(i, new[1], new[2], 204, 17))

	return data.graphprep(prep)



class Settings_Panel(object):

	def __init__(self,surface):

		self.left_margin = 37

		self.index = 0
		self.surface = surface
		self.labelstart = 47
		self.labeljump = 21

		self.titlelabel = Label()
		self.titlelabel.update("Control Panel",25,17,15,titleFont,orange)

		self.option1 = SelectableLabel(configure.sensor1, special = 1)
		self.option1.update("Graph 1: ",20,self.left_margin,47,titleFont,themes[configure.theme[0]][0])

		self.option2 = SelectableLabel(configure.sensor2, special = 1)
		self.option2.update("Graph 2: ", 20, self.left_margin, self.labelstart + self.labeljump, titleFont, themes[configure.theme[0]][1])

		self.option3 = SelectableLabel(configure.sensor3, special = 1)
		self.option3.update("Graph 3: ", 20, self.left_margin, self.labelstart + (self.labeljump*2), titleFont, themes[configure.theme[0]][2])

		self.option4 = SelectableLabel(configure.theme, special = 2)
		self.option4.update("Theme:  ", 20, self.left_margin, self.labelstart + (self.labeljump*3), titleFont, orange)

		self.option5 = SelectableLabel(configure.auto)
		self.option5.update("Auto Range: ", 20, self.left_margin, self.labelstart + (self.labeljump*4), titleFont, orange)

		self.option6 = SelectableLabel(configure.leds)
		self.option6.update("LEDs: ", 20, self.left_margin, self.labelstart + (self.labeljump*5), titleFont, orange)

		self.option7 = SelectableLabel(configure.moire)
		self.option7.update("Moire: ", 20, self.left_margin, self.labelstart + (self.labeljump*6), titleFont, orange)

		self.options = [self.option1,self.option2, self.option3, self.option4, self.option5, self.option6, self.option7]

	def colour_update(self):
		self.option1.update("Graph 1: ",20,self.left_margin,47,titleFont,themes[configure.theme[0]][0])
		self.option2.update("Graph 2: ", 20, self.left_margin, 68, titleFont, themes[configure.theme[0]][1])
		self.option3.update("Graph 3: ", 20, self.left_margin, 90, titleFont, themes[configure.theme[0]][2])
		self.option4.update("Theme:  ", 20, self.left_margin, 111, titleFont, orange)
		self.option5.update("Auto Range: ", 20, self.left_margin, 132, titleFont, orange)
		self.option6.update("LEDs: ", 20, self.left_margin, 154, titleFont, orange)
		self.option7.update("Moire: ", 20, self.left_margin, 176, titleFont, orange)


	def frame(self):

		self.surface.fill(black)

		self.titlelabel.draw(self.surface)

		for i in range(len(self.options)):
			if i == self.index:
				self.options[i].selected = True
			else:
				self.options[i].selected = False

			self.options[i].draw(self.surface)

		self.colour_update()
		# draws UI to frame buffer
		pygame.display.flip()

		result = "settings"

		# pulls input information
		keys = self.input.read()

		if keys[0]:
			self.index += 1

			if self.index > (len(self.options) - 1):
				self.index = 0

		if keys[1]:
			self.options[self.index].toggle()

		if keys[2]:
			result = configure.last_status[0]

		return result


# The graph screen object is a self contained screen that is fed the surface
# and the sensor at the current moment and draws a frame when called.
class Graph_Screen(object):

	# Draws three graphs in a grid and three corresponding labels.

	def __init__(self,surface):


		# for long presses
		self.input_timer = timer()
		self.presstime = 5
		self.longpressed = [False, False, False]

		# State variable
		self.status = "mode_a"
		self.selection = 0

		# An fps controller
		self.drawinterval = timer()

		# Sample rate controller
		self.senseinterval = 0

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

		self.focus_label = Label()

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

		self.margin = 16


	def frame(self):
		# Because the graph screen is slow to update it needs to pop a reading onto screen as soon as it is initiated I draw a value once and wait for the interval to lapse for the next draw. Once the interval has lapsed pop another value on screen.
		#Sets a black screen ready for our UI elements

		#print(configure.sensor_info)

		# grabs sensor info from settings for quick reference and display
		sense_info_a = configure.sensor_info[configure.sensors[0][0]]
		sense_info_b = configure.sensor_info[configure.sensors[1][0]]
		sense_info_c = configure.sensor_info[configure.sensors[2][0]]

		self.surface.fill(black)

		#draws Background gridplane
		self.graphback.draw(self.surface)

		# resolves the key items (dsc and dev) for the targeted sensor, for plars to use.
		# creates a "senseslice"; an up to date data fragment for each configured sensor

		senseslice = [0,0,0]

		for i in range(3):
			# determines the sensor keys for each of the three main sensors
			dsc = configure.sensor_info[configure.sensors[i][0]][3]
			dev = configure.sensor_info[configure.sensors[i][0]][5]
			print("dsc, dev: ",dsc,dev)

			item = plars.get_recent(dsc,dev,num = 1)
			print("item: ", item)

			if len(senseslice) > 0:
				senseslice[i] = item


		#converts data to float

		print(senseslice)
		a_newest = float(senseslice[0][0])
		b_newest = float(senseslice[1][0])
		c_newest = float(senseslice[2][0])
		newests = [a_newest,b_newest,c_newest]

		# updates the data storage object and retrieves a fresh graph ready to store the positions of each segment for the line drawing
		a_cords = graphit(self.data_a,senseslice[0])
		b_cords = graphit(self.data_b,senseslice[1])
		c_cords = graphit(self.data_c,senseslice[2])
		cords = [a_cords,b_cords,c_cords]

		a_content = str(int(a_newest))
		a_color = themes[configure.theme[0]][0]

		self.a_label.update(a_content + sense_info_a[4],30,marginleft,205,titleFont,a_color)

		b_content = str(int(b_newest))
		b_color = themes[configure.theme[0]][1]
		self.b_label.update( b_content + sense_info_b[4],30,114,205,titleFont,b_color)
		self.b_label.center(resolution[0],31,0,205)

		c_content = str(int(c_newest))
		c_color = themes[configure.theme[0]][2]

		self.c_label.update(c_content + sense_info_c[4],30,marginright,205,titleFont,c_color)
		self.c_label.r_align(320 - marginright ,205)
		contents = [a_content,b_content,c_content]

		labels = [self.a_label,self.b_label,self.c_label]



		interx= (22)
		intery= (21)




		if not configure.auto[0]:

			a_slide = translate(a_newest, sense_info_a[1], sense_info_a[2], 194, 7)

			b_slide = translate(b_newest, sense_info_b[1], sense_info_b[2], 194, 7)

			c_slide = translate(c_newest, sense_info_c[1], sense_info_c[2], 194, 7)

			self.slider1.update(sliderb, 283, a_slide)
			self.slider2.update(sliderb, 283, b_slide)
			self.slider3.update(sliderb, 283, c_slide)
		else:
			self.slider1.update(sliderb, 283, a_cords[-1][1]-10)
			self.slider2.update(sliderb, 283, b_cords[-1][1]-10)
			self.slider3.update(sliderb, 283, c_cords[-1][1]-10)

		sliders = [self.slider1,self.slider2,self.slider3]

		if self.selection == 0:
			#draw the lines
			pygame.draw.lines(self.surface, a_color, False, a_cords, 2)
			self.slider1.draw(self.surface)

			pygame.draw.lines(self.surface, b_color, False, b_cords, 2)
			self.slider2.draw(self.surface)

			pygame.draw.lines(self.surface, c_color, False, c_cords, 2)
			self.slider3.draw(self.surface)

			# draws the labels
			self.a_label.draw(self.surface)
			self.b_label.draw(self.surface)
			self.c_label.draw(self.surface)

		# this checks if we are viewing a sensor individually and graphing it alone.
		if self.selection != 0:
			# we make a variable carrying the index of the currently selected item.
			this = self.selection - 1

			# we collect its default colour based off our theme
			this_color = themes[configure.theme[0]][this]

			focus_cords = cords[this]
			focus_slider = sliders[this]
			pygame.draw.lines(self.surface, this_color, False, focus_cords, 2)
			focus_slider.draw(self.surface)

			self.focus_label.update(configure.sensor_info[configure.sensors[this][0]][3],30,283,205,titleFont,this_color)
			self.focus_label.r_align(320 - marginright ,205)
			self.focus_label.draw(self.surface)

			self.a_label.update(contents[this] + sensors[configure.sensors[this][0]][4],30,15,205,titleFont,this_color)
			self.a_label.draw(self.surface)

		# draws the interval label (indicates refresh rate)
		#self.intervallabelshadow.draw(self.surface)
		#self.intervallabel.draw(self.surface)

		#draws UI to frame buffer


		pygame.display.update()

		status  = "mode_a"


		# The following code handles inputs and button presses.
		keys = [0,0,0]
		# if a key is registering as pressed.
		if keys[0]:
			self.selection += 1
			if self.selection > 3:
				self.selection = 0

		if keys[1]:
			status =  "mode_b"

		if keys[2]:
			configure.last_status[0] = "mode_a"
			status = "settings"

		return status

	def visible(self,item,option):
		self.visibility[item] = option



class Slider_Screen(object):
	def __init__(self, surface):
		# This function draws the main 3-slider interface, modelled after McCoy's tricorder in "Plato's Stepchildren". It displays temperature, humidity and pressure.
		self.surface = surface

		#checks time
		self.timenow = time.time()

		#compares time just taken with time of start to animate the apperance of text

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



	def frame(self):

		#converts data to float
		a_newest = float(sensors[configure.sensor1[0]][0])
		b_newest = float(sensors[configure.sensor2[0]][0])
		c_newest = float(sensors[configure.sensor3[0]][0])



		# data labels
		a_content = str(int(a_newest))
		self.a_label.update(a_content + sensors[configure.sensor1[0]][4],19,47,215,titleFont,yellow)
		b_content = str(int(b_newest))
		self.b_label.update(b_content + sensors[configure.sensor2[0]][4],19,152,215,titleFont,yellow)
		c_content = str(int(c_newest))
		self.c_label.update(c_content + sensors[configure.sensor3[0]][4],19,254,215,titleFont,yellow)

		# slider data adjustment
		# the routine takes the raw sensor data and converts it to screen coordinates to move the sliders
		a_slide = translate(float(sensors[configure.sensor1[0]][0]), sensors[configure.sensor1[0]][1], sensors[configure.sensor1[0]][2], 204, 15)
		b_slide = translate(float(sensors[configure.sensor2[0]][0]), sensors[configure.sensor2[0]][1], sensors[configure.sensor2[0]][2], 204, 15)
		c_slide = translate(float(sensors[configure.sensor3[0]][0]), sensors[configure.sensor3[0]][1], sensors[configure.sensor3[0]][2], 204, 15)

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

		if keys[0]:
			status =  "mode_a"

		if keys[2]:
			configure.last_status[0] = "mode_b"
			status = "settings"


		pygame.display.flip()
		#tock.timed = time.time()

			#returns state to main loop
		return status


# A basic screen object. Is given parameters and displays them on a number of preset panels
class Screen(object):

	def __init__(self):
		screenSize = resolution

		# The following commands initiate a pygame environment.
		pygame.init()
		pygame.font.init()
		pygame.display.set_caption('PicorderOS')

		# I forget, probably colour depth?
		smodes = pygame.display.list_modes(def_modes)

		# instantiate a pygame display with the name "surface",

		if configure.pc:
			#for development use this one (windowed mode)
			self.surface = pygame.display.set_mode(screenSize)
		else:
			# on the picorder use this option (Fullscreen).
			flags = pygame.FULLSCREEN | pygame.SCALED
			self.surface = pygame.display.set_mode(screenSize, flags, display=0)
			pygame.event.set_blocked(pygame.MOUSEMOTION)
			pygame.mouse.set_visible(False)


		self.timed = time.time()
		self.graphscreen = Graph_Screen(self.surface)
		self.slidescreen = Slider_Screen(self.surface)
		self.settings_screen = Settings_Panel(self.surface)


	def startup_screen(self,start_time):
		status = startUp(self.surface,start_time)
		return status

	def about_screen(self):
		status = about()
		return status

	def slider_screen(self,sensors):
		status = self.slidescreen.frame(sensors)
		return status

	def graph_screen(self):
		status = self.graphscreen.frame()
		return status

	def settings(self):
		status = self.settings_screen.frame()
		return status
