# the following function plots the environment sensors to an onscreen graph. It represent one frame.

class Graph_Screen(object):

	def __init__(self,surface):
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

	def frame(self,sensors):
		# Because the graph screen is slow to update it needs to pop a reading onto screen as soon as it is initiated I draw a value once and wait for the interval to lapse for the next draw. Once the interval has lapsed pop another value on screen.
		#Sets a black screen ready for our UI elements
		self.surface.fill(black)

		#draws Background gridplane
		self.graphback.draw(surface)

		#converts data to float
		a_newest = float(sensors[0][0])

		# updates the data storage object and retrieves a fresh graph ready to
		a_cords = graphit(data_a,sensors[0], auto = False)

		#repeat for each sensor
		b_newest = float(sensors[1][0])
		b_cords = graphit(data_b,sensors[1], auto = False)

		c_newest = float(sensors[2][0])
		c_cords = graphit(data_c,sensors[2], auto = False)

		a_content = str(int(b_newest))
		a_label.update(a_content + "\xb0" + " c",30,35,205,titleFont,red)
		c_content = str(int(c_newest))
		c_label.update(c_content + " hpa",30,114,205,titleFont,yellow)
		b_content = str(int(a_newest))
		b_label.update(b_content + " %",30,246,205,titleFont,green)
		#a_label.update(b_data + "\xb0",16,15,212,titleFont,yellow)

		setting = str(float(drawinterval))
		intervaltext = (setting + ' sec')
		interx= (22)
		intery= (21)


		intervallabel.update(intervaltext,30,interx,intery,titleFont,white)
		intervallabelshadow.update(intervaltext, 30, interx + 2, intery + 2 ,titleFont,(100,100,100))


		a_info = sensors[0][1]
		a_slide = translate(a_newest, a_info[0], a_info[1], 194, 7)

		b_info = sensors[1][1]
		b_slide = translate(b_newest, b_info[0], b_info[1], 194, 7)

		c_info = sensors[2][1]
		c_slide = translate(c_newest, c_info[0], c_info[1], 194, 7)

		self.slider1.update(sliderb, 283, a_slide)
		self.slider2.update(sliderb, 283, b_slide)
		self.slider3.update(sliderb, 283, c_slide)


		#draw the lines
		pygame.draw.lines(self.surface, green, False, a_cords, 2)

		pygame.draw.lines(self.surface, red, False, b_cords, 2)

		pygame.draw.lines(self.surface, yellow, False, c_cords, 2)

		self.a_label.draw(surface)
		self.c_label.draw(surface)
		self.b_label.draw(surface)
		self.intervallabelshadow.draw(surface)
		self.intervallabel.draw(surface)

		#draws UI to frame buffer


		self.slider1.draw(surface)
		self.slider2.draw(surface)
		self.slider3.draw(surface)



		pygame.display.flip()

		#returns state to main loop
		return status
