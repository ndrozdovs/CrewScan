from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
import keyboard
from kivy.core.window import Window
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time
import RPi.GPIO as GPIO
from kivy.properties import StringProperty, ObjectProperty
from kivy.event import EventDispatcher
from functools import partial
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button 
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget 


TEMPERATURE = 0
DISTANCE = 0
DIST_COUNTER = 0
TEMP_COUNTER = 0
PROGRESS_BAR = "["
COUNTER = 0


# Window to start the screening
class BeginWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'info', 'begin'), 1/20)
        self.event1 = Clock.schedule_interval(self.bullshit, 1/10)
        
    def on_pre_leave(self):
        self.event.cancel()
        
    def bullshit(self, dt):
        global COUNTER
        self.ids.progress.value = COUNTER
        COUNTER = COUNTER + 1
 
# Window to show how to answer to prompts
class InfoWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'cough', 'begin'), 1/20)
        
    def on_pre_leave(self):
        self.event.cancel()

# Window to check for new cough or fever symptoms
class CoughWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'begin', 'travel'), 1/20)
        
    def on_pre_leave(self):
        self.event.cancel()

# Window to check if person traveled outside of Canada
class TravelWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'begin', 'fever'), 1/20)
        
    def on_pre_leave(self):
        self.event.cancel()

# Window to check if person has a fever    
class FeverWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'begin', 'contact'), 1/20)
        
    def on_pre_leave(self):
        self.event.cancel()
 
# Window to check if person had to contact with an individual with Covid or Covid like symptoms
class ContactWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'equipment', 'distance'), 1/20)
        
    def on_pre_leave(self):
        self.event.cancel()

# Window to check if person was wearing protective equipment if they were exsposed to an individual with Covid
class EquipmentWindow(Screen):        
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'distance', 'begin'), 1/20)
        
    def on_pre_leave(self):
        self.event.cancel()

# Window to prompt the person to get within temperature measuring distance
class DistanceWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(self.measure_dist, 1/10)
        
    def on_pre_leave(self):
        self.event.cancel()

    def measure_dist(self, dt):
        global DIST_COUNTER
        global PROGRESS_BAR
        
        print("MEASURING")
        
        if ReadDistance(17) < 10:
            DIST_COUNTER = DIST_COUNTER + 1
            self.ids.progress.value = DIST_COUNTER
            print(DIST_COUNTER)
            if DIST_COUNTER is 10:
                print("Distance is good")
                DIST_COUNTER = 0
                self.manager.current = "temperature"
        else:
            DIST_COUNTER = 0

# Window to measure persons temperature
class TemperatureWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(self.measure_temp, 1/50)
        
    def on_pre_leave(self):
        self.event.cancel()
        
    def measure_temp(self, dt):
        global TEMPERATURE
        global TEMP_COUNTER
        global DISTANCE

        if ReadDistance(17) < 10:
            test_temperature = 2705.06 + ((-7670.457 - 2705.061) / (1 + (chan.voltage / (3.135016*(10**-8)))**0.0595245))
            if test_temperature > 20 and test_temperature < 45:
                TEMPERATURE = TEMPERATURE + test_temperature
                TEMP_COUNTER = TEMP_COUNTER + 1
                DISTANCE = DISTANCE + ReadDistance(17)
                if TEMP_COUNTER is 150:
                    print("Average temperature is:", (TEMPERATURE / TEMP_COUNTER), " Voltage: ", round(chan.voltage, 5), " Distance is:", (DISTANCE/TEMP_COUNTER))
                    if (TEMPERATURE / TEMP_COUNTER) < 40:
                        self.manager.current = "good_temp"
                    else:
                        self.manager.current = "bad_temp"
                    TEMP_COUNTER = 0
                    DISTANCE = 0
                    
        else:
            print("RESTARTING")
            TEMPERATURE = 0
            TEMP_COUNTER = 0
            DISTANCE = 0
            self.manager.current = "distance"
        
# Window if the persons temperature was good
class GoodTempWindow(Screen):
    temperature_display = StringProperty("")
        
    def on_enter(self):
        global TEMPERATURE
        self.temperature_display = TEMPERATURE

# Window if the persons temperature was not good    
class BadTempWindow(Screen):
    pass

# Window Manager
class WindowManager(ScreenManager):
    pass


def answer_input(instance, right, left, dt):
    if keyboard.is_pressed('d'):
        while (keyboard.is_pressed('d')):
            pass
        instance.manager.current = right
    elif keyboard.is_pressed('a'):
        while (keyboard.is_pressed('a')):
            pass
        instance.manager.current = left
    

# Measure distance from sensor and return the value
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

kv = Builder.load_file("my.kv")

sm = WindowManager(transition=NoTransition())
screens = [BeginWindow(name="begin"), InfoWindow(name="info"), CoughWindow(name="cough"), TravelWindow(name="travel"),
           FeverWindow(name="fever"), ContactWindow(name="contact"), EquipmentWindow(name="equipment"),
           DistanceWindow(name="distance"), TemperatureWindow(name="temperature"), GoodTempWindow(name="good_temp"),
           BadTempWindow(name="bad_temp")]
for screen in screens:
    sm.add_widget(screen)


class MyApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    # Window.fullscreen = 'auto'
    MyApp().run()
