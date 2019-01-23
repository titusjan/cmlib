""" Color Map Library

    A library of color map from different sources.


    MatPlotLib documentation on color maps is pretty good:
        https://matplotlib.org/api/cm_api.html#matplotlib.cm.get_cmap
        https://matplotlib.org/gallery/color/colormap_reference.html        # list of maps
        https://matplotlib.org/tutorials/colors/colormap-manipulation.html
        https://matplotlib.org/tutorials/colors/colormaps.html          # choosing a good color map
        https://matplotlib.org/tutorials/colors/colormapnorms.html

"""

from misc import __version__

# Classes that may be of user externally. I.e. by users of CmLib
from cmlib.cmap import ColorLib, ColorMap, DataCategory
from cmlib.qtwidgets.browser import CmLibBrowserDialog
from cmlib.qtwidgets.selection import ColorSelectionWidget
from cmlib.qtwidgets.table import ColorLibModel
