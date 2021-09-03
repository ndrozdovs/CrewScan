import sys
if sys.version_info[0] == 2:  # Just checking your Python version to import Tkinter properly.
    from Tkinter import *
else:
    from tkinter import *


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

if __name__ == '__main__':
    w = Fullscreen_Window()
    
    # Add a label
    lbl_temp = Label(w.tk, text = "Please enter your temperature", font = ("Arial Bold", 25))
    lbl_temp.pack()
    # Add entry class
    txt_temp = Entry(w.tk, width = 10)
    txt_temp.pack()
    # Add checkbox text
    lbl_chktxt = Label(w.tk, text = "Tick the boxes if the statements below apply to you", font = ("Arial Bold", 15))
    lbl_chktxt.pack()
    # Create CheckButton Widget
    chk_BC = Checkbutton(w.tk, text = "I Have travelled outside of BC in the last 2 weeks?")
    chk_BC.pack()

    # Function to execute when button is clicked
    def clicked():
        res = "Temperature is " + txt_temp.get()
        lbl_temp.configure(text = res)
        txt_temp.configure(state = 'disabled')
        chk_BC.configure(state = 'disabled')
        # Info
        #messagebox.showinfo('Result','Heres a tip:...')
        # Warning
        #messagebox.showwarning('Result','Be aware that...')
        # Error
        #messagebox.showerror('Result','Error...')
        # yes/no message box for the user
        #res = messagebox.askquestion('Screening Question', 'Have you had flu symptoms')

    # Add a button
    btn_verify = Button(w.tk, text = "Click Me to Continue", command = clicked)
    btn_verify.pack()

    w.tk.mainloop()