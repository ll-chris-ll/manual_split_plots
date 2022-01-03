import random
import spectral.io.envi as envi
from spectral import settings
settings.envi_support_nonlowercase_params = True
from multiprocessing import Queue as mQueue
import numpy as np
from PIL import  Image, ImageTk


def image_processor(image_path, image_queue:mQueue, rgb_band=None) -> None:

    raw = envi.open(image_path)

    """ If rgb bands are not supplied randomise the bands to make each image look different. 
        This has no practical use other than testing. """
    if not rgb_band:
        rgb_band = [random.randrange(20,200),random.randrange(20,200),random.randrange(20,200)]

    rgb_img = raw.read_bands(rgb_band)

    _image = (rgb_img / 4096)

    width = _image.shape[1]
    height = _image.shape[0]
    img_min = np.min(_image)
    img_max = np.max(_image)
    """ Pixel values at this point are between 0.0 and 0.1 this will stretch them to values between 0.0 and 1.0 """
    stretched_pixels = [((i - img_min) * 2 / (img_max - img_min * 2)) for i in _image.flatten()]
    thumbnail = np.reshape(stretched_pixels, (height, width, 3))
    reshaped_image = (thumbnail * 255).astype(np.uint8)

    p_img = Image.fromarray(reshaped_image)
    p_img = p_img.resize((width, 1000))

    image_header_file:str
    with open(image_path, 'r') as f:
        image_header_file = f.read()
    image_queue.put([image_path, p_img, image_header_file])

