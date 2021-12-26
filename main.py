import queue
import tkinter

from image_loader import ImageLoader
from mainWindow import MainWindow





if __name__ == '__main__':
    action_queue = queue.Queue()
    image_loader = ImageLoader(action_queue)
    image_loader.start()

    root = tkinter.Tk()
    mw = MainWindow(root, action_queue, image_loader)
    root.mainloop()

    image_loader.join()