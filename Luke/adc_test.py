# ADS1115 ADC & ZTP-115 IR Sensor test script
# Luke Bidulka

# Import modules & initialize I2C bus
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
# Import module for ADS1115 
import adafruit_ads1x15.ads1115 as ADS

from adafruit_ads1x15.analog_in import AnalogIn
# Create ADC object
ads = ADS.ADS1115(i2c)
# Create analog input channel 
chan = AnalogIn(ads, ADS.P0)

while True:
    # Rough calc for temperature & print values
    temp = 2705.06 + ((-7670.457 - 2705.061) / (1 + (chan.voltage / (3.135016*(10**-8)))**0.0595245))
    print(chan.value, round(chan.voltage, 5), round(temp,3))
    