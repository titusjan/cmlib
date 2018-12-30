""" Funcions to create or manipulate QImages
"""

import logging
import numpy as np

from PyQt5 import QtGui

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

    assert arr.flags['C_CONTIGUOUS'], "expected c_contigous array"

    buf = arr.data
    qimg = QtGui.QImage(buf, arr_width, arr_height, format)
    return qimg



