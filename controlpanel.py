# External module imports
import RPi.GPIO as GPIO
import time

# Pin Definitons:
led1 = 16 # Broadcom pin 18 (P1 pin 12)
led2 = 20 # Broadcom pin 23 (P1 pin 16)
led3 = 21 # Broadcom pin 17 (P1 pin 11)

buta = 13
butb = 19
butc = 26

dc = 95 # duty cycle (0-100) for PWM pin

# Pin Setup:
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(led1, GPIO.OUT) # LED pin set as output
GPIO.setup(led2, GPIO.OUT) # LED pin set as output
GPIO.setup(led3, GPIO.OUT) # LED pin set as output
GPIO.setup(buta, GPIO.IN) # PWM pin set as output
GPIO.setup(butb, GPIO.IN) # PWM pin set as output
GPIO.setup(butc, GPIO.IN) # PWM pin set as output

# Initial state for LEDs:
GPIO.output(led1, GPIO.LOW)
GPIO.output(led2, GPIO.LOW)
GPIO.output(led3, GPIO.LOW)


def leda_on():
    GPIO.output(led1, GPIO.HIGH)
    
def ledb_on():
    GPIO.output(led2, GPIO.HIGH)
    
def ledc_on():
    GPIO.output(led3, GPIO.HIGH)

def leda_off():
    GPIO.output(led1, GPIO.LOW)
    
def ledb_off():
    GPIO.output(led2, GPIO.LOW)

def ledc_off():
    GPIO.output(led3, GPIO.LOW)

flip = 0
   
try:
    while 1:
        if flip == 0:
            leda_on()
            ledb_off()
            ledc_off()
        if flip == 1:
            leda_off()
            ledb_on()
            ledc_off()    
        if flip == 2:
            leda_off()
            ledb_off()
            ledc_on()
        flip = flip + 1
        
        if flip > 2:
            flip = 0
        time.sleep(1)
                
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    GPIO.cleanup() # cleanup all GPIO