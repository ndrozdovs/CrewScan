import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3

from tkinter import *
from tkinter import ttk
import time

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

class SampleApp(tk.Tk):
    
    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        
        self.tk = Tk()
        self.tk.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
        #self.frame = Frame(self.tk)
        #self.frame.pack()
        self.state = False
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, TakeTemp, ShowTemp):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
        
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        
    def get_page(self, page_class):
        return self.frames[page_class]

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Welcome to the CrewScan Kiosk!", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Begin",
                            command=lambda: controller.show_frame("TakeTemp"))
        #button2 = tk.Button(self, text="Go to Page Two",
        #                    command=lambda: controller.show_frame("PageTwo"))
        button1.pack()
        #button2.pack()


class TakeTemp(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Please don't move, taking temperature", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        lbl_temp = tk.Label(self, text = "")
        lbl_temp.pack(side="top", fill="x", pady=10)      
        
        btn_taketemp = tk.Button(self, text="Take my Temperature",
                           command=self.temp_sequence)
        btn_taketemp.pack()
        btn_return = tk.Button(self, text="Go to the start page",
                                   command=lambda: controller.show_frame("StartPage"))
        btn_return.pack()
        
    # Get average temperature
    def temp_sequence(self):
        #page = self.controller.get_page(TakeTemp)
        # Number of readings to take with sensor
        sampling_time = 100
        num_samples = 0
        sum_temp = 0
        temp_progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate",
                                            maximum=sampling_time, value=0)
        temp_progress_bar.pack(side="top", fill="x", pady=10)
        
        t_end = time.time() + sampling_time
        while time.time() < t_end:
            sensor_temp = 2705.06 + ((-7670.457 - 2705.061) / (1 + (chan.voltage / (3.135016*(10**-8)))**0.0595245))
            sum_temp += sensor_temp
            num_samples += 1
            # Update bar
            temp_progress_bar['value'] += 1
            self.update()
                    
        avg_temp = sum_temp / num_samples
        lbl_temp = tk.Label(self, text="Temperature is " + str(round(avg_temp, 2)))
        lbl_temp.pack(side="top", fill="x", pady=10)
        #self.lbl_temp.configure(text = res)


class ShowTemp(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 2", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()


if __name__ == "__main__":
    #w = Fullscreen_Window()
    app = SampleApp()
    app.mainloop()