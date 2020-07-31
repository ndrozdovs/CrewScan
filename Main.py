from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
import keyboard
from kivy.core.window import Window
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time
import RPi.GPIO as GPIO


class BeginWindow(Screen):
    pass

class InfoWindow(Screen):
    pass

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
    
class TemperatureWindow(Screen):
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


i2c = busio.I2C(board.SCL, board.SDA)
# Create ADC object
ads = ADS.ADS1115(i2c)
# Create analog input channel
chan = AnalogIn(ads, ADS.P0)

GPIO.setmode(GPIO.BCM)

pop_active = 0
kv = Builder.load_file("my.kv")

sm = WindowManager()
screens = [BeginWindow(name="begin"), InfoWindow(name="info"), CoughWindow(name="cough"), TravelWindow(name="travel"),
           FeverWindow(name="fever"), ContactWindow(name="contact"), EquipmentWindow(name="equipment"),
           TemperatureWindow(name="temperature")]
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
                    #temp = 2705.06 + ((-7670.457 - 2705.061) / (1 + (chan.voltage / (3.135016*(10**-8)))**0.0595245))
                    #distance = ReadDistance(17)
                    #print ("Distance to object:",distance*.3937," inches    temperature:",round(temp,3), " degrees")
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
                        self.root.current = 'temperature'
                        self.root.transition.direction = "left"
                        
                elif self.root.current is 'equipment':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'temperature'
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
                        self.root.current = 'temp'
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
