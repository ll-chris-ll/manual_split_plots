import queue
import tkinter

from image_loader import ImageLoader
from mainWindow import MainWindow
from relay import Relay

if __name__ == '__main__':
    action_queue = queue.Queue()
    r_qu = queue.Queue()

    image_loader = ImageLoader(action_queue, r_qu)
    image_loader.start()

    root = tkinter.Tk()
    mw = MainWindow(root, action_queue, image_loader)

    relay = Relay(r_qu, image_loader, mw)
    relay.start()

    root.mainloop()

    relay.join()
    image_loader.join()