""" Functionality to browse through the color maps in a library
"""

import logging
import os.path
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from cmlib.cmap import ColorLib, ColorMap
from cmlib.misc import LOG_FMT, check_class
from cmlib.qtwidgets.qimg import makeColorBarPixMap
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

        self.colorMapNameLabel = QtWidgets.QLabel()
        self.colorMapNameLabel.setAlignment(Qt.AlignCenter)
        self.colorMapNameLabel.setStyleSheet("font-size: x-large; color: redl")
        font = self.colorMapNameLabel.font()
        font.setPointSizeF(font.pointSize() * 1.5)
        self.colorMapNameLabel.setFont(font)

        self.colorMapImageLabel = QtWidgets.QLabel()
        self.colorMapImageLabel.setScaledContents(True)
        self.colorMapImageLabel.setFrameStyle(QtWidgets.QFrame.Panel)
        self.colorMapImageLabel.setLineWidth(1)

        # Layout
        # self.verSplitter = QtWidgets.QSplitter(orientation=Qt.Vertical)
        # self.verSplitter.setChildrenCollapsible(False)
        # self.verSplitter.addWidget(self.tableView)
        # self.verSplitter.addWidget(self.colorMapImageLabel)
        #self.mainLayout.addWidget(self.verSplitter)

        self.mainLayout = QtWidgets.QVBoxLayout()
        mar = 10
        self.mainLayout.setContentsMargins(mar, mar, mar, mar)
        self.mainLayout.addWidget(self.colorMapNameLabel)
        self.mainLayout.addWidget(self.colorMapImageLabel)
        self.mainLayout.addWidget(self.tableView)
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
        pixMap = makeColorBarPixMap(colorMap, width=256, height=25)
        self.colorMapImageLabel.setPixmap(pixMap)

        self.colorMapNameLabel.setText(colorMap.pretty_name)


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
    win.setGeometry(10, 10, 800, 350)
    app.exec_()



if __name__ == "__main__":
    logging.basicConfig(level='DEBUG', format=LOG_FMT)
    main()


