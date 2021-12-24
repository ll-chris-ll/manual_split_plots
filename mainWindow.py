import tkinter as tk
from tkinter import ttk, filedialog
from utils import Sensor, App, FileDispenser







class MainWindow(tk.Frame):

    def __init__(self, master):
        # super().__init__()
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title("Manual Split Plots")
        self.master.geometry("400x200")
        self.pack(fill=tk.BOTH, expand=1)

        """ Select Sensor """
        self.buttons_frame = ttk.Frame(self, borderwidth=1, relief="raised")
        self.label = ttk.Label(self.buttons_frame, text="Select Sensor")
        self.label.grid(row=0, column=0)

        self.greet_button = ttk.Button(self.buttons_frame, text="FX10", command=lambda : self.select_sensor(Sensor.FX10))
        self.greet_button.grid(row=1, column=0)

        self.close_button = ttk.Button(self.buttons_frame, text="FX17", command=lambda : self.select_sensor(Sensor.FX17))
        self.close_button.grid(row=1, column=1)

        self.select_directory_button = ttk.Button(self.buttons_frame, text="Select Directory", command=lambda : self.select_directory())

        self.buttons_frame.grid(row=0, column=0, ipadx=10, ipady=10, padx=10, pady=10)

        """ Status Bar """
        self.status_bar = ttk.Frame(self.master, borderwidth=2, relief="groove")
        self.sb_text_left = tk.StringVar(value="left")
        self.sb_text_centre = tk.StringVar(value="centre")
        self.sb_text_right = tk.StringVar(value="right")
        sb_label_left = tk.Label(self.status_bar, textvariable=self.sb_text_left)
        sb_label_centre = tk.Label(self.status_bar, textvariable=self.sb_text_centre)
        sb_label_right = tk.Label(self.status_bar, textvariable=self.sb_text_right, anchor="e")
        sb_label_left.grid(row=0, column=0)
        sb_label_centre.grid(row=0, column=1)
        sb_label_right.grid(row=0, column=2, sticky='e')



        self.status_bar.pack(expand=1, anchor="sw", fill="x")

    def select_sensor(self, sensor):
        self.sb_text_right.set(sensor.value)
        App.SENSOR = sensor

        # Show button to select dir
        self.select_directory_button.grid(row=2, column=0, columnspan=2)

    def select_directory(self):
        dir_selected = filedialog.askdirectory()
        App.WORKING_DIR = dir_selected
        self.buttons_frame.grid_forget()

        # todo: temp stuff
        # fd = FileDispenser()
        # fd.find_files()
        App.FILES = FileDispenser()
        App.FILES.find_files()

        while App.FILES.has_next():
            print(App.FILES.next())