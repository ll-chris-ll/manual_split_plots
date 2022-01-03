import configparser
import time
import uuid

from image_controller import ImageController
from gui import MainWindow
from utils import queues, App

config = configparser.ConfigParser()
config.read('config.ini')
App.BUFFER_COUNT = int(config['IMAGES']['buffer'])
App.SESSION_ID = uuid.uuid4()
App.RGB_BAND = list(map(int, config['IMAGES']['rgb'].split(",")))


if __name__ == '__main__':
    image_controller = ImageController()
    image_controller.start()

    mw = MainWindow(queues=queues, image_controller=image_controller)
    mw.mainloop()
