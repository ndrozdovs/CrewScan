import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time
import RPi.GPIO as GPIO


def ReadDistance(pin):
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

    while GPIO.input(pin)==1:
        endtime=time.time()

    duration=endtime-starttime
    # Distance is defined as time/2 (there and back) * speed of sound 34000 cm/s 
    distance=duration*34000/2
    return distance


i2c = busio.I2C(board.SCL, board.SDA)
# Create ADC object
ads = ADS.ADS1115(i2c)
# Create analog input channel
chan = AnalogIn(ads, ADS.P0)

GPIO.setmode(GPIO.BCM)

f = open('results.txt', 'a')
print('----------------------------TEST START----------------------------', file=f)
counter = 600

while counter > 0:
	f = open('results.txt', 'a')
	temp = 2705.06 + ((-7670.457 - 2705.061) / (1 + (chan.voltage / (3.135016*(10**-8)))**0.0595245))
	distance = ReadDistance(17)
	print ('Distance to object:{} cm   |   temperature:{} degrees'.format(round(distance,1), round(temp,1)), file=f)
	counter = counter - 1
	time.sleep(1)
	
print('----------------------------TEST END----------------------------', file=f)
