# -*- coding: utf-8 -*-

""" Table model and view classes for examining the color map library
"""
import logging
import numpy as np


from .bindings import QtCore, QtWidgets, Qt, QtSignal
from .toggle_column_mixin import ToggleColumnTableView
from .qimg import makeColorBarPixmap
from ..cmap import CmLib, ColorMap, CatalogMetaData, CmMetaData
from ..misc import check_class, __version__

logger = logging.getLogger(__name__)

_HW_BOOL = 80 # header width for boolean columns
_ALIGN_STRING = int(Qt.AlignVCenter | Qt.AlignLeft)
_ALIGN_NUMBER = int(Qt.AlignVCenter | Qt.AlignRight)
_ALIGN_BOOLEAN = int(Qt.AlignVCenter | Qt.AlignHCenter)


ALL_ITEMS_STR = "All"

#
# def createTransparentColorMap():
#     """ Creates a color map to use for when not color map is selected"""
#
#     cmMd = CmMetaData(name = "")
#     cmMd.notes = "Transparent color map to use when no color map is selected"
#
#     catMd = CatalogMetaData(key="CmLib", name="ColorMapLib")
#     catMd.version = __version__
#     catMd.license = "BSD"
#
#     colorMap = ColorMap(meta_data=cmMd, catalog_meta_data=catMd)
#
#     colorMap.set_argb_unit8_array(np.zeros(dtype=np.uint8, shape=(16, 4)))
#     return colorMap
#




class CmLibModel(QtCore.QAbstractTableModel):
    """ A table model that maps CmLib data as a table.
    """
    HEADERS = ('★', 'Key', 'Catalog', 'Name', 'Category', 'Size', 'Recommended',
               'P. Uniform', 'B & W', 'Color Blind', 'Isoluminant',
               'Tags', 'Notes')

    HEADER_TOOL_TIPS = ('Favorite', 'Key', 'Catalog', 'Name', 'Category', 'Size', 'Recommended',
                        'Perceptually uniform.', 'Black & white Friendly', 'Color Blind friendly',
                        'Isoluminant', 'Tags', 'Notes')

    (COL_FAV, COL_KEY, COL_CATALOG, COL_NAME, COL_CATEGORY, COL_SIZE, COL_RECOMMENDED,
     COL_UNIF, COL_BW, COL_COLOR_BLIND, COL_ISOLUMINANT, COL_TAGS, COL_NOTES) = range(len(HEADERS))

    DEFAULT_WIDTHS = [32, 175, 100, 120, 100, 50, _HW_BOOL + 10,
                      _HW_BOOL, _HW_BOOL, _HW_BOOL, _HW_BOOL, 100, 200]

    SORT_ROLE = Qt.UserRole

    def __init__(self, cmLib, **kwargs):
        """ Constructor

            :param CmLib cmLib: the underlying color library
            :param QWidget parent: Qt parent widget
        """
        super(CmLibModel, self).__init__(**kwargs)
        check_class(cmLib, CmLib)

        assert len(self.HEADERS) == len(self.DEFAULT_WIDTHS), "sanity check failed."
        assert len(self.HEADERS) == len(self.HEADER_TOOL_TIPS), "sanity check failed."

        self._cmLib = cmLib
        self._colorMaps = cmLib.color_maps # used often

        # Parameters that defined the legend bars. You should dataChanged on the column
        # that contains the icons (COL_NAME) if you change these (or just reset the entire model.)
        self.showIconBars = True
        self.drawIconBarBorder = True
        self.iconBarWidth = 64
        self.iconBarHeight = 16

        # Check mark for boolean columns
        #   ✓ Check mark Unicode: U+2713
        #   ✔︎ Heavy check mark Unicode: U+2714
        self.checkmarkChar = '✓︎'


    @property
    def cmLib(self):
        """ Returns the underlying CmLib
        """
        return self._cmLib


    def rowCount(self, _parent=None):
        """ Returns the number of rows.
        """
        return len(self._colorMaps)


    def columnCount(self, _parent=None):
        """ Returns the number of columns.
        """
        return len(self.HEADERS)


    def _posFromIndex(self, index):
        """ Returns the (row, col) given the index

            Returns None if the index is invalid or row or column are negative or larger than the
            number of rows/cols
        """
        if not index.isValid():
            return None

        row, col = index.row(), index.column()

        if col < 0 or col >= self.columnCount():
            return None

        if row < 0 or row >= self.rowCount():
            return None

        return row, col


    def flags(self, index):
        """ Returns the item flags for the given index
        """
        pos = self._posFromIndex(index)
        if pos is None:
            return None
        else:
            row, col = pos

        result = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if col == self.COL_FAV:
            result = result | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return result


    def _boolToData(self, value, role=Qt.DisplayRole):
        """ If role is the display roel it shows a checkmark if value is True, the empty string
            otherwise. For other roles it just returns the boolean value
        """
        if role == Qt.DisplayRole:
            return self.checkmarkChar if value else ""
        else:
            return bool(value) # convert to bool just in case


    def data(self, index, role=Qt.DisplayRole):
        """ Returns the data stored under the given role for the item referred to by the index.
        """
        pos = self._posFromIndex(index)
        if pos is None:
            return None
        else:
            row, col = pos

        if role == Qt.DisplayRole or role == self.SORT_ROLE:
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
                return len(colMap.rgba_uint8_array)

            elif col == self.COL_UNIF:
                return self._boolToData(md.perceptually_uniform)

            elif col == self.COL_BW:
                return self._boolToData(md.black_white_friendly)

            elif col == self.COL_COLOR_BLIND:
                return self._boolToData(md.color_blind_friendly)

            elif col == self.COL_ISOLUMINANT:
                return self._boolToData(md.isoluminant)

            elif col == self.COL_TAGS:
                return ", ".join(md.tags)

            elif col == self.COL_NOTES:
                return md.notes

            elif col == self.COL_FAV:
                if role == Qt.DisplayRole:
                    return "" # A checkbox will be shown instead
                else:
                    return md.favorite

            elif col == self.COL_RECOMMENDED:
                return self._boolToData(md.recommended)

            else:
                raise AssertionError("Unexpected column: {}".format(col))

        elif role == Qt.CheckStateRole:
            colMap = self._colorMaps[row]
            isFav = colMap.meta_data.favorite

            if col == self.COL_FAV:
                if isFav:
                    return Qt.Checked
                else:
                    return Qt.Unchecked

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
            colMap = self._colorMaps[row]
            if col == self.COL_CATALOG:
                cmd = colMap.catalog_meta_data
                toolTip = " ".join([cmd.name, cmd.version, cmd.date])
            else:
                md = colMap.meta_data
                toolTip = "{}<br/>Size: {} colors<br/>Category: {}".format(
                    md.pretty_name, len(colMap.rgba_uint8_array),
                    md.category.name)
                if md.notes:
                    toolTip = "{}<br/><br/>{}".format(toolTip, md.notes)
            # Use rich text so the tool tip is word-wrapped
            #logger.debug("Tooltip: {}".format(toolTip))
            return "<FONT COLOR=black>{}</FONT>".format(toolTip)

        elif role == Qt.DecorationRole:
            if col == self.COL_NAME and self.showIconBars:
                colMap = self._colorMaps[row]
                pixmap = makeColorBarPixmap(colMap,
                                            width=self.iconBarWidth,
                                            height=self.iconBarHeight,
                                            drawBorder=self.drawIconBarBorder)
                return pixmap

        return None


    def setData(self, index, value, role=Qt.EditRole):
        """ Sets the data of the item at the index to the given value.
            Emits the dataChanged signal.
        """
        logger.debug("setDataCalled(value={} ({}), role={}".format(value, type(value), role))

        if role != Qt.CheckStateRole:
            return 0

        pos = self._posFromIndex(index)
        if pos is None:
            return 0
        else:
            row, col = pos

        logger.debug("setDataCalled(row={}, col={}, value={}".format(row, col, value))

        if col != self.COL_FAV:
            return 0

        colMap = self._colorMaps[row]
        md = colMap.meta_data
        md.favorite = (value == Qt.Checked)

        logger.debug("{} emitting dataChanged signal for cell: ({}, {})".format(self, row, col))
        self.dataChanged.emit(index, index)

        return True


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


    def getColorMapByIndex(self, index):
        """ Returns a color map at row of the given index.

            Returns None if the index is not valid
        """
        if not index.isValid():
            return None
        else:
            return self._colorMaps[index.row()]


    def getColorMapByKey(self, key):
        """ Returns a color map having a key. Returns None if not found.
        """
        return self.cmLib.getColorMapByKey(key)


    def getIndexByKey(self, key):
        """ Returns a color map ha a key.

            Returns invalid index if the key is not found.
        """
        for row, cmap in enumerate(self._colorMaps): # TODO: use ordered dict?
            if cmap.key == key:
                return self.index(row, self.COL_KEY)
        else:
            return QtCore.QModelIndex()



class CmLibProxyModel(QtCore.QSortFilterProxyModel):
    """ Proxy model that overrides the sorting.
    """

    # Filter types
    FT_CATALOG = "ft_catalog"
    FT_CATEGORY = "ft_category"
    FT_QUALITY = "ft_quality"
    FT_TAG = "ft_tag"

    def __init__(self, parent):
        super(CmLibProxyModel, self).__init__(parent)

        self._exlusiveFilters = {
            CmLibProxyModel.FT_CATALOG: ALL_ITEMS_STR,
            CmLibProxyModel.FT_CATEGORY: ALL_ITEMS_STR,
        }
        self._filters = {
            CmLibProxyModel.FT_TAG: [],
            CmLibProxyModel.FT_QUALITY: [],
        }


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


    def lessThan(self, leftIndex, rightIndex):
        """ Returns true if the value of the item referred to by the given index left is less than
            the value of the item referred to by the given index right, otherwise returns false.

            Sorts first by the desired column and uses the Key as tie breaker
        """
        sourceModel = self.sourceModel()
        leftData  = sourceModel.data(leftIndex, role=CmLibModel.SORT_ROLE)
        rightData = sourceModel.data(rightIndex, role=CmLibModel.SORT_ROLE)

        leftKeyIndex = sourceModel.index(leftIndex.row(), CmLibModel.COL_KEY)
        rightKeyIndex = sourceModel.index(rightIndex.row(), CmLibModel.COL_KEY)

        leftKey  = sourceModel.data(leftKeyIndex, role=CmLibModel.SORT_ROLE)
        rightKey = sourceModel.data(rightKeyIndex, role=CmLibModel.SORT_ROLE)

        # logger.debug("lessThan: {} <? {} = {}".format(
        #     (leftData, leftKey), (rightData, rightKey),
        #     (leftData, leftKey) < (rightData, rightKey)
        # ))

        return (leftData, leftKey) < (rightData, rightKey)


    def setExclusiveFilter(self, filterType, desiredValue):
        """ Sets a filter that can have only one value at the time.
            These filters (catalog, category) are typically set by selecting an item of a combobox.
        """
        logger.debug("Setting exclusive {}-filter {!r}".format(filterType, desiredValue))
        self._exlusiveFilters[filterType] = desiredValue

        for key, value in sorted(self._exlusiveFilters.items()):
            logger.debug("   {:15s}{}".format(key, value))

        self.invalidateFilter()


    def toggleFilter(self, filterType, attrName, desiredValue, isFilterAdded):
        """ Adds or removes an 'And' filter (depending on isFilterAdded).
            Rows are accept if all of the metadata attributes have their desired value.
            These filters are typically added/removed by (un)checking the corresponding checkbox
        """
        filt = (attrName, desiredValue)
        if isFilterAdded:
            logger.debug("Adding {}-filter {}".format(filterType, filt))
            self._filters[filterType].append(filt)
        else:
            logger.debug("Removing {}-filter {}".format(filterType, filt))
            self._filters[filterType].remove(filt)

        # for key, value in sorted(self._filters.items()):
        #     logger.debug("   {:15s}{}".format(key, value))
        self.invalidateFilter()


    def filterAcceptsRow(self, sourceRow, sourceParentIndex):
        """ Returns true if the item in the row indicated by the given source_row and
            source_parent should be included in the model.
        """
        assert not sourceParentIndex.isValid(), "sourceParentIndex is not the root index"

        colMap = self.sourceModel().cmLib.color_maps[sourceRow]

        # Exclusive filters (catalog and catergory)
        catMd = colMap.catalog_meta_data
        catalogFilter = self._exlusiveFilters[CmLibProxyModel.FT_CATALOG]
        acceptCatalog = (catalogFilter == catMd.name or catalogFilter == ALL_ITEMS_STR)

        md = colMap.meta_data
        categoryFilter = self._exlusiveFilters[CmLibProxyModel.FT_CATEGORY]
        acceptCategory = (categoryFilter == md.category.name or categoryFilter == ALL_ITEMS_STR)

        # Filters that must all be true
        acceptQuality = all([getattr(md, attrName) == desired for attrName, desired in
                             self._filters[CmLibProxyModel.FT_QUALITY]])  # Note test for all

        acceptTags = all([desired in md.tags for _, desired in
                          self._filters[CmLibProxyModel.FT_TAG]])

        accept = all([acceptCatalog, acceptCategory, acceptQuality, acceptTags])

        # logger.debug("filterAcceptsRow = {}: {:15s}".format(accept, md.pretty_name))
        return accept


    def getColorMapByProxyIndex(self, proxyIdx):
        """ Returns a color map given an index of the proxy model
            Returns None if not found.
        """
        sourceIdx = self.mapToSource(proxyIdx)
        colorMap = self.sourceModel().getColorMapByIndex(sourceIdx)
        return colorMap



    def getProxyIndexByKey(self, key):
        """ Returns the index of the proxy model given the color map key
        """
        sourceIdx = self.sourceModel().getIndexByKey(key)
        return self.mapFromSource(sourceIdx)



# TODO: https://github.com/baoboa/pyqt5/blob/master/examples/itemviews/frozencolumn/frozencolumn.py
class CmLibTableViewer(ToggleColumnTableView):

    sigColorMapHighlighted = QtSignal(ColorMap)

    def __init__(self, model=None, parent=None):
        """ Constructor

            :param CmLibModel model: the item model
        """
        super(CmLibTableViewer, self).__init__(parent=parent)

        self._colorMapNoneSelected = self.createTransparentColorMap()

        check_class(model, CmLibModel)
        self._sourceModel = model
        self._proxyModel = CmLibProxyModel(parent=self)
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

        for col, width in enumerate(CmLibModel.DEFAULT_WIDTHS):
            treeHeader.resizeSection(col, width)

        # Make the 'name' color wider because of the legend bar.
        treeHeader.resizeSection(
            CmLibModel.COL_NAME,
            self._sourceModel.iconBarWidth + CmLibModel.DEFAULT_WIDTHS[CmLibModel.COL_NAME])

        headerNames = CmLibModel.HEADERS
        enabled = dict((name, True) for name in headerNames)
        enabled[headerNames[CmLibModel.COL_NAME]] = False # Cannot be unchecked
        checked = dict((name, True) for name in headerNames)
        checked[headerNames[CmLibModel.COL_KEY]] = False
        checked[headerNames[CmLibModel.COL_SIZE]] = False
        checked[headerNames[CmLibModel.COL_NOTES]] = False
        self.addHeaderContextMenu(checked=checked, enabled=enabled, checkable={})

        self.setContextMenuPolicy(Qt.DefaultContextMenu) # will call contextMenuEvent

        self._selectionModel = self.selectionModel()
        self._selectionModel.currentChanged.connect(self._onCurrentChanged)

        self.sortByColumn(CmLibModel.COL_CATEGORY, Qt.AscendingOrder)


    @classmethod
    def createTransparentColorMap(cls):
        """ Creates a color map to use for when not color map is selected
        """

        cmMd = CmMetaData(name = "")
        cmMd.notes = "Transparent color map to use when no color map is selected"

        catMd = CatalogMetaData(key="CmLib", name="ColorMapLib")
        catMd.version = __version__
        catMd.license = "BSD"

        colorMap = ColorMap(meta_data=cmMd, catalog_meta_data=catMd)

        colorMap.set_rgba_uint8_array(np.zeros(dtype=np.uint8, shape=(16, 4)))
        return colorMap


    def _onCurrentChanged(self, curIdx, _prevIdx):
        """ Emits sigColorMapSelected if a valid row has been selected
        """
        if not curIdx.isValid():
            logger.info("NONE selected")
            colorMap = self._colorMapNoneSelected
        else:
            sourceIdx = self._proxyModel.mapToSource(curIdx)
            assert sourceIdx.isValid(), "Source Index not valid"

            row = sourceIdx.row()
            colorMap = self._sourceModel.cmLib.color_maps[row]

        logger.debug("Emitting sigColorMapSelected: {}".format(colorMap))
        self.sigColorMapHighlighted.emit(colorMap)


    def getCurrentColorMap(self):
        """ Gets the current colorMap

            Returns None if None selected.
        """
        return self._proxyModel.getColorMapByProxyIndex(self.currentIndex())


    def selectRowByKey(self, key):
        """ Selects the row with the color map with key

            Returns the selected row or None, if no color map was found with this key.
        """
        index = self._proxyModel.getProxyIndexByKey(key)
        if not index.isValid():
            logger.warning("No color map found with key {!r}. Ignored selection.".format(key))
            return None

        self.selectRow(index.row())
        return index.row()


    def scrollToCurrent(self):
        """ Scroll to the currently selected color map.
        """
        curIdx = self.currentIndex()
        logger.debug("scrollToCurrent: {} (isValid)".format(curIdx, curIdx.isValid()))
        if curIdx.isValid():
            self.scrollTo(self.currentIndex())
        
        