""" Funcions to create or manipulate QImages
"""

import logging
import numpy as np

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)


# Define constants for the depth dimension when an image is converted to a Width x Height x Depth array
# Qt uses ARGB (or BGRA in little endian) when the format is RGB32, ARGB32 or ARGB32_Premultiplied

def arrayToQImage(arr, share_memory=True, format = None):
    """ Creates QBugImage from a numpy array.

        If share_memory is True, the numpy array and the QImage is shared.
        Be careful: make sure the image is destroyed before the numpy array ,
        otherwise the image will point to unallocated memory!!

        If format is not set it will default to QtGui.QImage.Format.Format_RGB32

        :rtype: QtGui.QImage
    """
    assert type(arr) == np.ndarray, "arr must be a numpy array"
    if format == None:
        #format = QtGui.QImage.Format.Format_RGB32
        format = QtGui.QImage.Format_ARGB32

    assert arr.dtype == np.uint8, "Array must be of type np.uint8"
    assert arr.ndim == 3, "Array must be width x height x 4 array"

    # Note the different width/height parameter order!
    arr_height, arr_width, arr_depth = arr.shape
    assert arr_depth == 4, "Array depth must be 4. Got: {}".format(arr_depth)

    if share_memory:
        arr = np.copy(arr)

    if not arr.flags['C_CONTIGUOUS']:
        logger.warning("Converting array from Fortan contiguous to C contiguous")
        arr = np.ascontiguousarray(arr)

    assert arr.flags['C_CONTIGUOUS'], "expected C-contiguous array"

    buf = arr.data
    qimg = QtGui.QImage(buf, arr_width, arr_height, format)
    return qimg



def makeColorBarPixmap(colorMap, width=None, height=None, drawBorder=False):
    """ Creates a PixMap that visualizes the color map.
        This can be used in a QLabel to draw a legend.

        The resulting pixmap will be 1xN ARGB
    """
    rgba_arr = colorMap.argb_uint8_array

    # Shuffle dimensions to BGRA from RGBA  (which is what Qt uses for ARGB in little-endian mode)
    # Do this by swapping index 0 and 2. If using bgra_arr = rgba_arr[:, [2, 1, 0, 3]], the
    # resulting bgra_arr will be fortran-contiguous, which would have to be fixed later on.
    # Swapping dimensions is faster
    bgra_arr = np.copy(rgba_arr)
    bgra_arr[:, 0] = rgba_arr[:, 2]
    bgra_arr[:, 2] = rgba_arr[:, 0]
    del rgba_arr
    imageArr = np.expand_dims(bgra_arr, 0)  # Add a dimension to get a N x 1 x 4 array

    assert imageArr.flags['C_CONTIGUOUS'], "expected C-contiguous array"

    image = arrayToQImage(imageArr, share_memory=True)

    if width is not None or height is not None:
        if width is None:
            width = image.width()
        if height is None:
            height = image.height()

        image = image.scaled(width, height)

    pixmap = QtGui.QPixmap.fromImage(image)

    if drawBorder:
        painter = QtGui.QPainter(pixmap)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QtCore.QRect(0, 0, width-1, height-1))
        painter.end()

    return pixmap
