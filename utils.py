import os
from enum import Enum
from dataclasses import dataclass


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
        for f in hdr_list:
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

@dataclass
class App:
    SENSOR : Sensor
    WORKING_DIR : str
    FILES: FileDispenser
