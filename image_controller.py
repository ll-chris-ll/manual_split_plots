import queue
import threading
from multiprocessing import Process
from image_processor import image_processor
from utils import App, queues, ImageHandler




class ImageController(threading.Thread):

    def __init__(self):
        super().__init__()
        self.buffered_images = []
        self.background_task_complete_callback = None

    def run(self) -> None:
        while True:
            try:
                imgObj = queues["processed_image"].get()
                item: ImageHandler
                for item in self.buffered_images:
                    if item.fullPath == imgObj[0]:
                        item.image_ready(imgObj)
                        self.background_task_complete_callback()
            except queue.Empty:
                pass

    def set_event_callback(self, event_callback):
        self.background_task_complete_callback = event_callback

    def buffer_images(self):
        while len(self.buffered_images) < App.BUFFER_COUNT and App.FILES.has_next():
            image_h = ImageHandler(
                fileName=App.FILES.next(),
                dirPath=App.WORKING_DIR,
                is_ready=False,
                image=None
            )
            proc = Process(target=image_processor, args=(image_h.fullPath, queues["processed_image"], App.RGB_BAND))
            proc.daemon = True
            proc.start()
            self.buffered_images.append(image_h)

    def get_next_image(self):
        self.buffer_images()

        if len(self.buffered_images):
            img_h: ImageHandler = self.buffered_images[0]
            if img_h.is_ready is True:
                item = self.buffered_images.pop(0)
                self.buffer_images()
                return item
        return None
