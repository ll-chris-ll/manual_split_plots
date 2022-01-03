import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk, Image

from image_controller import ImageController
from utils import App, FileDispenser, Sensor, ImageHandler, output_split_data


# Mouse wheel handler for Mac, Windows and Linux
# Windows, Mac: Binding to <MouseWheel> is being used
# Linux: Binding to <Button-4> and <Button-5> is being used
# https://stackoverflow.com/a/41505949
def delta_fix(event):
    if event.num == 5 or event.delta < 0:
        return -1
    return 1


import configparser

config = configparser.ConfigParser()
config.read('config.ini')


class MainWindow(tk.Tk):

    def __init__(self, queues, image_controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queues = queues
        self.image_controller = image_controller

        self.title("MSP9000 v0.1.2")
        self.geometry("1820x1080")
        self["bg"] = "white"

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, minsize=40)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, minsize=28)

        """ TOOLBAR """
        self.toolbar = Toolbar(self)

        """ main area """
        self.container = tk.PanedWindow(sashwidth=4, showhandle=False)
        # self.container = tk.Frame(self, background="#44ff11")
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=2)
        self.container.columnconfigure(1, weight=1)

        """ STATUSBAR """
        self.statusbar = Statusbar(self)

        """ CANVAS """
        self.canvas = ScrolledCanvas(self, self.container, self.image_controller, self.statusbar, self.toolbar)

        self.scrolled_text = ScrolledText(self.container)


        """ Layout - TOP level """
        self.container.grid(row=1, column=0, sticky="news")
        self.toolbar.grid(row=0, column=0, sticky="new")
        self.statusbar.grid(row=2, column=0, sticky="wse")

        # self.canvas.grid(row=0, column=0, sticky="nws")
        # t.grid(row=0, column=1, sticky="nes")
        self.container.add(self.canvas)
        self.container.add(self.scrolled_text)

        self.bind("<<background_task_complete_image_loaded>>", self.statusbar.update_background_task_indicator)
        self.image_controller.set_event_callback(self.event_callback)

    def event_callback(self):
        """ Gets triggered by the image_controller thread, when a new image is ready. """
        self.event_generate("<<background_task_complete_image_loaded>>", when="tail")
        self.canvas.next_image_ready()

    def signal_load_next_image(self):
        self.canvas.load_next_image(None)

    def set_scrolled_text(self, title, text):
        self.scrolled_text.config(state=tk.NORMAL)
        self.scrolled_text.delete('1.0', tk.END)
        self.scrolled_text.insert(tk.END, title)
        self.scrolled_text.insert(tk.END, text)
        self.scrolled_text.config(state=tk.DISABLED)


class ScrolledCanvas(tk.Frame):

    def __init__(self, mainWindow, parent, image_controller: ImageController, statusbar, toolbar):
        # super().__init__(parent)
        tk.Frame.__init__(self, parent)
        self.master = parent
        self.mainWindow: mainWindow = mainWindow
        self.statusbar: Statusbar = statusbar
        self.toolbar: Toolbar = toolbar

        """ Image and Handler """
        self.current_image = None
        self.currentImageHandler = None
        self.prevImageHandler = None

        self.image_controller = image_controller
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self["bg"] = "#1e464f"
        self["bd"] = 2
        self.canvas = tk.Canvas(self, width=400, height=400, background='green')
        self.canvas.bind('<Button-1>', self.load_next_image)
        self.canvas.bind('<Motion>', self.vertical_line)

        self.canvas.grid(row=0, column=0, sticky='nw')

        """ Create Vertical Line """
        self.vLine = self.canvas.create_line(0, 0, 0, 0, fill='red', width='5', tags="vline")

        """ Mouse Wheel scrolling based on https://stackoverflow.com/a/37858368 """
        self.bind("<Enter>", self._bound_to_mousewheel)
        self.bind("<Leave>", self._unbound_to_mousewheel)

        self.vbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vbar.config(command=self.canvas.yview)
        self.vbar.grid(row=0, column=1, sticky=tk.NS)

        self.hbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hbar.config(command=self.canvas.xview)
        self.hbar.grid(row=1, column=0, sticky=tk.EW)

        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

    def next_image_ready(self):
        if self.current_image is None:
            self.load_next_image(None)

    def load_next_image(self, event):
        if event:
            if self.currentImageHandler:
                self.currentImageHandler.x_split = event.x
                output_split_data(self.currentImageHandler)

                """ Store for one round in case i ever add undo. """
                self.prevImageHandler = self.currentImageHandler

        self.currentImageHandler: ImageHandler = self.image_controller.get_next_image()
        if self.currentImageHandler:
            self.display_image(self.currentImageHandler.image)
            self.mainWindow.set_scrolled_text(self.currentImageHandler.fileName, self.currentImageHandler.header)
            _count = App.FILES.count()
            self.statusbar.update_status(f"{_count[0]} of {_count[1]} images processed")
        else:
            self.statusbar.update_status("Wait for image to process...")

    def display_image(self, pil_image):
        self.current_image = ImageTk.PhotoImage(pil_image)
        self.canvas.config(width=self.current_image.width(), height=self.current_image.height())
        self.canvas.create_image(0, 0, image=self.current_image, anchor=tk.NW)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.statusbar.update_background_task_indicator(False)
        self.canvas.lift("vline")

    def _bound_to_mousewheel(self, event):
        """ Windows and Mac """
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_horizontal_mousewheel)

        """ Linux """
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        self.canvas.bind("<Shift-Button-4>", self._on_horizontal_mousewheel)
        self.canvas.bind("<Shift-Button-5>", self._on_horizontal_mousewheel)

    def _unbound_to_mousewheel(self, event):
        """ Windows and Mac """
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Shift-MouseWheel>")
        """ Linux """
        self.canvas.unbind("<Button-4>")
        self.canvas.unbind("<Shift-Button-4>")
        self.canvas.unbind("<Button-5>")
        self.canvas.unbind("<Shift-Button-5>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-(delta_fix(event)), "units")

    def _on_horizontal_mousewheel(self, event):
        self.canvas.xview_scroll(-(delta_fix(event)), "units")

    def vertical_line(self, event):
        self.canvas.coords(self.vLine, event.x, 0, event.x, self.canvas.winfo_height())
        self.toolbar.update_coords(event)


class Toolbar(tk.Frame):

    def __init__(self, parent):
        super().__init__()
        self.parent: MainWindow = parent
        self.select_dir = ttk.Button(self, text="load", state=tk.DISABLED, command=self._select_directory)

        """ Dropdown Menu for Sensor """
        sensor_options = ["Sensor"]
        for opt in config["IMAGES"]["sensors"].split(","):
            sensor_options.append(opt.strip())

        sensor_variable = tk.StringVar(self)
        sensor_variable.set(sensor_options[0])
        sensor_select = ttk.OptionMenu(self, sensor_variable, *sensor_options, command=self._on_sensor_select)

        """ Coords Display """
        self.coordsValue = tk.StringVar(value="xy(00-00)")
        self.coordsDisplay = tk.Label(self, textvariable=self.coordsValue)

        """ Layout Items """
        self.select_dir.grid(row=0, column=0, pady=4, padx=4)
        sensor_select.grid(row=0, column=2, pady=4, padx=4)
        self.coordsDisplay.grid(row=0, column=4, padx=10)

    def update_coords(self, event):
        self.coordsValue.set(f"xy({event.x}-{event.y})")

    def _on_sensor_select(self, event):
        self.select_dir.config(state=tk.ACTIVE)
        App.SENSOR = Sensor[event]

    def _select_directory(self):
        App.WORKING_DIR = filedialog.askdirectory()
        App.FILES = FileDispenser()
        App.FILES.find_files()
        self.parent.signal_load_next_image()


class Statusbar(tk.Frame):

    def __init__(self, parent):
        super().__init__()
        # self["bg"] = "#abc2c4"
        self["height"] = 28

        self.lights = []
        self.g = "#32a852"
        self.r = "#ff5c5c"

        self.canvas = tk.Canvas(self, height=28, background="white")
        self.canvas.grid(row=0, column=0)

        """ Create ovals for indicator lights in status bar canvas. """
        d = 22
        _canvas_width = 6
        for i in range(0, App.BUFFER_COUNT):
            i = i * 20
            """Create oval with coordinates x1,y1,x2,y2."""
            item_id = self.canvas.create_oval(i + 6, 6, i + d, d, fill=self.r)
            self.lights.append({
                "item_id": item_id,
                "colour": self.r
            })
            _canvas_width += 20
        self.canvas.config(width=_canvas_width)

        self.sb_text = tk.StringVar(value="Select sensor, then directory.")
        self.text_status = tk.Label(self, textvariable=self.sb_text)
        self.text_status.grid(row=0, column=1, padx=10)

    def update_status(self, message):
        self.sb_text.set(message)

    def update_background_task_indicator(self, event):
        """ If there is an event, then it was called by bind, else called manualy. """
        if event:
            for item in self.lights:
                if item["colour"] is self.r:
                    self.canvas.itemconfig(item["item_id"], fill=self.g)
                    item["colour"] = self.g
                    return
        else:
            for item in self.lights[::-1]:
                if item["colour"] is self.g:
                    self.canvas.itemconfig(item["item_id"], fill=self.r)
                    item["colour"] = self.r
                    return
