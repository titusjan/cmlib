""" Table model and view classes for examining the color map library
"""
import logging


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal

from cmlib.cmap import ColorLib, ColorMap
from cmlib.misc import LOG_FMT, check_class
from cmlib.qtwidgets.toggle_column_mixin import ToggleColumnTableView

logger = logging.getLogger(__name__)


class ColorLibModel(QtCore.QAbstractTableModel):
    """ A table model that contains a color lib
    """
    HEADERS = ['Key', 'Name', 'Catalog', 'Category']  # TODO: size
    (COL_KEY, COL_NAME, COL_CATALOG, COL_CATEGORY) = range(len(HEADERS))

    DEFAULT_WIDTHS = [175, 125, 125, 125]

    def __init__(self, colorLib, parent=None):
        """ Constructor

            :param ColorLib colorLib: the underlying color library
            :param QWidget parent: Qt parent widget
        """
        super().__init__(parent=parent)
        check_class(colorLib, ColorLib)

        assert len(self.HEADERS) == len(self.DEFAULT_WIDTHS), "sanity check failed."

        self._colorLib = colorLib
        self._colorMaps = colorLib.color_maps # used often


    @property
    def colorLib(self):
        """ Returns the underlying ColorLib
        """
        return self._colorLib


    def rowCount(self, _parent=None):
        """ Returns the number of rows.
        """
        return len(self._colorMaps)


    def columnCount(self, _parent=None):
        """ Returns the number of columns.
        """
        return len(self.HEADERS)


    def flags(self, index):
        """ Returns the item flags for the given index
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


    def data(self, index, role=Qt.DisplayRole):
        """ Returns the data stored under the given role for the item referred to by the index.
        """
        if not index.isValid():
            return None

        row, col = index.row(), index.column()

        if col < 0 or col >= self.columnCount():
            return None

        if row < 0 or row >= self.rowCount():
            return None

        if role == Qt.DisplayRole or role == Qt.EditRole:

            colMap = self._colorMaps[row]
            md = colMap.meta_data

            if col == self.COL_KEY:
                return colMap.key
            elif col == self.COL_NAME:
                return md.pretty_name
            elif col == self.COL_CATALOG:
                return colMap.catalog_meta_data.key
            elif col == self.COL_CATEGORY:
                return md.category.name
            else:
                raise AssertionError("Unexpected column: {}".format(col))

        elif role == Qt.ToolTipRole:
            if col == self.COL_CATALOG:
                colMap = self._colorMaps[row]
                cmd = colMap.catalog_meta_data
                return " ".join([cmd.name, cmd.version, cmd.date])

        return None


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Header data given a orientation.

            :param section: row or column number, depending on orientation
            :param orientation: Qt.Horizontal or Qt.Vertical
        """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        else:
            return str(section)



class ColorLibProxyModel(QtCore.QSortFilterProxyModel):
    """ Proxy model that overrides the sorting.
    """
    def __init__(self, parent):
        super(ColorLibProxyModel, self).__init__(parent)


    def lessThan(self, leftIndex, rightIndex):
        """ Returns true if the value of the item referred to by the given index left is less than
            the value of the item referred to by the given index right, otherwise returns false.

            Sorts first by the desired column and uses the Key as tie breaker
        """
        sourceModel = self.sourceModel()
        leftData  = sourceModel.data(leftIndex)
        rightData = sourceModel.data(rightIndex)

        leftKeyIndex = sourceModel.index(leftIndex.row(), ColorLibModel.COL_KEY)
        rightKeyIndex = sourceModel.index(rightIndex.row(), ColorLibModel.COL_KEY)

        leftKey  = sourceModel.data(leftKeyIndex)
        rightKey = sourceModel.data(rightKeyIndex)

        logger.debug("lessThan: {} <? {} = {}".format(
            (leftData, leftKey), (rightData, rightKey),
            (leftData, leftKey) < (rightData, rightKey)
        ))

        return (leftData, leftKey) < (rightData, rightKey)


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Returns the data for the given role and section in the header with the
            specified orientation.

            Needed to override the vertical header to always be increasing.
        """
        # Take horizontal headers from the source model but override the vertical header
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.sourceModel().headerData(section, orientation, role)
            else:
                return str(section + 1)
        else:
            return None


class ColorLibTableViewer(ToggleColumnTableView):

    sigColorMapSelected = pyqtSignal(ColorMap)

    def __init__(self, model=None, parent=None):
        super().__init__(parent=parent)

        check_class(model, ColorLibModel)
        self._sourceModel = model
        self._proxyModel = ColorLibProxyModel(parent=self)
        self._proxyModel.setSourceModel(self._sourceModel)
        self.setModel(self._proxyModel)

        self.setSortingEnabled(True)
        self.setShowGrid(False)
        self.setCornerButtonEnabled(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.verticalHeader().hide()
        treeHeader = self.horizontalHeader()
        treeHeader.setSectionsMovable(True)
        treeHeader.setStretchLastSection(True)
        treeHeader.setSectionResizeMode(QtWidgets.QHeaderView.Interactive) # don't set to stretch

        for col, width in enumerate(ColorLibModel.DEFAULT_WIDTHS):
            treeHeader.resizeSection(col, width)

        headerNames = ColorLibModel.HEADERS
        enabled = dict((name, True) for name in headerNames)
        enabled[headerNames[ColorLibModel.COL_NAME]] = False # Cannot be unchecked
        checked = dict((name, True) for name in headerNames)
        checked[headerNames[ColorLibModel.COL_KEY]] = False
        self.addHeaderContextMenu(checked=checked, enabled=enabled, checkable={})

        self.setContextMenuPolicy(Qt.DefaultContextMenu) # will call contextMenuEvent

        self._selectionModel = self.selectionModel()
        self._selectionModel.currentChanged.connect(self._onCurrentChanged)

        self.sortByColumn(ColorLibModel.COL_NAME, Qt.AscendingOrder)



    def _onCurrentChanged(self, curIdx, _prevIdx):
        """ Emits sigColorMapSelected if a valid row has been selected
        """
        if not curIdx.isValid():
            return None

        row = curIdx.row()
        colorMap = self._sourceModel.colorLib.color_maps[row]

        logger.debug("Emitting sigColorMapSelected: {}".format(colorMap))
        self.sigColorMapSelected.emit(colorMap)



