
# Import tkinter package and create a window
from tkinter import *
from tkinter.ttk import *

# Add a Message Box
from tkinter import messagebox

window = Tk()

window.title("CrewScan Interface")
# Set default window size
window.geometry('600x200')

# Create combobox widget
#combo = Combobox(window, values = ["yes", "no"])
#combo.current(1)
#combo.grid(column = 0, row = 3)

# Create CheckButton Widget
chk_BC = Checkbutton(window, text = "I Have travelled outside of BC in the last 2 weeks?")

# Add a label
lbl_temp = Label(window, text = "Please enter your temperature", font = ("Arial Bold", 25))
lbl_chktxt = Label(window, text = "Tick the boxes if the statements below apply to you", font = ("Arial Bold", 15))
#lbl_BC = Label(window, text = "Have you been outside BC in the last 2 weeks?")


#lbl_BC.grid(column = 0, row = 2)
# Add entry class
txt_temp = Entry(window, width = 10)

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
btn_verify = Button(window, text = "Click Me to Continue", command = clicked)



# Place everything
lbl_temp.grid(column = 0, row = 0)
txt_temp.grid(column = 0, row = 1)
lbl_chktxt.grid(column = 0, row = 2)
chk_BC.grid(column = 0, row = 3)
btn_verify.grid(column = 0, row = 4)

# Focus keyboard on entry box 
txt_temp.focus

# Run the window
window.mainloop()