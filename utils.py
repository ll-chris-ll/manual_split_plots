import os
from enum import Enum
from dataclasses import dataclass
class Sensor(Enum):
    FX10 = "FX10"
    FX17 = "FX17"

@dataclass
class App:
    SENSOR : Sensor
    WORKING_DIR : str



class FileDispenser:

    def __init__(self):
        self.file_list = []

    def find_files(self):
        tmp_list = os.listdir(App.WORKING_DIR)
        for f in tmp_list:
            if App.SENSOR.value in f:
                self.file_list.append(f)
        print(f"----->file_list:{self.file_list}")