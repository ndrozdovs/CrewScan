#!/usr/bin/python
import time
import RPi.GPIO as GPIO

# Use board based pin numbering
GPIO.setmode(GPIO.BCM)

def ReadDistance(pin):
    try:
        counter = 0
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

        time.sleep(0.000002)

        #send trigger signal
        GPIO.output(pin, 1)

        time.sleep(0.000005)

        GPIO.output(pin, 0)

        GPIO.setup(pin, GPIO.IN)

        while GPIO.input(pin)==0:
            starttime=time.time()
            counter = counter + 1
            if counter == 5000:
                return 0

        while GPIO.input(pin)==1:
            endtime=time.time()

        duration=endtime-starttime
        distance=duration*34000/2  # Distance is defined as time/2 (there and back) * speed of sound 34000 cm/s 
        return distance
    except:
        return 0

while True:
   distance = ReadDistance(17)
   if distance < 10:
       print(distance)
   time.sleep(.01)

