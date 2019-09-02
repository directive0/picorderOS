![Logo](https://raw.githubusercontent.com/directive0/picorderOS/master/assets/picorderOS_logo.png?raw=true "PicorderOS Logo")

#
A set of python components that together provide functionality for a number of raspberry pi based tricorder replicas that I call "Picorders". A Picorder is made of a Raspberry Pi, a sensor package, battery, display and supplemental components to provide a satisfying and accurate Tricorder experience. The goal is to have a raspberry pi based device that provides the operator with a selection of sensor readings that may be useful and feels like a Tricorder from Star Trek.  

## Notes:
At present PicorderOS supports a number of displays, sensors, and inputs. The user can mix and match their desired picorder load out using the configure object contained in objects.py.

Since picorderOS uses Luma.LCD it can address screens that use ST7735 drivers for colour display, and PCD8544 drivers for low power monochromatic applications.

Using pygame it is also possible to use standard monitors or any display that connects to the Pi via HDMI or Composite.

## Requirements:
PicorderOS uses a number of modules to operate, specifically:
- [Pygame](https://www.pygame.org/wiki/GettingStarted)
- [Luma.lcd](https://pypi.org/project/luma.lcd/)
- [Adafruit Blinka](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi)
- [MPR121 Capacitive Sensor](https://github.com/adafruit/Adafruit_CircuitPython_MPR121)
- [Sensehat](https://projects.raspberrypi.org/en/projects/getting-started-with-the-sense-hat/2)
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/)
- sys
- time
- math
- os
- psutil (PC Demo only)

Be sure you have these modules installed before attempting to run this program.

## Sources
This project was made possible by information and inspiration provided by these sources:
- https://hackaday.io/project/5437-star-trek-tos-picorder
- https://github.com/tobykurien/rpi_lcars
