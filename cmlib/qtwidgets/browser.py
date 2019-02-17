""" Functionality to browse through the color maps in a library
"""

import logging

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

from ..cmap import DataCategory
from ..misc import check_class
from ..qtwidgets.qimg import makeColorBarPixmap
from ..qtwidgets.table import ColorLibModel, ColorLibProxyModel, ColorLibTableViewer


logger = logging.getLogger(__name__)

def _isChecked(checkState):
    """ Returns if checkState == Qt.﻿Checked """
    return checkState == Qt.Checked

def uniqueSort(lst):
    """ Returns the sorted list of unique list entries"""
    return sorted(list(set(lst)))


class FilterForm(QtWidgets.QWidget):
    """ Form with widgets to filter the color bars
    """
    def __init__(self, proxyModel: ColorLibProxyModel, parent=None):
        super().__init__(parent=parent)

        self._defaultOnCheckboxes = []
        self._defaultOffCheckboxes = []

        self._proxyModel = proxyModel
        self._sourceModel = self._proxyModel.sourceModel()
        self._colorLib = self._sourceModel.colorLib
        colMaps = self._colorLib.color_maps

        self.resetButton = QtWidgets.QPushButton("Reset Filters")
        self.resetButton.clicked.connect(self.resetCheckboxes)

        self.catalogsGroupBox = QtWidgets.QGroupBox("Show catalogs")
        self.catalogsLayout = QtWidgets.QVBoxLayout(self.catalogsGroupBox)
        allCatalogs = uniqueSort([(cm.catalog_meta_data.key, cm.catalog_meta_data.name)
                                   for cm in colMaps])

        for catalogKey, catalogName in allCatalogs:
            checkBox = self._createFilterCheckbox(
                ColorLibProxyModel.FT_CATALOG, None, catalogKey)
            checkBox.setText(catalogKey)
            checkBox.setToolTip(catalogName)
            self._defaultOnCheckboxes.append(checkBox)
            self.catalogsLayout.addWidget(checkBox)

        self.categoriesGroupBox = QtWidgets.QGroupBox("Show categories")
        self.categoriesLayout = QtWidgets.QVBoxLayout(self.categoriesGroupBox)

        for category in list(DataCategory):
            checkBox = self._createFilterCheckbox(
                ColorLibProxyModel.FT_CATEGORY, 'category', category)
            checkBox.setText(category.name)
            self._defaultOnCheckboxes.append(checkBox)
            self.categoriesLayout.addWidget(checkBox)

        self.qualityGroupBox = QtWidgets.QGroupBox("Quality filter")
        self.qualityLayout = QtWidgets.QVBoxLayout(self.qualityGroupBox)

        infoList = [
            ("Favorite (★)", "favorite"),
            ("Recommended", "recommended"),
            ("Perceptually Uniform", "perceptually_uniform"),
            ("Black && White Friendly", "black_white_friendly"),
            ("Color Blind Friendly", "color_blind_friendly"),
            ("Isoluminant", "isoluminant"),
        ]
        for text, attrName in infoList:
            checkBox = self._createFilterCheckbox(ColorLibProxyModel.FT_QUALITY, attrName, True)
            checkBox.setText(text)
            if attrName == "recommended":
                self._defaultOnCheckboxes.append(checkBox)
            else:
                self._defaultOffCheckboxes.append(checkBox)
            self.qualityLayout.addWidget(checkBox)

        self.tagsGroupBox = QtWidgets.QGroupBox("Tag filter")
        self.tagsLayout = QtWidgets.QVBoxLayout(self.tagsGroupBox)

        tagSet = set([])
        for cm in colMaps:
            for tag in cm.meta_data.tags:
                tagSet.add(tag)
        allTags = sorted(list(tagSet))

        for tag in allTags:
            checkBox = self._createFilterCheckbox(ColorLibProxyModel.FT_TAG, None, tag)
            checkBox.setText(tag)
            self._defaultOffCheckboxes.append(checkBox)
            self.tagsLayout.addWidget(checkBox)

        self.mainLayout = QtWidgets.QVBoxLayout()
        #self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.catalogsGroupBox)
        self.mainLayout.addWidget(self.categoriesGroupBox)
        self.mainLayout.addWidget(self.qualityGroupBox)
        self.mainLayout.addWidget(self.tagsGroupBox)
        self.mainLayout.addWidget(self.resetButton)
        self.mainLayout.addStretch()

        self.resetCheckboxes()


    def _createFilterCheckbox(self, filterType, attrName, desiredValue):
        """ Creates checkbox that filters on attrName with the and-operator.
        """
        checkBox = QtWidgets.QCheckBox()
        checkBox.toggled.connect(lambda checked:
            self._proxyModel.toggleFilter(filterType, attrName, desiredValue, checked))
        return checkBox


    def resetCheckboxes(self):
        """ Resets all checkboxes to their initial values
        """
        for checkbox in self._defaultOnCheckboxes:
            checkbox.setChecked(True)

        for checkbox in self._defaultOffCheckboxes:
            checkbox.setChecked(False)



class CmLibBrowserDialog(QtWidgets.QDialog):
    """ Widget to browse the though the color library
    """
    def __init__(self, colorLibModel: ColorLibModel, parent=None):
        super().__init__(parent=parent)

        check_class(colorLibModel, ColorLibModel)
        self._colorLibModel = colorLibModel

        self.tableView = ColorLibTableViewer(model=self._colorLibModel)
        self.tableView.sigColorMapHighlighted.connect(self._onColorMapSelected)
        self.tableView.verticalHeader().hide()

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

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.rightLayout.addWidget(self.buttonBox)

        self.okButton = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.cancelButton = self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)

        self.tableView.doubleClicked.connect(self.accept)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        #self.discardButton.clicked.connect(self.reject)


    @property
    def colorLib(self):
        """ Returns the underlying ColorLib
        """
        return self._colorLibModel.colorLib


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

