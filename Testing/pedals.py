import time
import RPi.GPIO as GPIO

# Use board based pin numbering
GPIO.setmode(GPIO.BCM)
pedal1 = 16
pedal2 = 20
pedal3 = 21
GPIO.setup(pedal1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(pedal2,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(pedal3,GPIO.IN,pull_up_down=GPIO.PUD_UP)

while True:
    pedal1_state = GPIO.input(pedal1)
    pedal2_state = GPIO.input(pedal2)
    pedal3_state = GPIO.input(pedal3)
    print(pedal1_state)
    print(pedal2_state)
    print(pedal3_state)
    time.sleep(1)
