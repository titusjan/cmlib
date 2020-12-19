# -*- coding: utf-8 -*-

""" Functionality to browse through the color maps in a library
"""

import logging

from ..cmap import DataCategory # TODO: why attempted relative import beyond top-level package
from ..misc import check_class
from .bindings import QtCore, QtWidgets, Qt, QtSignal
from .qimg import makeColorBarPixmap
from .table import CmLibModel, CmLibProxyModel, CmLibTableViewer, ALL_ITEMS_STR


logger = logging.getLogger(__name__)

def _isChecked(checkState):
    """ Returns if checkState == Qt.Checked """
    return checkState == Qt.Checked

def uniqueSort(lst):
    """ Returns the sorted list of unique list entries"""
    return sorted(list(set(lst)))


class FilterForm(QtWidgets.QWidget):
    """ Form with widgets to filter the color bars
    """
    sigFilterChanged = QtSignal() # A filter has changed

    def __init__(self, proxyModel, parent=None):
        super(FilterForm, self).__init__(parent=parent)

        self._defaultOnCheckboxes = []
        self._defaultOffCheckboxes = []

        self._proxyModel = proxyModel
        self._sourceModel = self._proxyModel.sourceModel()
        self._cmLib = self._sourceModel.cmLib
        colMaps = self._cmLib.color_maps

        self.resetButton = QtWidgets.QPushButton("Reset Filters")
        self.resetButton.clicked.connect(self.resetFilters)

        self.catalogsGroupBox = QtWidgets.QGroupBox("Catalog")
        self.catalogsLayout = QtWidgets.QVBoxLayout(self.catalogsGroupBox)
        allCatalogs = uniqueSort([cm.catalog_meta_data.name for cm in colMaps])
        self.catalogComboBox = self._createFilterCombobox(
            CmLibProxyModel.FT_CATALOG, allCatalogs)
        self.catalogsLayout.addWidget(self.catalogComboBox)

        self.categoriesGroupBox = QtWidgets.QGroupBox("Category")
        self.categoriesLayout = QtWidgets.QVBoxLayout(self.categoriesGroupBox)
        allCategories = uniqueSort([dc.name for dc in list(DataCategory)])
        self.categoryComboBox = self._createFilterCombobox(
            CmLibProxyModel.FT_CATEGORY, allCategories)
        self.categoriesLayout.addWidget(self.categoryComboBox)

        self.qualityGroupBox = QtWidgets.QGroupBox("Quality filters")
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
            checkBox = self._createFilterCheckbox(CmLibProxyModel.FT_QUALITY, attrName, True)
            checkBox.setText(text)
            if attrName == "recommended":
                self._defaultOnCheckboxes.append(checkBox)
            else:
                self._defaultOffCheckboxes.append(checkBox)
            self.qualityLayout.addWidget(checkBox)

        self.tagsGroupBox = QtWidgets.QGroupBox("Tag filters")
        self.tagsLayout = QtWidgets.QVBoxLayout(self.tagsGroupBox)

        tagSet = set([])
        for cm in colMaps:
            for tag in cm.meta_data.tags:
                tagSet.add(tag)
        allTags = sorted(list(tagSet))

        for tag in allTags:
            checkBox = self._createFilterCheckbox(CmLibProxyModel.FT_TAG, None, tag)
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

        self.resetFilters()


    def _createFilterCombobox(self, filterType, allNames):
        """ Creates checkbox that filters on attrName with the and-operator.
        """
        combobox = QtWidgets.QComboBox()
        combobox.addItem(ALL_ITEMS_STR)
        combobox.addItems(allNames)

        filterType2 = filterType # keep reference in closure

        combobox.currentTextChanged.connect(lambda text:
            self._onFilterIndexSelected(filterType2, text))

        return combobox


    def _onFilterIndexSelected(self, filterType, text):
        """ Called when the user checks a filter on or off
        """
        self._proxyModel.setExclusiveFilter(filterType, text)
        self.sigFilterChanged.emit()


    def _createFilterCheckbox(self, filterType, attrName, desiredValue):
        """ Creates checkbox that filters on attrName with the and-operator.
        """
        checkBox = QtWidgets.QCheckBox()
        filterType2, attrName2, desiredValue2 = filterType, attrName, desiredValue
        checkBox.toggled.connect(lambda checked:
            self._onFilterChecked(filterType2, attrName2, desiredValue2, checked))
        return checkBox


    def _onFilterChecked(self, filterType, attrName, desiredValue, checked):
        """ Called when the user checks a filter on or off
        """
        self._proxyModel.toggleFilter(filterType, attrName, desiredValue, checked)
        self.sigFilterChanged.emit()
        

    def resetFilters(self):
        """ Resets all checkboxes to their initial values
        """
        self.catalogComboBox.setCurrentText(ALL_ITEMS_STR)
        self.categoryComboBox.setCurrentText(ALL_ITEMS_STR)

        for checkbox in self._defaultOnCheckboxes:
            checkbox.setChecked(True)

        for checkbox in self._defaultOffCheckboxes:
            checkbox.setChecked(False)



class CmLibBrowserDialog(QtWidgets.QDialog):
    """ Widget to browse the though the color library
    """
    def __init__(self, cmLibModel, parent=None):
        super(CmLibBrowserDialog, self).__init__(parent=parent)

        check_class(cmLibModel, CmLibModel)
        self._cmLibModel = cmLibModel

        self.tableView = CmLibTableViewer(model=self._cmLibModel)
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
        self.mainLayout.setSpacing(0)
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
        
        self.filterForm.sigFilterChanged.connect(self.tableView.scrollToCurrent)




    @property
    def cmLib(self):
        """ Returns the underlying CmLib
        """
        return self._cmLibModel.cmLib


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


    def setColorMapByKey(self, key):
        """ Selects the color map in the table and accepts the color map (i.e. 'presses Ok')
        """
        logger.debug("Setting color map by key: {}".format(key))
        row = self.tableView.selectRowByKey(key)
        self.accept()
        return row

