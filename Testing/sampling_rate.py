import board
import busio
import time
i2c = busio.I2C(board.SCL, board.SDA)
# Import module for ADS1115 
import adafruit_ads1x15.ads1115 as ADS

from adafruit_ads1x15.analog_in import AnalogIn
# Create ADC object
ads = ADS.ADS1115(i2c)
# Create analog input channel 
chan = AnalogIn(ads, ADS.P0)

counter = 0
current_voltage = chan.voltage
start_time = time.time()

while (time.time() - start_time) < 1:
    # Rough calc for temperature & print values
    if current_voltage != chan.voltage:
        current_voltage = chan.voltage
        counter = counter + 1
    
print(counter)
