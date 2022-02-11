<p align="center">
![Logo](https://raw.githubusercontent.com/directive0/picorderOS/master/assets/Picorder_Logo.png?raw=true "PicorderOS Logo")
</p>

# PicorderOS

a set of python components that provide functionality for a Raspberry Pi based [Tricorder](https://en.wikipedia.org/wiki/Tricorder) replica called a "picorder". A picorder is made of a Raspberry Pi, one or more sensor packages, a battery, a display, and supplemental components. The purpose of this project is to provide a simple, extensible method for quickly getting a Raspberry Pi to be a handheld sensor data collection and display device like the fictional device it is inspired by.

For further information please visit my [Wiki](https://squaredwave.com/wiki/index.php?title=PicorderOS)

## Usage:
At present picorderOS supports a number of displays, sensors, and inputs. The user can mix and match their desired picorder load out by editing the objects.py preferences file.

The software is started with ```python3 main.py``` from the project folder, which starts the main loop. The main loop handles display directly, various ancillary elements like input detection, LED sequencing, and audio playback run as separate threads and communicate via flags set in the ```objects.py``` module.

PicorderOS will generate an INI file on creation called ```picorder.ini```. By editing this file certain flags can be set for specific Picorder builds. Any sensors or peripherals not physically present must be turned off before picorderOS will run properly.

PicorderOS uses a module called PLARS (Picorder Library Access and Retrieval) to catalogue and organize each sensor reading into a pandas dataframe. PLARS then provides it to screen drawing modules as requested.

## Requirements:
Depending on hardware configuration picorderOS uses a number of exotic modules to operate:

Most installs will require:
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) (For various I/O functions)
- [os](https://pythonprogramming.net/python-3-os-module/) (For machine vitals)
- [psutil](https://psutil.readthedocs.io/en/latest/) (For simulating sensors when testing or demonstrating)
- [Adafruit Blinka](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi) (Adafruit graciously offers a number of great python sensor libraries through their circuitpython platform)

Depending on your sensor loadout and operator interface solution you may require:
- [Sensehat](https://projects.raspberrypi.org/en/projects/getting-started-with-the-sense-hat/2)
- [Adafruit Circuitpython BME680](https://github.com/adafruit/Adafruit_CircuitPython_BME680)

There are other sensor modules for capacitive buttons that can be used such as
- [cap1xxx](https://github.com/pimoroni/cap1xxx) (For CAP1208 based capacitive touch buttons)
- [MPR121 Capacitive Sensor](https://github.com/adafruit/Adafruit_CircuitPython_MPR121) (For CAP1208 based capacitive touch buttons)

Depending on your choice of screen you may need:
- [Pygame](https://www.pygame.org/wiki/GettingStarted) (For framebuffer screens)
- [Luma.lcd](https://pypi.org/project/luma.lcd/) (For a range of LCD options)

## Installation:

A requirements file is included, it can be used to install all the necessary python modules through pip.

```
python3 -m pip -r requirements.txt
```

A fresh Raspberry Pi OS image can usually be initialized to work with picorderOS with the following installation commands:

```
sudo apt-get update

sudo apt-get upgrade

sudo apt-get install libatlas-base-dev libsdl2-dev libopenjp2-7-dev libtiff5 python3-pandas python3-psutil

pip3 install --upgrade colour luma.lcd luma.emulator adafruit-circuitpython-bme680 sense-hat adafruit-circuitpython-mpr121 pygame==2.0.0

```

Some experimentation may be necessary. PicorderOS is provided as free software and comes with no guarantee or warranty. This software is not to be used outside federation space, and is not suitable for use in environments that do not obey established laws of physics. Using this software could cause timeline damage, rocks exploding out of consoles, or blue barrels. Do not use PicorderOS if you have recently tested positive for Andorian Flu.
