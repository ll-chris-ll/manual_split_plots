import multiprocessing
import os
import queue
import uuid
from enum import Enum
from dataclasses import dataclass
from multiprocessing import Lock, Queue
import json
class Sensor(Enum):
    FX10 = "FX10"
    FX17 = "FX17"




class FileDispenser:

    def __init__(self):
        self.file_list = []
        self._total = 0
        self._current = 0
        self._prev = [None, None]
        # todo: change file_list to one array and use a pointer to select current

    def find_files(self):
        tmp_list = os.listdir(App.WORKING_DIR)
        hdr_list = [s for s in tmp_list if ".hdr" in s]
        for f in sorted(hdr_list, reverse=True):
            if App.SENSOR.value in f:
                self.file_list.append(f)
                self._total +=1

    def next(self):
        """
        Returns the next image, "file path"
        :return: string
        """
        self._current +=1
        current = self.file_list.pop()
        self._set_prev(current)
        return current

    def has_next(self)->bool:
        """
        Returns True if there is at least one image left in the array, else returns False.
        :return: bool
        """
        if len(self.file_list):
            return True
        return False

    def count(self):
        """
        Returns the current images count and the total count.
        :return: tuple (int, int)
        """
        return self._current, self._total

    def undo_one(self):
        """
        Returns the last image path, or None if it was the first
        :return: string
        """
        return self._prev[0]

    def _set_prev(self, current):
        """
        Stores the current image path, so it can be used as the previous one next time.
        :param current:
        """
        self._prev[0] = self._prev[1]
        self._prev[1] = current

queues = {
    "gui==>image_loader": queue.Queue(),
    "image_loader==>gui": queue.Queue(),
    "processed_image": Queue()
}





@dataclass
class App:
    SENSOR : Sensor
    RGB_BAND: list
    WORKING_DIR : str
    FILES: FileDispenser
    BUFFER_COUNT: int
    SESSION_ID: uuid

@dataclass
class ImageHandler:
    fileName: str
    dirPath: str
    is_ready: bool
    image: any
    fullPath: str = None
    header: str = ""
    x_split: int = 0

    def __post_init__(self):
        self.fullPath = os.path.join(self.dirPath, self.fileName)

    def image_ready(self, _image):
        self.image = _image[1]
        self.header = _image[2]
        self.is_ready = True


def output_split_data(imageHandler:ImageHandler):
    output = json.dumps({
        "dir": imageHandler.dirPath,
        "file": imageHandler.fileName,
        "x_split": imageHandler.x_split
    })

    with open(os.path.join(imageHandler.dirPath, f"split_data_{App.SESSION_ID}.txt"), 'a') as f:
        f.write(output+"\n")