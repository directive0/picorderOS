![Logo](https://raw.githubusercontent.com/directive0/picorder/master/assets/Picorder%20Logo.png?raw=true "Logo")

# The TR-108 Picorder 
This repo is a set of python components that together provide functionality for the TR-108 Tricorder I am building, as well as necessary files for anyone to build their own should they so desire. The TR-108 is a Raspberry Pi Zero based system that includes a sensor package, battery, display and supplemental components to provide a satisfying and accurate Tricorder experience. In the interest of inspiring others to build on what I have done I am providing all of the documentation I can.

## Notes:
Basic functionality is complete; the program logs values from the sense hat and displays them. I have become to optimize this code. 

I am hoping to add:
- Graph auto ranging
- Standardize sensor value retrieval
- Organize and modularize code for easier feature additions.

## Requirements:
Picorder.py uses a number of modules to operate, specifically:
- Pygame
- Senshat
- RPi.GPIO
- sys
- time
- math
- os
- psutil (PC Demo only)

Be sure you have these modules installed before attempting to run this program.

## Construction:
You can find all the necessary construction documents in the "construction" folder.

Adafruit parts Wishlist is here:
http://www.adafruit.com/wishlists/435166

The base I used for the tricorder:
https://www.amazon.ca/gp/product/B001820194/ref=ox_sc_sfl_title_6?ie=UTF8&psc=1&smid=A3DWYIK6Y9EEQB

## Sources
This project was made possible by information and inspiration provided by these sources:
- https://hackaday.io/project/5437-star-trek-tos-picorder
- https://github.com/tobykurien/rpi_lcars
