import threading
import queue

from mainWindow import MainWindow


class Relay(threading.Thread):

    def __init__(self, qu, image_loader, mainWindow):
        super().__init__()
        self.qu:queue.Queue = qu
        self.mw:MainWindow = mainWindow


    def run(self) -> None:
        while True:
            msg = self.qu.get()
            # print(msg)
            if msg[0] == 'ui':
                self.mw.master.event_generate("<<background_task_complete_image_loaded>>", when="tail")