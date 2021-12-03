![Logo](https://raw.githubusercontent.com/directive0/picorderOS/master/assets/picorderOS_logo.png?raw=true "PicorderOS Logo")

#
A set of python components that together provide functionality for a number of Raspberry Pi based tricorder replicas called "Picorders". A Picorder is made of a Raspberry Pi, a sensor package, battery, display and supplemental components to provide a satisfying and accurate Tricorder experience. The goal is to have a raspberry pi based device that provides the operator with a selection of sensor readings that may be useful and feels like a Tricorder from Star Trek.  

For more up to date information please visit my [Wiki](https://squaredwave.com/wiki/index.php?title=PicorderOS)

## Notes:
At present PicorderOS supports a number of displays, sensors, and inputs. The user can mix and match their desired picorder load out using the configure object contained in objects.py.

Since picorderOS uses Luma.LCD it can address screens that use ST7735 drivers for colour display, and PCD8544 drivers for low power monochromatic applications.

Using pygame it is also possible to use standard monitors or any display that connects to the Pi via HDMI or Composite.

## Requirements:
Depending on hardware configuration PicorderOS relies on a number of exotic modules to operate:
- [Pygame](https://www.pygame.org/wiki/GettingStarted)
- [Luma.lcd](https://pypi.org/project/luma.lcd/)
- [Adafruit Blinka](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi)
- [MPR121 Capacitive Sensor](https://github.com/adafruit/Adafruit_CircuitPython_MPR121)
- [Sensehat](https://projects.raspberrypi.org/en/projects/getting-started-with-the-sense-hat/2)
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/)
- [os](https://pythonprogramming.net/python-3-os-module/)
- [psutil](https://psutil.readthedocs.io/en/latest/) (For simulating sensors when testing or demonstrating)

Be sure you have these modules installed before attempting to run picorderOS.

A requirements file have been included

```
python3 -m pip -r requirements.txt
```
-m defines next is a python module 
-r defines next is a requirements file
