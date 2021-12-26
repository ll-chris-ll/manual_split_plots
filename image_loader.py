import configparser
import os.path
import random
import threading
import queue
from utils import App
import spectral.io.envi as envi
from spectral import settings
settings.envi_support_nonlowercase_params = True
import numpy as np
from PIL import  Image, ImageTk

class ImageLoader(threading.Thread):

    def __init__(self, action_queue):
        super().__init__()
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.buffer_count = int(config['IMAGES']['buffer'])

        self.action_queue:queue.Queue = action_queue

        self.image_threads = []

    def run(self) -> None:
        while True:
            action = self.action_queue.get()
            print(action)
            if action == "load_images": self._load()

    def _load(self):
        print(App.FILES.next())
        while len(self.image_threads) < self.buffer_count and App.FILES.has_next():
            t_image = ThreadedImage(os.path.join(App.WORKING_DIR, App.FILES.next()))
            t_image.start()
            self.image_threads.append(t_image)

    def get_image(self):
        if len(self.image_threads):
            t_:ThreadedImage = self.image_threads.pop()
            self.action_queue.put("load_images")
            return t_.image
        return None

class ThreadedImage(threading.Thread):

    def __init__(self, image_path):
        super().__init__()
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.buffer_count = config['IMAGES']['buffer']
        self.rgb_band = list(map(int, config['IMAGES']['rgb'].split(",")))
        self.image_path = image_path
        self.image = None

    def run(self) -> None:
        print(f"loading image:{self.image_path}")
        raw = envi.open(self.image_path)
        self.rgb_band = [random.randrange(20,200),random.randrange(20,200),random.randrange(20,200)]
        rgb_img = raw.read_bands(self.rgb_band)

        _image = (rgb_img / 4096)

        width = _image.shape[1]
        height = _image.shape[0]
        img_min = np.min(_image)
        img_max = np.max(_image)
        stretched_pixels = [((i - img_min) * 2 / (img_max - img_min * 2)) for i in _image.flatten()]
        thumbnail = np.reshape(stretched_pixels, (height, width, 3))
        reshaped_image = (thumbnail * 255).astype(np.uint8)

        p_img = Image.fromarray(reshaped_image)
        p_img = p_img.resize((width, 1000))
        self.image = ImageTk.PhotoImage(p_img)


    def get_image(self):
        return self.image