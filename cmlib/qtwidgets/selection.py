""" Widgets to select colors
"""
import logging

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from ..cmap import ColorMap
from ..misc import check_class
from ..qtwidgets.browser import CmLibBrowserDialog
from ..qtwidgets.table import ColorLibModel

logger = logging.getLogger(__name__)



class ComboProxyModel(QtCore.QSortFilterProxyModel):
    """ Proxy model used for sorting and filtering the combobox.

        Sorts by name and filter only favorites.
    """

    def __init__(self, parent):
        super(ComboProxyModel, self).__init__(parent)

        # The color map selected from the browser dialog box
        self.colorMapFromDialog = None


    def lessThan(self, leftIndex, rightIndex):
        """ Returns true if the value of the item referred to by the given index left is less than
            the value of the item referred to by the given index right, otherwise returns false.

            Sorts first by the desired column and uses the Key as tie breaker
        """
        sourceModel = self.sourceModel()
        leftData  = sourceModel.data(leftIndex, role=ColorLibModel.SORT_ROLE)
        rightData = sourceModel.data(rightIndex, role=ColorLibModel.SORT_ROLE)

        leftKeyIndex = sourceModel.index(leftIndex.row(), ColorLibModel.COL_KEY)
        rightKeyIndex = sourceModel.index(rightIndex.row(), ColorLibModel.COL_KEY)

        leftKey  = sourceModel.data(leftKeyIndex, role=ColorLibModel.SORT_ROLE)
        rightKey = sourceModel.data(rightKeyIndex, role=ColorLibModel.SORT_ROLE)

        return (leftData, leftKey) < (rightData, rightKey)


    def filterAcceptsRow(self, sourceRow, sourceParentIndex):
        """ Returns true if the item is a favorite
        """
        colMap = self.sourceModel().colorLib.color_maps[sourceRow]
        accept = colMap.meta_data.favorite or colMap == self.colorMapFromDialog
        #logger.debug("filterAcceptsRow = {}: {:15s}".format(accept, colMap.meta_data.pretty_name))
        return accept


    def getColorMapByRow(self, row):
        """ Returns a color map at row of the given index.
            Returns None if no colormap is found
        """
        proxyIdx = self.index(row, 0)
        sourceIdx = self.mapToSource(proxyIdx)
        colorMap = self.sourceModel().getColorMapByIndex(sourceIdx)
        return colorMap



class ColorSelectionWidget(QtWidgets.QWidget):
    """ Widget to select a color map.

        Consists of Combobox and a button that pop ups a selection dialog.

        The sigColorMapChanged signal is emitted when the user selects a color map in the combobox,
        clicks Ok in the browser dialog, or double clicks a row in the browser dialog.

        The sigColorMapHighlighted is emitted when the user selects a row in the browser dialog.
        It is also emitted when the user clicks Cancel with the color map that was active when the
        dialog is shown.
    """
    sigColorMapHighlighted = pyqtSignal(ColorMap)
    sigColorMapChanged = pyqtSignal(ColorMap)

    def __init__(self, colorLibModel: ColorLibModel, **kwargs):
        """ Constructor
        """
        super().__init__(**kwargs)

        check_class(colorLibModel, ColorLibModel)
        self._sourceModel = colorLibModel
        self._proxyModel = ComboProxyModel(parent=self)
        self._proxyModel.setSourceModel(self._sourceModel)

        self._colorMapAtShow = None # The current color map at the moment the browser is shown

        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.setModel(self._proxyModel)
        self.comboBox.setModelColumn(ColorLibModel.COL_NAME)

        scale = 0.65
        self.comboBox.setIconSize(
            QtCore.QSize(colorLibModel.iconBarWidth * scale, colorLibModel.iconBarHeight * scale))

        self.browser = CmLibBrowserDialog(colorLibModel=colorLibModel)

        self.openDialogButton = QtWidgets.QToolButton()
        self.openDialogButton.setText("...")
        self.openDialogButton.setToolTip("Open color map browser dialog.")
        self.openDialogButton.clicked.connect(self.showDialog)

        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.addWidget(self.comboBox)
        self.mainLayout.addWidget(self.openDialogButton)

        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.comboBox.currentIndexChanged.connect(self._onCurrentChanged)
        self.browser.tableView.sigColorMapHighlighted.connect(self.sigColorMapHighlighted)
        self.browser.accepted.connect(self._onDialogAccepted)
        self.browser.rejected.connect(self._onDialogRejected)


    def showDialog(self):
        """ Shows the color browser dialog
        """
        self.browser.show()
        self._colorMapAtShow = self.getCurrentColorMap()
        curRow = self.comboBox.currentIndex()
        proxyIdx = self._proxyModel.index(curRow, self.comboBox.modelColumn())
        sourceIdx = self._proxyModel.mapToSource(proxyIdx)

        filterIdx = self.browser.tableView.model().mapFromSource(sourceIdx)
        if filterIdx.isValid():
            self.browser.tableView.selectRow(filterIdx.row())
        else:
            logger.warning("Unable to select color map of combobox in dialog box: {}"
                           .format(curRow))


    @pyqtSlot(int)
    def _onCurrentChanged(self, row):
        """ Emits sigColorMapSelected if a valid row has been selected
        """
        try:
            colorMap = self._proxyModel.getColorMapByRow(row)
            self.sigColorMapChanged.emit(colorMap)
        except IndexError as ex:
            logger.warning("No color map found for row: {}".format(row))


    def getCurrentColorMap(self):
        """ Gets the current colorMap

            Returns None if None selected.
        """
        row = self.comboBox.currentIndex()
        try:
            return self._proxyModel.getColorMapByRow(row)
        except IndexError:
            return None


    def _onDialogAccepted(self):
        """ Sets the color that was selected to the combobox.
        """
        colorMap = self.browser.tableView.getCurrentColorMap()
        logger.debug("Accepted color map from dialog: {}".format(colorMap.pretty_name))

        self._proxyModel.colorMapFromDialog = colorMap
        self._proxyModel.invalidateFilter()
        self.comboBox.setCurrentText(colorMap.pretty_name)



    def _onDialogRejected(self):
        """ Sets the color that was selected to the combobox.
        """
        self.sigColorMapHighlighted.emit(self._colorMapAtShow)