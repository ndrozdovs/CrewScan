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


TEMPERATURE = 0
COUNTER = 0


class BeginWindow(Screen):
    pass
    
class InfoWindow(Screen):
    string_dummy = StringProperty("")
    
    def bullshit(self, dt):
        global COUNTER
        self.string_dummy = str(COUNTER)
        COUNTER = COUNTER + 1
    
    def on_enter(self):
        Clock.schedule_interval(self.bullshit, 1)
        print("HERE")
        #while counter < 500:
            #self.string_dummy = str(counter)
            #counter = counter + 1
        #self.string_dummy = str(TEMPERATURE)
        #time.sleep(2)
        #self.string_dummy = "HI"

class CoughWindow(Screen):
    pass

class TravelWindow(Screen):
    pass
    
class FeverWindow(Screen):
    pass
    
class ContactWindow(Screen):
    pass
    
class EquipmentWindow(Screen):
    pass
    
class DistanceWindow(Screen):
    def on_enter(self):
        Clock.schedule_once(self.measureDist)

    def measureDist(self, dt):
        dist_counter = 0
        
        print("MEASURING")
        
        while dist_counter <= 2:
            if ReadDistance(17) < 100:
                dist_counter = dist_counter + 1
            else:
                dist_counter = 0
            time.sleep(0.1)
        
        print("Distance is good")
        self.manager.current = "temperature"
        

class TemperatureWindow(Screen):
    def on_enter(self):
        Clock.schedule_once(self.measureTemp) 
        
    def measureTemp(self, dt):
        global TEMPERATURE
        temp_counter = 0
        distance = 0
        
        while temp_counter <= 15:
            if ReadDistance(17) < 100:
                test_temperature = 2705.06 + ((-7670.457 - 2705.061) / (1 + (chan.voltage / (3.135016*(10**-8)))**0.0595245))
                if test_temperature > 20 and test_temperature < 45:
                    TEMPERATURE = TEMPERATURE + test_temperature
                    temp_counter = temp_counter + 1
                    distance = distance + ReadDistance(17)
            else:
                print("RESTARTING")
                TEMPERATURE = 0
                self.manager.current = "distance"
            time.sleep(0.02)
        
        print("Average temperature is:", (TEMPERATURE / temp_counter), " Voltage: ", round(chan.voltage, 5), " Distance is:", (distance/temp_counter))
        
        if (TEMPERATURE / temp_counter) < 40:
            self.manager.current = "good_temp"
        else:
            self.manager.current = "bad_temp"
            
class GoodTempWindow(Screen):
    temperature_display = StringProperty("")
        
    def on_enter(self):
        global TEMPERATURE
        self.temperature_display = TEMPERATURE
    
class BadTempWindow(Screen):
    pass

class WindowManager(ScreenManager):
    pass


def invalidAnswer():
    pop = Popup(title='Warning',
                content=Label(text='Warning: Invalid answer'),
                size_hint=(None, None), size=(400, 400))
    pop.open()
    return pop


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


#i2c = busio.I2C(board.SCL, board.SDA)
# Create ADC object
#ads = ADS.ADS1115(i2c)
# Create analog input channel
#chan = AnalogIn(ads, ADS.P0)

GPIO.setmode(GPIO.BCM)

pop_active = 0
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
        def answer_input(dt):
            global pop_active
            if pop_active == 0:
                if self.root.current is 'begin':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'info'
                        self.root.transition.direction = "left"

                elif self.root.current is 'info':
                    #App.get_running_app().root.string_dummy = "NO"
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'cough'
                        self.root.transition.direction = "left"
                    elif keyboard.is_pressed('a'):
                        while (keyboard.is_pressed('a')):
                            pass
                        self.root.current = 'begin'
                        self.root.transition.direction = "right"

                elif self.root.current is 'cough':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'begin'
                        self.root.transition.direction = "right"
                        self.pop = invalidAnswer()
                        pop_active = 1
                    elif keyboard.is_pressed('a'):
                        while (keyboard.is_pressed('a')):
                            pass
                        self.root.current = 'travel'
                        self.root.transition.direction = "left"

                elif self.root.current is 'travel':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'begin'
                        self.root.transition.direction = "right"
                        self.pop = invalidAnswer()
                        pop_active = 1
                    elif keyboard.is_pressed('a'):
                        while (keyboard.is_pressed('a')):
                            pass
                        self.root.current = 'fever'
                        self.root.transition.direction = "left"
                
                elif self.root.current is 'fever':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'begin'
                        self.root.transition.direction = "right"
                        self.pop = invalidAnswer()
                        pop_active = 1
                    elif keyboard.is_pressed('a'):
                        while (keyboard.is_pressed('a')):
                            pass
                        self.root.current = 'contact'
                        self.root.transition.direction = "left"
                        
                elif self.root.current is 'contact':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'equipment'
                        self.root.transition.direction = "left"
                    elif keyboard.is_pressed('a'):
                        while (keyboard.is_pressed('a')):
                            pass
                        self.root.current = 'distance'
                        self.root.transition.direction = "left"
                        
                elif self.root.current is 'equipment':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'distance'
                        self.root.transition.direction = "left"
                    elif keyboard.is_pressed('a'):
                        while (keyboard.is_pressed('a')):
                            pass
                        self.root.current = 'begin'
                        self.root.transition.direction = "right"
                        self.pop = invalidAnswer()
                        pop_active = 1
                        
                elif self.root.current is 'temperature':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'begin'
                        self.root.transition.direction = "right"
                    elif keyboard.is_pressed('a'):
                        while (keyboard.is_pressed('a')):
                            pass
                        self.root.current = 'distance'
                        self.root.transition.direction = "right"

            elif pop_active == 1:
                if keyboard.is_pressed('d'):
                    while (keyboard.is_pressed('d')):
                        pass
                    self.pop.dismiss()
                    pop_active = 0

        Clock.schedule_interval(answer_input, 1/20)

        return sm


if __name__ == "__main__":
    # Window.fullscreen = 'auto'
    MyApp().run()
