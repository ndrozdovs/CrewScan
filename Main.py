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


TEMPERATURE = 0       # Global variable to track temperature from the sensor
DIST_COUNTER = 0      # Global variable to track distance from the snesor
TEMP_COUNTER = 0      # Global variable to track the amount of times we measured the temperature
PROGRESS_COUNTER = 0  # Global variable to track and output progress of the progress bar
TIMEOUT_COUNTER = 0   # Global variable to track the timeout of each screen
RIGHT_PEDAL = 16      # Global variable for the right pedal
LEFT_PEDAL = 21       # Global variable for the left pedal
MIDDLE_PEDAL = 20     # Global variable for the middle pedal
POP_ACTIVE = 0        # Global variable to track if we have a pop up active
ERROR_CODE = 0        # Global variable to track the Error COde to be displayed
ERROR_FOUND = 0       # Global variable to track if we have any errors


# Window to start the screening
class BeginWindow(Screen):
    # Execute before entering the screen
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(partial(answer_input, self, 'info', 'begin', 'begin'), 1/20)  # Create event for pedal input, 20 times per second
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 0, 0), 1)                      # Create event for checking screen timeout, 1 time per second
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)                              # Create event for checking for errors, 1 time per second

    # Execute before leaving the screen    
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0    # Reset the timeout counter when leaving the screen
        self.event.cancel()    # Cancel event for pedal input
        self.timeout.cancel()  # Cancel event for pedal input
        self.errors.cancel()   # Cancel event for pedal input
 
# Window to show how to answer to the prompts
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
 
# Window to check if person had contact with an individual with Covid or Covid like symptoms
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
        self.event = Clock.schedule_interval(self.measure_dist, 1/30)  # Create event to measure distance, 30 times per second
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 50, 1), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        
    def on_pre_leave(self):
        global DIST_COUNTER
        global PROGRESS_COUNTER
        global TIMEOUT_COUNTER
        DIST_COUNTER = 0
        PROGRESS_COUNTER = 0
        TIMEOUT_COUNTER = 0
        self.ids.progress.value = PROGRESS_COUNTER  # Update the progress bar counter to 0 when leaving the screen
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()

    # Measure the distance away from the sensor, and make sure the person is within range for 1 second
    def measure_dist(self, dt):
        global DIST_COUNTER
        global PROGRESS_COUNTER
        global MIDDLE_PEDAL
        global ERROR_CODE
        
        # Reset the screening proccess if middle pedal was pressed
        if GPIO.input(MIDDLE_PEDAL) == 0:
            start_time = time.time()
            while (GPIO.input(MIDDLE_PEDAL) == 0):
                if (time.time() - start_time) > 10:
                    ERROR_CODE |= 16
                    instance.manager.current = 'error'
                    return
            self.manager.current = 'begin'
        
        # If distance read from the sensor is less than 10 centimeters
        if ReadDistance(17) < 10:
            DIST_COUNTER = DIST_COUNTER + 1
            PROGRESS_COUNTER = PROGRESS_COUNTER + 3.33  # Increment by 3.33 because progress bar is up to 100 and we execute this for 1 second
            self.ids.progress.value = PROGRESS_COUNTER  # Update the progress bar
            if DIST_COUNTER is 30:
                self.manager.current = "temperature"    # Change screen to measure temperature if we have enough samples of distance
        # If distance is less than 10 centimeters -> reset variables and progress bar, and start measuring again
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

    # Measure the persons temperature for 3 seconds and average it over time      
    def measure_temp(self, dt):
        global TEMPERATURE
        global TEMP_COUNTER
        global PROGRESS_COUNTER
        global MIDDLE_PEDAL
        global ERROR_CODE
        
        # Reset the screening proccess if middle pedal was pressed
        if GPIO.input(MIDDLE_PEDAL) == 0:
            start_time = time.time()
            while (GPIO.input(MIDDLE_PEDAL) == 0):
                if (time.time() - start_time) > 10:
                    ERROR_CODE |= 16
                    instance.manager.current = 'error'
                    return
            self.manager.current = 'begin'

        distance = ReadDistance(17)
        # If person is within 10 cm from the sensor
        if distance < 10:
            # Sometimes the sensor times out and reads 0, this is not an issue so just skip this iteration
            if distance > 3:
                compensation = 1.72255 - (-0.0028336242611106542*distance + 1.739147043467168)                            # Compensation for distance from the sensor
                voltage = chan.voltage + 0.064 + compensation                                                             # Add voltage for proper calibaration
                test_temperature = 2705.06 + ((-7670.457 - 2705.061) / (1 + (voltage / (3.135016*(10**-8)))**0.0595245))  # Convert voltage to degrees Celsius            
                # If temperature is valid, count it as one of the data points
                if test_temperature > 20 and test_temperature < 45:
                    TEMPERATURE = TEMPERATURE + test_temperature
                    TEMP_COUNTER = TEMP_COUNTER + 1
                    PROGRESS_COUNTER = PROGRESS_COUNTER + 1.111
                    self.ids.progress.value = PROGRESS_COUNTER
                    if TEMP_COUNTER is 90:
                        if (TEMPERATURE / TEMP_COUNTER) < 38:
                            self.manager.current = "good_temp"                                                            # If temperature is below 38 degrees, go to good temperature window and print the pass
                        else:
                            self.manager.current = "fail"                                                                 # If temperature is above 38 degrees, go to fail screen
        else:
            TEMPERATURE = 0
            TEMP_COUNTER = 0
            self.manager.current = "distance"
        
# Window if the persons temperature was good
class GoodTempWindow(Screen):
    temperature_display = StringProperty("")  # Create a string object that could be updated and dispalyed on the Kivy screen
    
    def on_pre_enter(self):
        global TEMPERATURE
        global TEMP_COUNTER
        self.event = Clock.schedule_interval(partial(answer_input, self, 'begin', 'distance', 'begin'), 1/20)
        self.timeout = Clock.schedule_interval(partial(timeout_check, self, 10, 0), 1)
        self.errors = Clock.schedule_interval(partial(check_errors, self), 1)
        self.temperature_display = str(round(TEMPERATURE / TEMP_COUNTER, 1))  # Varibale for displaying the temperature on the screen
        TEMPERATURE = 0
        TEMP_COUNTER = 0
        
    def on_enter(self):
        # Create a png image file with todays date and time and then print it 
        fontPath = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"                                # Choose the font
        mono_14 = ImageFont.truetype(fontPath, 14)                                                  # Size 14 font
        mono_20 = ImageFont.truetype(fontPath, 20)                                                  # Size 20 font
  
        img = Image.new('RGB', (200, 100), color = (255, 255, 255))                                 # Create an image object
        dt_string = datetime.now().strftime("%m/%d/%Y %H:%M:%S")                                    # Format the date and time in desired format
        d = ImageDraw.Draw(img)                                                                     # Create an object that we can draw on
        d.text((25,0), "Visitor Pass", fill=(0,0,0), font=mono_20)
        d.text((12,5), "______________", fill=(0,0,0), font=mono_20)
        d.text((5,30), "Access to Site Granted:", fill=(0,0,0), font=mono_14)
        d.text((20,50), str(dt_string), fill=(0,0,0), font=mono_14)
        d.text((150,88), "SetTek", fill=(0,0,0), font=mono_14) 
        img.save('pil_text.png')                                                                    # Save the image file
        os.system("brother_ql -b pyusb -m QL-700 -p usb://0x04f9:0x2042 print -l 62 pil_text.png")  # Send a console print command
        
    def on_pre_leave(self):
        global TIMEOUT_COUNTER
        TIMEOUT_COUNTER = 0
        self.event.cancel()
        self.timeout.cancel()
        self.errors.cancel()

# Not currently used    
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

# Window of the person fails any of the prompts or the temperature reading    
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

# Window if an error was detected        
class ErrorWindow(Screen):
    error_display = StringProperty(str('{0:05b}'.format(ERROR_CODE)))  # Create a string object that could be updated and displayed on the Kivy screen
    
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


# A function for checking if any of the pedals have been pressed
def answer_input(instance, right, left, middle, dt):
    global RIGHT_PEDAL
    global LEFT_PEDAL
    global MIDDLE_PEDAL
    global TIMEOUT_COUNTER
    global POP_ACTIVE
    global ERROR_FOUND
    global ERROR_CODE
    
    # If Timeout counter has started, we don't have a pop up active and have no errors
    if TIMEOUT_COUNTER > 0 and POP_ACTIVE == 0 and ERROR_FOUND == 0:
        start_time = time.time()                        # Track the time in order to see if pedals ahve timed out and raise an error
        # If right pedal is pressed
        if GPIO.input(RIGHT_PEDAL) == 0:
            while (GPIO.input(RIGHT_PEDAL) == 0):
                if (time.time() - start_time) > 10:
                    ERROR_CODE |= 16                    # If Right pedal is still pressed after 10 seconds, raise an error
                    instance.manager.current = 'error'  # Change screen to an error screen
                    return                              # Return from this infinite loop
            instance.manager.current = right            # Chnage screen to the right varibale if Right pedal is pressed
        elif GPIO.input(LEFT_PEDAL) == 0:
            while (GPIO.input(LEFT_PEDAL) == 0):
                if (time.time() - start_time) > 10:
                    ERROR_CODE |= 16
                    instance.manager.current = 'error'
                    return
            instance.manager.current = left
        elif GPIO.input(MIDDLE_PEDAL) == 0:
            while (GPIO.input(MIDDLE_PEDAL) == 0):
                if (time.time() - start_time) > 10:
                    ERROR_CODE |= 16
                    instance.manager.current = 'error'
                    return
            instance.manager.current = middle
    # If pop up is active on the screen
    elif POP_ACTIVE == 1:
        start_time = time.time() 
        # Use right pedal as a dismiss for the pop up
        if GPIO.input(RIGHT_PEDAL) == 0:
            while (GPIO.input(RIGHT_PEDAL) == 0):
                if (time.time() - start_time) > 10:
                    ERROR_CODE |= 16
                    instance.manager.current = 'error'
                    instance.pop.dismiss()
                    POP_ACTIVE = 0
                    TIMEOUT_COUNTER = 0
                    return 
            instance.pop.dismiss()
            POP_ACTIVE = 0
            TIMEOUT_COUNTER = 0
        

# Function to check for timeout on each screen        
def timeout_check(instance, timeout_val, activate_pop, dt):
    global TIMEOUT_COUNTER
    global POP_ACTIVE
    global ERROR_FOUND
    TIMEOUT_COUNTER = TIMEOUT_COUNTER + 1
    
    # Don't check for a timeout on begin screen or if an error is found
    if instance.manager.current is not 'begin' and ERROR_FOUND == 0:
        # Not every screen requires a pop up, so this varibale gets passed in by the caller
        if activate_pop == 1:
            # If time copunter is equal to the value passed by the caller, make a pop up
            if TIMEOUT_COUNTER is timeout_val:
                timeout_pop(instance)  # Open a pop up window
                POP_ACTIVE = 1
            if TIMEOUT_COUNTER >= timeout_val:
                instance.show.ids.progress.value = 10 * (TIMEOUT_COUNTER - timeout_val)  # Progress bar for the pop up window
            # If pop up has been active for 10 seconds, bring the user to begin screen and dismiss the pop up
            if TIMEOUT_COUNTER is (timeout_val + 10) and POP_ACTIVE == 1:
                instance.manager.current = 'begin'
                instance.pop.dismiss()
                POP_ACTIVE = 0
        # If timeout has been hit, but no pop up was activated, bring user to begin screen
        elif TIMEOUT_COUNTER is timeout_val:
            instance.manager.current = 'begin'


# Function for creating a pop up window
def timeout_pop(instance):
    instance.show = Popups()    
    instance.pop = Popup(title='Warning', content=instance.show, size_hint=(None, None), size=(400, 250))
    instance.pop.open()
    

# Function for checking various errors such as: Temperature sensor, ADC, distance sensor, printer and pedals    
def check_errors(instance, dt):
    global RIGHT_PEDAL
    global LEFT_PEDAL
    global MIDDLE_PEDAL
    global POP_ACTIVE
    global ERROR_CODE
    global ERROR_FOUND
    # Each variable corresponds to each bit, the value is its bit value
    temp_sensor = 1  # If temperature sensor is broken, raise bit 0
    adc = 2          # If adc is broken, raise bit 1
    dist_sensor = 4  # If distance sensor is broken, raise bit 2
    printer = 8      # If printer is offline, raise bit 3
    pedals = 16      # If pedals are pressed for > 10 seconds, raise bit 4
    
    # Try to create an adc object, if there is an exception raise the correct bit
    try:
        check_i2c = busio.I2C(board.SCL, board.SDA)
        check_ads = ADS.ADS1115(check_i2c)        # Create ADC object
        check_chan = AnalogIn(check_ads, ADS.P0)  # Create analog input channel
        # If we did not hit an excpetion yet, check if adc error bit is already high and put it to low
        if (ERROR_CODE & adc) == adc:
            ERROR_CODE ^= adc                     # Make adc bit low
        # Check if voltage from temperature sensor is below 1    
        if check_chan.voltage < 1:
            ERROR_CODE |= temp_sensor             # Make temperature sensor bit high
        # Else check if the temperature sensor bit is already high, and put it to low
        elif (ERROR_CODE & temp_sensor) == temp_sensor:
            ERROR_CODE ^= temp_sensor             # Make temperature sensor bit low
    except:
        ERROR_CODE |= adc                         # Make adc bit high if there was an exception during adc setup
    
    # Read the distance 5 times, if >= 3, raise an error. The try is needed to handle excpetions for when distance sensor gets plugged and unplugged
    try:
        counter = 0
        for loop in range(5):
            if ReadDistance(17) != 0:
                if (ERROR_CODE & dist_sensor) == dist_sensor:
                    ERROR_CODE ^= dist_sensor
                counter += 1
            elif loop == 4:
                if counter < 2:
                    ERROR_CODE |= dist_sensor
    except:
        pass
    
    # Send a console command to check for available usb devices, if can't find the printer string, then raise an error
    if "04f9:2042" not in str(subprocess.check_output("lsusb", shell=True)):
        ERROR_CODE |= printer          
    elif (ERROR_CODE & printer) == printer:
        ERROR_CODE ^= printer

    # If pedals error is already raised, check if all of them are unpressed, then set error bit to low    
    if (ERROR_CODE & pedals) == pedals:
        if GPIO.input(RIGHT_PEDAL) == 1 and GPIO.input(LEFT_PEDAL) == 1 and GPIO.input(MIDDLE_PEDAL) == 1:
            ERROR_CODE ^= pedals        
  
    if ERROR_CODE != 0:
        ERROR_FOUND = 1                     # If error code is not 0, indicate that we found an error
        instance.manager.current = 'error'  # Change user to error screen
        # If there is a popup active, dismiss it as its useless now
        if POP_ACTIVE == 1:
            instance.pop.dismiss()
            POP_ACTIVE = 0
            TIMEOUT_COUNTER = 0 
    # If error code is finally 0, and error was found, bring user back to begin screen
    elif ERROR_CODE == 0 and ERROR_FOUND == 1:
        instance.manager.current = 'begin'
        ERROR_FOUND = 0

    # Update the error code on the error screen    
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
    distance=duration*34000/2  # Distance is defined as time/2 (there and back) * speed of sound 34000 cm/s 
    return distance


try:
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)                                 # Create ADC object
    chan = AnalogIn(ads, ADS.P0)                           # Create analog input channel
except:
    pass

GPIO.setmode(GPIO.BCM)                                     # Set GPIO mode to BCM
GPIO.setup(RIGHT_PEDAL,GPIO.IN,pull_up_down=GPIO.PUD_UP)   # Setup Right pedal as GPIO
GPIO.setup(LEFT_PEDAL,GPIO.IN,pull_up_down=GPIO.PUD_UP)    # Setup Left pedal as GPIO
GPIO.setup(MIDDLE_PEDAL,GPIO.IN,pull_up_down=GPIO.PUD_UP)  # Setup Middle pedal as GPIO

Window.size = (480, 800)                                   # Set screen size to 480x800, if we don't want to use fullscreen (should be fullscreen is final version)

kv = Builder.load_file("my.kv")                            # Load .kv file for GUI interface

# Setup the screen manager
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
