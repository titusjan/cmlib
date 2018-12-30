""" Functionality to browse through the color maps in a library
"""

import logging
import os.path
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from cmlib.cmap import ColorLib, ColorMap
from cmlib.misc import LOG_FMT, check_class
from cmlib.qtwidgets.qimg import arrayToQImage
from cmlib.qtwidgets.table import ColorLibModel, ColorLibTableViewer


logger = logging.getLogger(__name__)




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
        self.colorMapImageLabel.setFrameStyle(QtWidgets.QFrame.Panel)
        self.colorMapImageLabel.setLineWidth(1)

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
        # Do this by swapping index 0 and 2. If using bgra_arr = rgba_arr[:, [2, 1, 0, 3]], the
        # resulting bgra_arr will be fortran-contiguous, which would have to fixed later on.
        # Swapping dimensions is faster
        bgra_arr = np.copy(rgba_arr)
        bgra_arr[:, 0] = rgba_arr[:, 2]
        bgra_arr[:, 2] = rgba_arr[:, 0]
        del rgba_arr
        imageArr = np.expand_dims(bgra_arr, 0)  # Add a dimension to get a N x 1 x 4 array

        assert imageArr.flags['C_CONTIGUOUS'], "expected c_contigous array"

        image = arrayToQImage(imageArr, share_memory=True)
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
    colorLib.load_catalog(os.path.join(data_dir, 'MatPlotLib'))
    colorLib.load_catalog(os.path.join(data_dir, 'SciColMaps'))

    win = CmLibBrowser(colorLib=colorLib)
    win.show()
    win.raise_()
    app.exec_()



if __name__ == "__main__":
    logging.basicConfig(level='DEBUG', format=LOG_FMT)
    main()


