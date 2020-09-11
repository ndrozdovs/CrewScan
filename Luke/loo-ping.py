#!/usr/bin/python
import time
import RPi.GPIO as GPIO

# Use board based pin numbering
GPIO.setmode(GPIO.BCM)

def ReadDistance(pin):
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, 0)
   counter = 0

   time.sleep(0.0002)

   #send trigger signal
   GPIO.output(pin, 1)

   time.sleep(0.0005)

   GPIO.output(pin, 0)

   GPIO.setup(pin, GPIO.IN)

   while GPIO.input(pin)==0:
      starttime=time.time()
      counter = counter + 1
      if counter == 5000:
         print(counter)
         return 0

   while GPIO.input(pin)==1:
      endtime=time.time()
      
   duration=endtime-starttime
   # Distance is defined as time/2 (there and back) * speed of sound 34000 cm/s 
   distance=duration*34000/2
   return distance

while True:
   distance = ReadDistance(17)
   if distance < 10:
       print(distance)
   time.sleep(.01)

