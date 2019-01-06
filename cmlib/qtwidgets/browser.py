""" Functionality to browse through the color maps in a library
"""

import logging
import os.path
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from cmlib.cmap import ColorLib, ColorMap
from cmlib.misc import LOG_FMT, check_class
from cmlib.qtwidgets.qimg import makeColorBarPixmap
from cmlib.qtwidgets.table import ColorLibModel, ColorLibProxyModel, ColorLibTableViewer


logger = logging.getLogger(__name__)

def _isChecked(checkState):
    """ Returns if checkState == Qt.﻿Checked """
    return checkState == Qt.Checked


class FilterForm(QtWidgets.QWidget):
    """ Form with widgets to filter the color bars
    """
    def __init__(self, proxyModel: ColorLibProxyModel, parent=None):
        super().__init__(parent=parent)

        self._proxyModel = proxyModel
        self._sourceModel = self._proxyModel.sourceModel()
        self._colorLib = self._sourceModel.colorLib

        # Show only
        self.showOnlyGroupBox = QtWidgets.QGroupBox("Show Only")
        self.showOnlyLayout = QtWidgets.QVBoxLayout(self.showOnlyGroupBox)

        infoList = [
            ("Favorites", "favorite"),
            ("Recommended", "recommended"),
            ("Perceptually Uniform", "perceptually_uniform"),
            ("Black & white friendly", "black_white_friendly"),
            ("Color blind friendly", "color_blind_friendly"),
            ("Isoluminant", "isoluminant"),
        ]
        for text, attrName in infoList:
            self.showOnlyLayout.addWidget(self._createAndFilterCheckbox(text, attrName))

        self.mainLayout = QtWidgets.QVBoxLayout()
        #self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.showOnlyGroupBox)
        self.mainLayout.addStretch()

    def _createAndFilterCheckbox(self, text, attrName):
        """ Creates checkbox that filters on attrName"""
        checkBox = QtWidgets.QCheckBox(text)
        checkBox.stateChanged.connect(
            lambda state: self._proxyModel.toggleAndFilter(attrName, _isChecked(state)))
        return checkBox


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
        #self.tableView.verticalHeader().show()

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

        self.filterForm = FilterForm(self.tableView._proxyModel)


        # Layout
        # self.verSplitter = QtWidgets.QSplitter(orientation=Qt.Vertical)
        # self.verSplitter.setChildrenCollapsible(False)
        # self.verSplitter.addWidget(self.tableView)
        # self.verSplitter.addWidget(self.colorMapImageLabel)
        #self.mainLayout.addWidget(self.verSplitter)

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.filterForm)

        self.rightLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addLayout(self.rightLayout)
        mar = 10
        self.rightLayout.setContentsMargins(mar, mar, mar, mar)
        self.rightLayout.addWidget(self.colorMapNameLabel)
        self.rightLayout.addWidget(self.colorMapImageLabel)
        self.rightLayout.addWidget(self.tableView)


    @property
    def colorLib(self):
        """ Returns the underlying ColorLib
        """
        return self._colorLib


    def _onColorMapSelected(self, colorMap):
        """ Updates the color map image label with the selected color map
        """
        logger.debug("Selected ColorMap: {}".format(colorMap))
        pixMap = makeColorBarPixmap(colorMap, width=256, height=25)
        self.colorMapImageLabel.setPixmap(pixMap)

        self.colorMapNameLabel.setText(colorMap.pretty_name)


    def sizeHint(self):
        """ Holds the recommended size for the widget.
        """
        return QtCore.QSize(1000, 600)



def main():
    app = QtWidgets.QApplication([])

    data_dir=os.path.abspath("../../data")

    colorLib = ColorLib()
    colorLib.load_catalog(os.path.join(data_dir, 'CET'))
    colorLib.load_catalog(os.path.join(data_dir, 'MatPlotLib'))
    colorLib.load_catalog(os.path.join(data_dir, 'SciColMaps'))

    # Set some favorites to test
    for colorMap in colorLib.color_maps:
        if colorMap.key in ['SciColMaps/Oleron', 'CET/CET-CBL1', 'MatPlotLib/Cubehelix']:
            colorMap.meta_data.favorite = True

    win = CmLibBrowser(colorLib=colorLib)
    win.show()
    win.raise_()
    win.setGeometry(10, 10, 1200, 500)
    win.move(10, 10)
    app.exec_()

    logger.debug("Favorites:")
    for colorMap in colorLib.color_maps:
        if colorMap.meta_data.favorite:
            logger.debug("  {}".format(colorMap.meta_data.name))


if __name__ == "__main__":
    logging.basicConfig(level='DEBUG', format=LOG_FMT)
    main()


