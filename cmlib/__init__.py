""" Color Map Library

    A library of color map from different sources.


    MatPlotLib documentation on color maps is pretty good:
        https://matplotlib.org/api/cm_api.html#matplotlib.cm.get_cmap
        https://matplotlib.org/gallery/color/colormap_reference.html        # list of maps
        https://matplotlib.org/tutorials/colors/colormap-manipulation.html
        https://matplotlib.org/tutorials/colors/colormaps.html          # choosing a good color map
        https://matplotlib.org/tutorials/colors/colormapnorms.html


    TODO:
        look at https://github.com/matplotlib/cmocean (https://matplotlib.org/cmocean/)
"""

from .misc import __version__, MODULE_DIR, DATA_DIR

# Classes that may be of use externally. I.e. by users of CmLib
from .cmap import CmLib, ColorMap, DataCategory, CmMetaData, CatalogMetaData
from .qtwidgets.browser import CmLibBrowserDialog
from .qtwidgets.qimg import makeColorBarPixmap
from .qtwidgets.selection import ColorSelectionWidget
from .qtwidgets.table import CmLibModel
