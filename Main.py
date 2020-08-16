from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout 
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from functools import partial
from adafruit_ads1x15.analog_in import AnalogIn
from PIL import Image, ImageDraw, ImageFont
from datetime import date
import os
import adafruit_ads1x15.ads1115 as ADS
import keyboard
import board
import busio
import time
import RPi.GPIO as GPIO


TEMPERATURE = 0
DIST_COUNTER = 0
TEMP_COUNTER = 0
PROGRESS_COUNTER = 0
TIMEOUT_COUNTER = 0
RIGHT_PEDAL = 16
LEFT_PEDAL = 21
MIDDLE_PEDAL = 20


# Window to start the screening
class BeginWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'info', 'begin', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
 
# Window to show how to answer to prompts
class InfoWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'cough', 'begin', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()

# Window to check for new cough or fever symptoms
class CoughWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'fail', 'travel', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()

# Window to check if person traveled outside of Canada
class TravelWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'fail', 'fever', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()

# Window to check if person has a fever    
class FeverWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'fail', 'contact', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
 
# Window to check if person had to contact with an individual with Covid or Covid like symptoms
class ContactWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'equipment', 'distance', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()

# Window to check if person was wearing protective equipment if they were exsposed to an individual with Covid
class EquipmentWindow(Screen):        
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'distance', 'fail', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()

# Window to prompt the person to get within temperature measuring distance
class DistanceWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(self.measure_dist, 1/30)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global DIST_COUNTER
        global PROGRESS_COUNTER
        global TIMEOUT_COUNTER
        DIST_COUNTER = 0
        PROGRESS_COUNTER = 0
        TIMEOUT_COUNTER = 0
        self.ids.progress.value = PROGRESS_COUNTER
        self.event.cancel()
        self.timeout.cancel()

    def measure_dist(self, dt):
        global DIST_COUNTER
        global PROGRESS_COUNTER
        
        if ReadDistance(17) < 10:
            DIST_COUNTER = DIST_COUNTER + 1
            PROGRESS_COUNTER = PROGRESS_COUNTER + 3.33
            self.ids.progress.value = PROGRESS_COUNTER
            if DIST_COUNTER is 30:
                self.manager.current = "temperature"
        else:
            DIST_COUNTER = 0
            PROGRESS_COUNTER = 0
            self.ids.progress.value = PROGRESS_COUNTER

# Window to measure persons temperature
class TemperatureWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(self.measure_temp, 1/30)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global PROGRESS_COUNTER
        global TIMEOUT_COUNTER
        PROGRESS_COUNTER = 0
        TIMEOUT_COUNTER = 0
        self.ids.progress.value = PROGRESS_COUNTER
        self.event.cancel()
        self.timeout.cancel()
        
    def measure_temp(self, dt):
        global TEMPERATURE
        global TEMP_COUNTER
        global PROGRESS_COUNTER

        distance = ReadDistance(17)
        if distance < 10:
            if distance is not 0:
                test_temperature = 2705.06 + ((-7670.457 - 2705.061) / (1 + (chan.voltage / (3.135016*(10**-8)))**0.0595245))
                if test_temperature > 20 and test_temperature < 45:
                    TEMPERATURE = TEMPERATURE + test_temperature
                    TEMP_COUNTER = TEMP_COUNTER + 1
                    PROGRESS_COUNTER = PROGRESS_COUNTER + 1.111
                    self.ids.progress.value = PROGRESS_COUNTER
                    if TEMP_COUNTER is 90:
                        if (TEMPERATURE / TEMP_COUNTER) < 38:
                            self.manager.current = "good_temp"
                        else:
                            self.manager.current = "bad_temp"
                    
        else:
            TEMPERATURE = 0
            TEMP_COUNTER = 0
            self.manager.current = "distance"
        
# Window if the persons temperature was good
class GoodTempWindow(Screen):
    temperature_display = StringProperty("")
    
    def on_pre_enter(self):
        global TEMPERATURE
        global TEMP_COUNTER
        self.event = Clock.schedule_interval(partial(answer_input, self, 'begin', 'distance', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        self.temperature_display = str(round(TEMPERATURE / TEMP_COUNTER, 1))
        TEMPERATURE = 0
        TEMP_COUNTER = 0
        
    def on_enter(self):
        os.system("brother_ql -b pyusb -m QL-700 -p usb://0x04f9:0x2042 print -l 62 pil_text.png")
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()

# Window if the persons temperature was not good    
class BadTempWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'begin', 'fail', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
    
class FailWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'begin', 'fail', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()

# Window Manager
class WindowManager(ScreenManager):
    pass
    
class Popups(FloatLayout): 
    pass


def answer_input(instance, right, left, middle, dt):
    global RIGHT_PEDAL
    global LEFT_PEDAL
    global MIDDLE_PEDAL
    global TIMEOUT_COUNTER
    
    if TIMEOUT_COUNTER > 0:
        if GPIO.input(RIGHT_PEDAL) == 0:
            while (GPIO.input(RIGHT_PEDAL) == 0):
                pass
            instance.manager.current = right
        elif GPIO.input(LEFT_PEDAL) == 0:
            while (GPIO.input(LEFT_PEDAL) == 0):
                pass
            instance.manager.current = left
        elif GPIO.input(MIDDLE_PEDAL) == 0:
            while (GPIO.input(MIDDLE_PEDAL) == 0):
                pass
            instance.manager.current = middle
        

def timeout_check(instance, dt):
    global TIMEOUT_COUNTER
    TIMEOUT_COUNTER = TIMEOUT_COUNTER + 1
    
    if instance.manager.current is not 'begin':
        if TIMEOUT_COUNTER is 50:
            timeout_pop(instance)
            instance.pop.open()
        if TIMEOUT_COUNTER >= 50:
            instance.show.ids.progress.value = 10 * (TIMEOUT_COUNTER - 5)
        if TIMEOUT_COUNTER is 60:
            instance.manager.current = 'begin'
            instance.pop.dismiss()


def timeout_pop(instance):
    instance.show = Popups()    
    instance.pop = Popup(title='Warning', content=instance.show, size_hint=(None, None), size=(400, 250))
    instance.pop.open()
    

# Measure distance from sensor and return the value
def ReadDistance(pin):
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
    # Distance is defined as time/2 (there and back) * speed of sound 34000 cm/s 
    distance=duration*34000/2
    return distance


i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)       #Create ADC object
chan = AnalogIn(ads, ADS.P0) #Create analog input channel

GPIO.setmode(GPIO.BCM)
GPIO.setup(RIGHT_PEDAL,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(LEFT_PEDAL,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(MIDDLE_PEDAL,GPIO.IN,pull_up_down=GPIO.PUD_UP)

Window.size = (800, 480)

kv = Builder.load_file("my.kv")

sm = WindowManager(transition=NoTransition())
screens = [BeginWindow(name="begin"), InfoWindow(name="info"), CoughWindow(name="cough"), TravelWindow(name="travel"),
           FeverWindow(name="fever"), ContactWindow(name="contact"), EquipmentWindow(name="equipment"),
           DistanceWindow(name="distance"), TemperatureWindow(name="temperature"), GoodTempWindow(name="good_temp"),
           BadTempWindow(name="bad_temp"), FailWindow(name="fail")]
for screen in screens:
    sm.add_widget(screen)

# Create a png image file with todays date, print it if access to site was granted    
fontPath = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
font_mono = ImageFont.truetype(fontPath, 14)
 
img = Image.new('RGB', (200, 100), color = (255, 255, 255)) 
d = ImageDraw.Draw(img)
d.text((5,30), "Access to Site Granted:", fill=(0,0,0), font=font_mono)
d.text((60,50), str(date.today()), fill=(0,0,0), font=font_mono)
img.save('pil_text.png')


class MyApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    # Window.fullscreen = 'auto'
    MyApp().run()
