""" Table model and view classes for examining the color map library

"""
import logging


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal

from cmlib.cmap import ColorLib, ColorMap
from cmlib.misc import check_class
from cmlib.qtwidgets.toggle_column_mixin import ToggleColumnTableView
from cmlib.qtwidgets.qimg import makeColorBarPixmap

logger = logging.getLogger(__name__)

_HW_BOOL = 80 # header width for boolean columns
_ALIGN_STRING = Qt.AlignVCenter | Qt.AlignLeft
_ALIGN_NUMBER = Qt.AlignVCenter | Qt.AlignRight
_ALIGN_BOOLEAN = Qt.AlignVCenter | Qt.AlignHCenter

class ColorLibModel(QtCore.QAbstractTableModel):
    """ A table model that maps ColorLib data as a table.
    """
    HEADERS = ('Favorite', 'Key', 'Catalog', 'Name', 'Category', 'Size', 'Recommended',
               'P. Uniform', 'B & W', 'Color Blind', 'Isoluminant',
               'Tags', 'Notes')

    HEADER_TOOL_TIPS = ('Favorite', 'Key', 'Catalog', 'Name', 'Category', 'Size', 'Recommended',
                        'Perceptually uniform.', 'Black & white Friendly', 'Color Blind friendly',
                        'Isoluminant', 'Tags', 'Notes')

    (COL_FAV, COL_KEY, COL_CATALOG, COL_NAME, COL_CATEGORY, COL_SIZE, COL_RECOMMENDED,
     COL_UNIF, COL_BW, COL_COLOR_BLIND, COL_ISOLUMINANT, COL_TAGS, COL_NOTES) = range(len(HEADERS))

    DEFAULT_WIDTHS = [_HW_BOOL, 175, 100, 120, 100, 50, _HW_BOOL + 10,
                      _HW_BOOL, _HW_BOOL, _HW_BOOL, _HW_BOOL, 100, 200]

    def __init__(self, colorLib, parent=None):
        """ Constructor

            :param ColorLib colorLib: the underlying color library
            :param QWidget parent: Qt parent widget
        """
        super().__init__(parent=parent)
        check_class(colorLib, ColorLib)

        assert len(self.HEADERS) == len(self.DEFAULT_WIDTHS), "sanity check failed."
        assert len(self.HEADERS) == len(self.HEADER_TOOL_TIPS), "sanity check failed."

        self._colorLib = colorLib
        self._colorMaps = colorLib.color_maps # used often

        # Parameters that defined the legend bars. You should dataChanged on the column
        # that contains the icons (COL_NAME) if you change these (or just reset the entire model.)
        self.showIconBars = True
        self.drawIconBarBorder = True
        self.iconBarWidth = 64
        self.iconBarHeight = 16

        # Check mark for boolean columns
        #   ✓ checkmark Unicode: U+2713, UTF-8: E2 9C 93
        #   ✔︎ Heavy check mark Unicode: U+2714 U+FE0E, UTF-8: E2 9C 94 EF B8 8E
        self.checkMarkChar = '✓︎'


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

            elif col == self.COL_SIZE:
                return len(colMap.argb_uint8_array)

            elif col == self.COL_UNIF:
                return self.boolToStr(md.perceptually_uniform)

            elif col == self.COL_BW:
                return self.boolToStr(md.black_white_friendly)

            elif col == self.COL_COLOR_BLIND:
                return self.boolToStr(md.color_blind_friendly)

            elif col == self.COL_ISOLUMINANT:
                return self.boolToStr(md.isoluminant)

            elif col == self.COL_TAGS:
                return ", ".join(md.tags)

            elif col == self.COL_NOTES:
                return md.notes

            elif col == self.COL_FAV:
                return self.boolToStr(md.favorite)

            elif col == self.COL_RECOMMENDED:
                return self.boolToStr(md.recommended)

            else:
                raise AssertionError("Unexpected column: {}".format(col))

        elif role == Qt.TextAlignmentRole:

            if col in (self.COL_KEY, self.COL_CATALOG, self.COL_NAME, self.COL_CATEGORY,
                       self.COL_TAGS, self.COL_NOTES):
                return _ALIGN_STRING
            elif col in (self.COL_FAV, self.COL_RECOMMENDED, self.COL_ISOLUMINANT,
                         self.COL_UNIF, self.COL_BW, self.COL_COLOR_BLIND):
                return _ALIGN_BOOLEAN
            elif col is self.COL_SIZE:
                return _ALIGN_NUMBER
            else:
                raise AssertionError("Unexpected column: {}".format(col))

        elif role == Qt.ToolTipRole:
            if col == self.COL_CATALOG:
                colMap = self._colorMaps[row]
                cmd = colMap.catalog_meta_data
                return " ".join([cmd.name, cmd.version, cmd.date])

        elif role == Qt.DecorationRole:
            if col == self.COL_NAME and self.showIconBars:
                colMap = self._colorMaps[row]
                pixmap = makeColorBarPixmap(colMap,
                                            width=self.iconBarWidth,
                                            height=self.iconBarHeight,
                                            drawBorder=self.drawIconBarBorder)
                return pixmap

        return None


    def boolToStr(self, value):
        """ Shows a checkmark if value is True, the empty string otherwise
        """
        return self.checkMarkChar if value else ""


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Header data given a orientation.

            :param section: row or column number, depending on orientation
            :param orientation: Qt.Horizontal or Qt.Vertical
        """
        if role not in (Qt.DisplayRole, Qt.ToolTipRole):
            return None

        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.HEADERS[section]
            elif role == Qt.ToolTipRole: # doesn't seem to work (tried only on OS-X)
                return self.HEADER_TOOL_TIPS[section]
            else:
                assert False, "Unexpected role: {}".format(role)
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


# TODO: https://github.com/baoboa/pyqt5/blob/master/examples/itemviews/frozencolumn/frozencolumn.py
class ColorLibTableViewer(ToggleColumnTableView):

    sigColorMapSelected = pyqtSignal(ColorMap)

    def __init__(self, model=None, parent=None):
        """ Constructor

            :param ColorLibModel model: the item model
        """
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

        # Make the 'name' color wider because of the legend bar.
        treeHeader.resizeSection(
            ColorLibModel.COL_NAME,
            self._sourceModel.iconBarWidth + ColorLibModel.DEFAULT_WIDTHS[ColorLibModel.COL_NAME])

        headerNames = ColorLibModel.HEADERS
        enabled = dict((name, True) for name in headerNames)
        enabled[headerNames[ColorLibModel.COL_NAME]] = False # Cannot be unchecked
        checked = dict((name, True) for name in headerNames)
        checked[headerNames[ColorLibModel.COL_KEY]] = False
        checked[headerNames[ColorLibModel.COL_SIZE]] = False
        checked[headerNames[ColorLibModel.COL_NOTES]] = False
        self.addHeaderContextMenu(checked=checked, enabled=enabled, checkable={})

        self.setContextMenuPolicy(Qt.DefaultContextMenu) # will call contextMenuEvent

        self._selectionModel = self.selectionModel()
        self._selectionModel.currentChanged.connect(self._onCurrentChanged)

        self.sortByColumn(ColorLibModel.COL_CATEGORY, Qt.AscendingOrder)


    def _onCurrentChanged(self, curIdx, _prevIdx):
        """ Emits sigColorMapSelected if a valid row has been selected
        """
        if not curIdx.isValid():
            return None

        sourceIdx = self._proxyModel.mapToSource(curIdx)
        assert sourceIdx.isValid(), "Source Index not valid"

        row = sourceIdx.row()
        colorMap = self._sourceModel.colorLib.color_maps[row]

        logger.debug("Emitting sigColorMapSelected: {}".format(colorMap))
        self.sigColorMapSelected.emit(colorMap)



