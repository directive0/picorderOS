![Logo](https://raw.githubusercontent.com/directive0/picorderOS/master/assets/picorderOS_logo.png?raw=true "PicorderOS Logo")

#
A set of python components that together provide functionality for a number of raspberry pi based tricorder replicas that I call "Picorders". A Picorder is made of a Raspberry Pi, a sensor package, battery, display and supplemental components to provide a satisfying and accurate Tricorder experience. The goal is to have a raspberry pi based device that provides the operator with a selection of sensor readings that may be useful and feels like a Tricorder from Star Trek.

## Notes:
At present PicorderOS supports a number of displays, sensors, and inputs. The user can mix and match their desired picorder load out using the configure object contained in objects.py.

## Requirements:
PicorderOS uses a number of modules to operate, specifically:
- Pygame
- Luma.lcd
- Adafruit Blinka
- MPR121 Capacitive Sensor
- Senshat
- RPi.GPIO
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
