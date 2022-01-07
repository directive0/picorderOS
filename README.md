![Logo](https://raw.githubusercontent.com/directive0/picorderOS/master/assets/picorderOS_logo.png?raw=true "PicorderOS Logo")

# PicorderOS is not actually an OS, but a set of python components that together provide functionality for a number of Raspberry Pi based tricorder replicas called "Picorders". A Picorder is made of a Raspberry Pi, one (or more) sensor package, battery, display and supplemental components to provide a satisfying and accurate Tricorder experience. The purpose of this project is to provide a simple, extensible method for quickly getting a raspberry pi to be a handheld sensor data collection and display device.

For more up to date information please visit my [Wiki](https://squaredwave.com/wiki/index.php?title=PicorderOS)

## Notes:
At present PicorderOS supports a number of displays, sensors, and inputs. The user can mix and match their desired picorder load out by editing the objects.py preferences file.

The software is driven by a main loop in main.py which starts and controls the screen. Various elements like input detection, LED sequencing, and audio playback run as separate threads, communicating via flags set in the objects.py module.

PicorderOS features PLARS (Picorder Library Access and Retrieval) to catalogue and organize each sensor reading into a pandas dataframe. PLARS then provides it to screen drawing modules as requested.

## Requirements:
Depending on hardware configuration PicorderOS use a number of exotic modules to operate:

Most installs will require:
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) (For various I/O functions)
- [os](https://pythonprogramming.net/python-3-os-module/) (For machine vitals)
- [psutil](https://psutil.readthedocs.io/en/latest/) (For simulating sensors when testing or demonstrating)
- [Adafruit Blinka](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi) (Adafruit graciously offers a number of great python sensor libraries through their circuitpython platform)

Depending on your choice of screen you may need:
- [Pygame](https://www.pygame.org/wiki/GettingStarted) (For framebuffer screens)
- [Luma.lcd](https://pypi.org/project/luma.lcd/) (For a range of LCD options)

Depending on your sensor loadout and operator interface solution you may require:
- [Sensehat](https://projects.raspberrypi.org/en/projects/getting-started-with-the-sense-hat/2)
- [Adafruit Circuitpython BME680](https://github.com/adafruit/Adafruit_CircuitPython_BME680)

I have
- [cap1xxx](https://github.com/pimoroni/cap1xxx) (For CAP1208 based capacitive touch buttons)
- [MPR121 Capacitive Sensor](https://github.com/adafruit/Adafruit_CircuitPython_MPR121) (For CAP1208 based capacitive touch buttons)


Be sure you have these modules installed before attempting to run picorderOS. A fresh Raspberry Pi OS image can usually be initialized with the following installation commands:

```
sudo apt-get update

sudo apt-get upgrade

sudo apt-get install libatlas-base-dev libsdl2-dev libopenjp2-7-dev libtiff5 python3-pandas python3-psutil

pip3 install --upgrade colour luma.lcd luma.emulator adafruit-circuitpython-bme680 sense-hat adafruit-circuitpython-mpr121


```
