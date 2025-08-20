import numpy as np
from PIL.Image import Image
from pyzbar.pyzbar import decode


def scan_barcode(img: np.ndarray | Image) -> list:
    return decode(img)
