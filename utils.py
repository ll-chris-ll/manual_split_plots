import os
from enum import Enum
from dataclasses import dataclass


class Sensor(Enum):
    FX10 = "FX10"
    FX17 = "FX17"



class FileDispenser:

    def __init__(self):
        self.file_list = []

    def find_files(self):
        tmp_list = os.listdir(App.WORKING_DIR)
        for f in tmp_list:
            if App.SENSOR.value in f:
                self.file_list.append(f)

    def next(self):
        return self.file_list.pop()

    def has_next(self)->bool:
        if len(self.file_list):
            return True
        return False

@dataclass
class App:
    SENSOR : Sensor
    WORKING_DIR : str
    FILES: FileDispenser
