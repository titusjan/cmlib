""" Functionality to browse through the color maps in a library
"""
import copy
import logging
import os.path
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from cmlib.cmap import ColorLib, ColorMap
from cmlib.misc import LOG_FMT, check_class
from cmlib.qtwidgets.table import ColorLibModel, ColorLibTableViewer


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
        buf = arr.data
    else:
        cpy = np.copy(arr)
        buf = cpy.data

    logger.debug("Buffer type: {}".format(type(buf)))

    qimg = QtGui.QImage(buf, arr_width, arr_height, format)
    return qimg




class CmLibBrowser(QtWidgets.QWidget):
    """ Widget to browse the though the color library
    """

    def __init__(self, colorLib, parent=None):
        super().__init__(parent=parent)

        check_class(colorLib, ColorLib)
        self._colorLib = colorLib
        self._colorLibModel = ColorLibModel(colorLib, parent=self)

        self.tableView = ColorLibTableViewer(model=self._colorLibModel)
        self.tableView.sigColorMapSelected.connect(self._onColorMapSelected)

        self.colorMapImageLabel = QtWidgets.QLabel()
        #self.colorMapImageLabel.setFrameStyle(QtWidgets.QFrame.Panel)
        #self.colorMapImageLabel.setLineWidth(1)

        # Layout
        self.verSplitter = QtWidgets.QSplitter(orientation=Qt.Vertical)
        self.verSplitter.setChildrenCollapsible(False)
        self.verSplitter.addWidget(self.tableView)
        self.verSplitter.addWidget(self.colorMapImageLabel)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(self.verSplitter)
        self.setLayout(self.mainLayout)


    @property
    def colorLib(self):
        """ Returns the underlying ColorLib
        """
        return self._colorLib


    def _onColorMapSelected(self, colorMap):
        """ Updates the color map image label with the selected color map
        """
        logger.debug("Selected ColorMap: {}".format(colorMap))
        rgba_arr = colorMap.argb_uint8_array

        # Shuffle dimensions to BGRA from RGBA  (which what Qt uses for ARGB in little-endian mode)
        #bgra_arr = rgba_arr[:, [2, 1, 0, 3]]

        imageArr = np.expand_dims(rgba_arr, 0)  # Add a dimension to get a N x 1 x 4 array

        #logger.debug("rgba_arr: {}".format(rgba_arr[25]))
        print(rgba_arr)
        # logger.debug("bgra_arr: {}".format(bgra_arr[25]))
        # logger.debug("bgra_arr: {}".format(type(bgra_arr)))
        logger.debug("imageArr: {}".format(type(imageArr)))

        image = arrayToQImage(imageArr, share_memory=False)
        labelSize = self.colorMapImageLabel.size()
        image = image.scaled(labelSize.width()-2, labelSize.height()-2)
        pixMap = QtGui.QPixmap.fromImage(image)
        self.colorMapImageLabel.setPixmap(pixMap)





    def sizeHint(self):
        """ Holds the recommended size for the widget.
        """
        return QtCore.QSize(800, 600)



def main():
    app = QtWidgets.QApplication([])

    data_dir=os.path.abspath("../../data")

    colorLib = ColorLib()
    colorLib.load_catalog(os.path.join(data_dir, 'CET'))
    #colorLib.load_catalog(os.path.join(data_dir, 'MatPlotLib'))
    #colorLib.load_catalog(os.path.join(data_dir, 'SciColMaps'))

    win = CmLibBrowser(colorLib=colorLib)
    win.show()
    win.raise_()
    app.exec_()



if __name__ == "__main__":
    logging.basicConfig(level='DEBUG', format=LOG_FMT)
    main()


