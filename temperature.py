import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import RPi.GPIO as GPIO
from adafruit_ads1x15.analog_in import AnalogIn


def ReadDistance(pin):
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, 0)
	counter = 0

	time.sleep(0.0002)
 
	GPIO.output(pin, 1)  # Send trigger signal

	time.sleep(0.0005)

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
   

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0)

counter = 100
temperature = 0
samples = 0

while counter > 0:
	try:
		distance = ReadDistance(17)
	except:
		distance = 0
	if distance < 8 and distance > 2.25:
		if counter < 90:
			compensation = 1.72255 - (-0.0028336242611106542*distance + 1.739147043467168)
			voltage = chan.voltage + 0.064 + compensation
			temp = 2705.06 + ((-7670.457 - 2705.061) / (1 + (voltage / (3.135016*(10**-8)))**0.0595245))
			temperature += temp
			time.sleep(.033)
			samples += 1
		counter -= 1

print("Temperature is: ", round((temperature / samples), 1))
