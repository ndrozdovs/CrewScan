# Temp data and fullscreen gui test
# Luke Bidulka

import sys
if sys.version_info[0] == 2:  # Just checking your Python version to import Tkinter properly.
    from Tkinter import *
else:
    from tkinter import *
    from tkinter import ttk


class Fullscreen_Window:

    def __init__(self):
        self.tk = Tk()
        self.tk.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
        self.frame = Frame(self.tk)
        self.frame.pack()
        self.state = False
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"
    
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


if __name__ == '__main__':
    w = Fullscreen_Window()
    
    # Creating welcome tab
    tabControl = ttk.Notebook(w.tk)
    welcome_tab = ttk.Frame(tabControl)
    tabControl.add(welcome_tab, text = '1 - Welcome')
    temp_tab = ttk.Frame(tabControl)
    tabControl.add(temp_tab, text = '2 - Temperature')
    tabControl.pack( fill="both")
    
    # Add a label
    lbl_temp = Label(welcome_tab, text = "Hello", font = ("Arial Bold", 25))
    lbl_temp.pack()
    

    # Function to execute when button is clicked
    def clicked():
        # Rough calc for temperature & print values
        sensor_temp = 2705.06 + ((-7670.457 - 2705.061) / (1 + (chan.voltage / (3.135016*(10**-8)))**0.0595245))
        res = "Temperature is " + str(round(sensor_temp, 2))
        lbl_temp.configure(text = res)
      
    # Add a button
    btn_verify = Button(welcome_tab, text = "Click Me to Continue", command = clicked)
    btn_verify.pack()

    w.tk.mainloop()