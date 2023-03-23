<p align="center">
  <img width="203" height="273" src="https://raw.githubusercontent.com/directive0/picorderOS/master/assets/Picorder_Logo.png?raw=true">
</p>

# PicorderOS

A set of python components that provide functionality for a Raspberry Pi based [Tricorder](https://en.wikipedia.org/wiki/Tricorder) replica called a "picorder". A picorder is made of a Raspberry Pi, one or more sensor packages, a battery, a display, and supplemental components. The purpose of this project is to provide a simple, extensible method for quickly getting a Raspberry Pi to be a handheld sensor data collection and display device like the fictional device it is inspired by.

PicorderOS is experimental and in development. A lot of user configuration is required and you will probably need to "roll your own" solutions to some problems. PicorderOS is offered as a framework solution that can be built upon if desired or used as is.

For further information on hardware please visit the [Wiki](https://squaredwave.com/wiki/index.php?title=PicorderOS)

## Requirements:
Depending on hardware configuration picorderOS can use a number of existing third party libraries to communicate with i2c sensors. At present only a few sensors are currently officially supported like

- The [Sensehat](https://projects.raspberrypi.org/en/projects/getting-started-with-the-sense-hat/2) using the [sensehat library](https://pythonhosted.org/sense-hat/)
- The Bosch [BME680](https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors/bme680/) with an [Adafruit library](https://github.com/adafruit/Adafruit_CircuitPython_BME680)
- The Panasonic [AMG8833](https://www.digikey.ca/en/products/detail/panasonic-electronic-components/AMG8833/5825302) with an [Adafruit library](https://github.com/adafruit/Adafruit_CircuitPython_AMG88xx)

There is mostly stable support for the PocketGeiger and envirophat but detailed instructions are not available for those yet.

 For testing purposes picorderOS does not need to be run with real sensors, or even on a Raspberry Pi when put in "PC Mode".

Most installs will require:
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) (For various I/O functions)
- [os](https://pythonprogramming.net/python-3-os-module/) (For machine vitals)
- [psutil](https://psutil.readthedocs.io/en/latest/) (For simulating sensors when testing or demonstrating)
- [Adafruit Blinka](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi) (Adafruit graciously offers a number of great python sensor libraries through their circuitpython platform)


For capacitive touch sensing the [Pimoroni cap1xxx library](https://github.com/pimoroni/cap1xxx) can be used for CAP1208 based capacitive touch buttons, and an [adafruit MPR121 Capacitive Sensor](https://github.com/adafruit/Adafruit_CircuitPython_MPR121) for MPR121 ones.

PicorderOS can run using an HDMI or Composite screen in some cases, and can also use TFT LCD displays. Depending on your choice of screen you may need:
- [Pygame](https://www.pygame.org/wiki/GettingStarted) (For framebuffer screens)
- [Luma.lcd](https://pypi.org/project/luma.lcd/) (For a range of LCD options, thought not all are supported)


## Installation:

A requirements file is included, it can be used to install all the necessary python modules through pip.

```
python3 -m pip install -r requirements.txt
```

A fresh Raspberry Pi OS image can usually be initialized to work with picorderOS with the following installation commands:

```
sudo apt-get update

sudo apt-get upgrade

sudo apt install libsdl2-2.0-0 libsdl2-gfx-1.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-net-2.0-0 libsdl2-ttf-2.0-0

sudo apt-get install libatlas-base-dev libsdl2-dev libopenjp2-7-dev libtiff5 python3-pandas python3-psutil

pip3 install --upgrade colour luma.lcd luma.emulator pygame==2.0.0
```
Depending on your sensors, you will need to install a package that supports it:
```
pip3 install adafruit-circuitpython-bme680 sense-hat adafruit-circuitpython-mpr121

```

## Usage:
At present picorderOS supports a number of displays, sensors, and inputs. The user can mix and match their desired picorder load out. PicorderOS will generate an INI file on creation called ```config.ini```. By editing this file certain flags can be set for specific Picorder builds. Any sensors or peripherals not physically present must be turned off before picorderOS will run properly.

The software is started with ```python3 main.py``` from the project folder (run with sudo for full wifi features on 109 style builds), which starts the main loop. The main loop handles display directly, various ancillary elements like input detection, LED sequencing, and audio playback run as separate threads and communicate via flags set in the ```objects.py``` module.






Some experimentation may be necessary. PicorderOS is provided as free software and comes with no guarantee or warranty. This software is not to be used outside federation space, and is not suitable for use in environments that do not obey established laws of physics. Using this software could cause timeline damage, rocks exploding out of consoles, or blue barrels. Do not use PicorderOS if you have recently tested positive for Andorian Flu.
