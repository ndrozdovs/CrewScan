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
from datetime import datetime
import os
import subprocess
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
RIGHT_PEDAL = 20
LEFT_PEDAL = 21
MIDDLE_PEDAL = 16
POP_ACTIVE = 0
ERROR_CODE = 0
ERROR_FOUND = 0


# Window to start the screening
class BeginWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'info', 'begin', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 0, 0), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()
 
# Window to show how to answer to prompts
class InfoWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'cough', 'begin', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 50, 1), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()

# Window to check for new cough or fever symptoms
class CoughWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'fail', 'travel', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 50, 1), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()

# Window to check if person traveled outside of Canada
class TravelWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'fail', 'fever', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 50, 1), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()

# Window to check if person has a fever    
class FeverWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'fail', 'contact', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 50, 1), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()
 
# Window to check if person had to contact with an individual with Covid or Covid like symptoms
class ContactWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'equipment', 'distance', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 50, 1), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()

# Window to check if person was wearing protective equipment if they were exsposed to an individual with Covid
class EquipmentWindow(Screen):        
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'distance', 'fail', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 50, 1), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()

# Window to prompt the person to get within temperature measuring distance
class DistanceWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(self.measure_dist, 1/30)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 50, 1), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
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
        self.errors.cancel()

    def measure_dist(self, dt):
        global DIST_COUNTER
        global PROGRESS_COUNTER
        global MIDDLE_PEDAL
        global ERROR_CODE
        
        #if GPIO.input(MIDDLE_PEDAL) == 0:
            #start_time = time.time()
            #while (GPIO.input(MIDDLE_PEDAL) == 0):
                #if (time.time() - start_time) > 10:
                    #ERROR_CODE |= 16
                    #instance.manager.current = 'error'
                    #return
            #self.manager.current = 'begin'
        
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
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 50, 1), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global PROGRESS_COUNTER
        global TIMEOUT_COUNTER
        PROGRESS_COUNTER = 0
        TIMEOUT_COUNTER = 0
        self.ids.progress.value = PROGRESS_COUNTER
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()
        
    def measure_temp(self, dt):
        global TEMPERATURE
        global TEMP_COUNTER
        global PROGRESS_COUNTER
        global MIDDLE_PEDAL
        global ERROR_CODE
        
        #if GPIO.input(MIDDLE_PEDAL) == 0:
            #start_time = time.time()
            #while (GPIO.input(MIDDLE_PEDAL) == 0):
                #if (time.time() - start_time) > 10:
                    #ERROR_CODE |= 16
                    #instance.manager.current = 'error'
                    #return
            #self.manager.current = 'begin'

        distance = ReadDistance(17)
        if distance < 10:
            if distance is not 0:
                voltage = chan.voltage + 0.05
                test_temperature = 2705.06 + ((-7670.457 - 2705.061) / (1 + (voltage / (3.135016*(10**-8)))**0.0595245))
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
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 10, 0), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        self.temperature_display = str(round(TEMPERATURE / TEMP_COUNTER, 1))
        TEMPERATURE = 0
        TEMP_COUNTER = 0
        
    def on_enter(self):
        # Create a png image file with todays date, print it if access to site was granted    
        fontPath = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        mono_14 = ImageFont.truetype(fontPath, 14)
        mono_20 = ImageFont.truetype(fontPath, 20)
  
        img = Image.new('RGB', (200, 100), color = (255, 255, 255))
        dt_string = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        d = ImageDraw.Draw(img)
        d.text((25,0), "Visitor Pass", fill=(0,0,0), font=mono_20)
        d.text((12,5), "______________", fill=(0,0,0), font=mono_20)
        d.text((5,30), "Access to Site Granted:", fill=(0,0,0), font=mono_14)
        d.text((20,50), str(dt_string), fill=(0,0,0), font=mono_14)
        d.text((150,88), "SetTek", fill=(0,0,0), font=mono_14) 
        img.save('pil_text.png')
        os.system("brother_ql -b pyusb -m QL-700 -p usb://0x04f9:0x2042 print -l 62 pil_text.png")
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()

# Window if the persons temperature was not good    
class BadTempWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'begin', 'fail', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 10, 0), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()
    
class FailWindow(Screen):
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'begin', 'fail', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 10, 0), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()
        
class ErrorWindow(Screen):
    error_display = StringProperty(str('{0:05b}'.format(ERROR_CODE)))
    
    def on_pre_enter(self):
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        self.errors.cancel()
        
# Window Manager
class WindowManager(ScreenManager):
    pass
 
# Used for adding text and progress bar for the pop up window in .kv file  
class Popups(FloatLayout): 
    pass


def answer_input(instance, right, left, middle, dt):
    global RIGHT_PEDAL
    global LEFT_PEDAL
    global MIDDLE_PEDAL
    global TIMEOUT_COUNTER
    global POP_ACTIVE
    global ERROR_FOUND
    global ERROR_CODE
    
    if TIMEOUT_COUNTER > 0 and POP_ACTIVE == 0 and ERROR_FOUND == 0:
        start_time = time.time()
        if GPIO.input(RIGHT_PEDAL) == 0:
            while (GPIO.input(RIGHT_PEDAL) == 0):
                if (time.time() - start_time) > 10:
                    ERROR_CODE |= 16
                    instance.manager.current = 'error'
                    return
            instance.manager.current = right
        elif GPIO.input(LEFT_PEDAL) == 0:
            while (GPIO.input(LEFT_PEDAL) == 0):
                if (time.time() - start_time) > 10:
                    ERROR_CODE |= 16
                    instance.manager.current = 'error'
                    return
            instance.manager.current = left
        #elif GPIO.input(MIDDLE_PEDAL) == 0:
            #while (GPIO.input(MIDDLE_PEDAL) == 0):
                #if (time.time() - start_time) > 10:
                    #ERROR_CODE |= 16
                    #instance.manager.current = 'error'
                    #return
            #instance.manager.current = middle
    elif POP_ACTIVE == 1:
        if GPIO.input(RIGHT_PEDAL) == 0:
            while (GPIO.input(RIGHT_PEDAL) == 0):
                pass
            instance.pop.dismiss()
            POP_ACTIVE = 0
            TIMEOUT_COUNTER = 0
        
        
def timeout_check(instance, timeout_val, activate_pop, dt):
    global TIMEOUT_COUNTER
    global POP_ACTIVE
    global ERROR_FOUND
    TIMEOUT_COUNTER = TIMEOUT_COUNTER + 1
    
    if instance.manager.current is not 'begin' and ERROR_FOUND == 0:
        if activate_pop == 1:
            if TIMEOUT_COUNTER is timeout_val:
                timeout_pop(instance)
                POP_ACTIVE = 1
            if TIMEOUT_COUNTER >= timeout_val:
                instance.show.ids.progress.value = 10 * (TIMEOUT_COUNTER - timeout_val)
            if TIMEOUT_COUNTER is (timeout_val + 10) and POP_ACTIVE == 1:
                instance.manager.current = 'begin'
                instance.pop.dismiss()
                POP_ACTIVE = 0
        elif TIMEOUT_COUNTER is timeout_val:
            instance.manager.current = 'begin'


def timeout_pop(instance):
    instance.show = Popups()    
    instance.pop = Popup(title='Warning', content=instance.show, size_hint=(None, None), size=(400, 250))
    instance.pop.open()
    
    
def check_errors(instance, dt):
    global RIGHT_PEDAL
    global LEFT_PEDAL
    global MIDDLE_PEDAL
    global POP_ACTIVE
    global ERROR_CODE
    global ERROR_FOUND
    temp_sensor = 1
    adc = 2
    dist_sensor = 4
    printer = 8
    pedals = 16
    
    try:
        check_i2c = busio.I2C(board.SCL, board.SDA)
        check_ads = ADS.ADS1115(check_i2c) #Create ADC object
        check_chan = AnalogIn(check_ads, ADS.P0) #Create analog input channel
        if (ERROR_CODE & adc) == adc:
            ERROR_CODE ^= adc
        if check_chan.voltage < 1:
            ERROR_CODE |= temp_sensor
        elif (ERROR_CODE & temp_sensor) == temp_sensor:
            ERROR_CODE ^= temp_sensor
    except:
        ERROR_CODE |= adc
    
    try:
        for loop in range(5):
            if ReadDistance(17) != 0:
                if (ERROR_CODE & dist_sensor) == dist_sensor:
                    ERROR_CODE ^= dist_sensor
                break
            elif loop == 4:
                ERROR_CODE |= dist_sensor
    except:
        print("oops")
    
    if "04f9:2042" not in str(subprocess.check_output("lsusb", shell=True)):
        ERROR_CODE |= printer          
    elif (ERROR_CODE & printer) == printer:
        ERROR_CODE ^= printer
        
    if (ERROR_CODE & pedals) == pedals:
        if GPIO.input(RIGHT_PEDAL) == 1 and GPIO.input(LEFT_PEDAL) == 1 and GPIO.input(MIDDLE_PEDAL) == 1:
            ERROR_CODE ^= pedals        
        
    if ERROR_CODE != 0:
        ERROR_FOUND = 1
        instance.manager.current = 'error'
        if POP_ACTIVE == 1:
            instance.pop.dismiss()
            POP_ACTIVE = 0
            TIMEOUT_COUNTER = 0 
    elif ERROR_CODE == 0 and ERROR_FOUND == 1:
        instance.manager.current = 'begin'
        ERROR_FOUND = 0
        
    if instance.manager.current == 'error':
        instance.error_display = str('{0:05b}'.format(ERROR_CODE))
        
    
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
try:
    ads = ADS.ADS1115(i2c)       #Create ADC object
    chan = AnalogIn(ads, ADS.P0) #Create analog input channel
except:
    pass

GPIO.setmode(GPIO.BCM)
GPIO.setup(RIGHT_PEDAL,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(LEFT_PEDAL,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(MIDDLE_PEDAL,GPIO.IN,pull_up_down=GPIO.PUD_UP)

Window.size = (480, 800)

kv = Builder.load_file("my.kv")

sm = WindowManager(transition=NoTransition())
screens = [BeginWindow(name="begin"), InfoWindow(name="info"), CoughWindow(name="cough"), TravelWindow(name="travel"),
           FeverWindow(name="fever"), ContactWindow(name="contact"), EquipmentWindow(name="equipment"),
           DistanceWindow(name="distance"), TemperatureWindow(name="temperature"), GoodTempWindow(name="good_temp"),
           BadTempWindow(name="bad_temp"), FailWindow(name="fail"), ErrorWindow(name="error")]
for screen in screens:
    sm.add_widget(screen)


class MyApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    #Window.fullscreen = 'auto'
    MyApp().run()
