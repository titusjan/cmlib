""" Ingests Matplotlib colormaps into the data directory.

    Matlplotlib needs to be installed for this script to work. The matplotlib version will be
    copied as the verion number in the source meta data.

    Based on https://matplotlib.org/gallery/color/colormap_reference.html
"""

import logging
import os.path

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap, LinearSegmentedColormap

from cmlib.cmap import DataCategory, CmMetaData, CatalogMetaData
from cmlib.misc import LOG_FMT, save_rgb_floats


logger = logging.getLogger(__name__)

TARGET_DIR = "../cmlib/data/MatPlotLib"


MAPS = [ ('Perceptually Uniform Sequential', [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis']),

         ('Sequential', [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),

         ('Sequential (2)', [ # Not B&W-friendly. Not monotioncally increasing
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']),

         ('Diverging', [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),

         ('Cyclic', ['twilight', 'twilight_shifted', 'hsv']),

         ('Qualitative', [
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c']),

         ('Miscellaneous', [
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar'])]


RECOMMENDED = ['viridis', 'plasma', 'inferno', 'magma', 'cubehelix']

def create_files(names, category, bw_friendly=False, origin='', recommended=False):
    """ Creates color map files.

        Names can be a list of color map names or a {name: notes} dictionary)
        For some maps the category is overriden (hardcoded)
    """

    smd = CatalogMetaData()
    smd.key = "MatPlotLib"
    smd.name = "MatPlotLib"
    smd.version = mpl.__version__
    smd.date = ""
    smd.author = ""
    smd.url = "https://matplotlib.org/tutorials/colors/colormaps.html"
    smd.doi = ""
    smd.license = "Matplotlib license." # https://matplotlib.org/users/license.html

    smd.save_to_json_file(os.path.join(TARGET_DIR, CatalogMetaData.DEFAULT_FILE_NAME))

    for name in names:

        data_file = "{}.csv".format(name)
        target_file = os.path.join(TARGET_DIR, data_file)

        array = make_cm_array(name)
        save_rgb_floats(target_file, array)

        md = CmMetaData(name)
        md.file_name = data_file
        md.category = category
        md.notes = names[name] if type(names) == dict else ''
        md.recommended = recommended

        if origin:
            md.notes = "Origin: {}. {}".format(origin, md.notes)

        md.black_white_friendly = bw_friendly or name in [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'hot', 'afmhot', 'gist_heat', 'copper', 'cubehelix']

        if name in ['viridis', 'plasma', 'inferno', 'magma', 'cividis']:
            md.perceptually_uniform = True

        if name in ['gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'hsv']:
            md.tags.append('Rainbow')

        if name in ['ocean', 'gist_earth', 'terrain']:
            md.tags.append('Geo')

        if name in ['bwr', 'coolwarm', 'seismic']:
            md.category = DataCategory.Diverging

        if name in ['flag', 'prism']:
            md.category = DataCategory.Cyclic

        if name in ['Wistia', 'cividis']:
            md.color_blind_friendly = True

        if name in ['gray', 'cubehelix']:
            md.recommended = True

        md.save_to_json_file(os.path.join(TARGET_DIR, "{}.json".format(name)))


def make_cm_array(name):
    """ Creates array data given the color name.

        The result will be a N by 3 array. Where N is the number of colors in the map

        See https://matplotlib.org/tutorials/colors/colormap-manipulation.html
    """
    cmap = plt.get_cmap(name)

    numColors = cmap.N
    arr = cmap(np.linspace(0.0, 1.0, numColors, dtype=np.float32))

    # arr will be a Nx4 array. The last column is the alpha, which consists of ones.
    assert arr.shape == (numColors, 4), "Shape mismatch for {}".format(name)
    assert np.all(arr[:, 3] == np.ones(numColors)), \
        "Alpha values != 1 encountered: {}".format(name)

    # Strip the last column with alpha values
    return arr[:, 0:3]


def main():

    # Information from:
    # https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/pyplot.py
    # https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/_cm.py

    # Perceptually Uniform Sequential

    create_files(
        names = {
            'inferno':  'Perceptually uniform shades of black-red-yellow',
            'magma':    'Perceptually uniform shades of black-red-white',
            'plasma':   'Perceptually uniform shades of blue-red-yellow',
            'viridis':  'Perceptually uniform shades of blue-green-yellow',
            'cividis':  'Perceptually uniform shades of '
        },
        category=DataCategory.Sequential,
        bw_friendly=True,
        recommended=True,
    )

    # ColorBrewer Sequential (luminance decreases monotonically)
    create_files(
        names = {
            'Blues':     'white to dark blue',
            'BuGn':      'White, light blue, dark green',
            'BuPu':      'White, light blue, dark purple',
            'GnBu':      'White, light green, dark blue',
            'Greens':    'White to dark green',
            'Greys':     'White to black (not linear)',
            'Oranges':   'White, orange, dark brown',
            'OrRd':      'White, orange, dark red',
            'PuBu':      'White, light purple, dark blue',
            'PuBuGn':    'White, light purple, dark green',
            'PuRd':      'White, light purple, dark red',
            'Purples':   'White to dark purple',
            'RdPu':      'White, pink, dark purple',
            'Reds':      'White to dark red',
            'YlGn':      'Light yellow, dark green',
            'YlGnBu':    'Light yellow, light green, dark blue',
            'YlOrBr':    'Light yellow, orange, dark brown',
            'YlOrRd':    'Light yellow, orange, dark red',
        },
        category=DataCategory.Sequential,
        bw_friendly=True,
        origin="Color Brewer",
        recommended=True,
    )

    # Sequential (2)
    # A set of colormaps derived from those of the same name provided
    # with Matlab are also included:
    create_files(
        names = {
            'autumn':      'Sequential linearly-increasing shades of red-orange-yellow',
            'bone':        'Sequential increasing black-white color map with a tinge of blue, to emulate X-ray film',
            'cool':        'Linearly-decreasing shades of cyan-magenta',
            'copper':      'Sequential increasing shades of black-copper',
            'flag':        'Repetitive red-white-blue-black pattern (not cyclic at endpoints)',
            'gray':        'Sequential linearly-increasing black-to-white grayscale',
            'hot':         'Sequential black-red-yellow-white, to emulate blackbody radiation from an object at increasing temperatures',
            'jet':         'A spectral map with dark endpoints, blue-cyan-yellow-red; based on a fluid-jet simulation by NCSA',
            'pink':        'Sequential increasing pastel black-pink-white, meant for sepia tone colorization of photographs',
            'prism':       'Repetitive red-yellow-green-blue-purple-...-green pattern (not cyclic at endpoints)',
            'spring':      'Linearly-increasing shades of magenta-yellow',
            'summer':      'Equential linearly-increasing shades of green-yellow',
            'winter':      'Linearly-increasing shades of blue-green',
        },
        category=DataCategory.Sequential,
        origin='Matlab',
    ) # Some are bw_friendly hardcoded inside

    # ColorBrewer Diverging (luminance is highest at the midpoint, and decreases towards
    # differently-colored endpoints):
    create_files(
        names = {
            'BrBG':      'brown, white, blue-green',
            'PiYG':      'pink, white, yellow-green',
            'PRGn':      'purple, white, green',
            'PuOr':      'orange, white, purple',
            'RdBu':      'red, white, blue',
            'RdGy':      'red, white, gray',
            'RdYlBu':    'red, yellow, blue',
            'RdYlGn':    'red, yellow, green',
            'Spectral':  'red, orange, yellow, green, blue',
        },
        category=DataCategory.Diverging,
        origin="Color Brewer",
        recommended=True,
    )

    # Cyclic
    create_files(
        names = ['twilight', 'twilight_shifted', 'hsv'],
        category=DataCategory.Cyclic)

    # Qualitative
    create_files(
        names = [
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3'],
        category=DataCategory.Qualitative,
        origin="Color Brewer",
        recommended=True,
    )

    # Categorical palettes from Vega:
    # https://github.com/vega/vega/wiki/Scales
    create_files(
        names = [
            'tab10', 'tab20', 'tab20b', 'tab20c'],
        category=DataCategory.Qualitative,
        origin="Vega",
        recommended=True,
    )

    # A set of palettes from the `Yorick scientific visualisation package
    # https://dhmunro.github.io/yorick-doc/, an evolution of the GIST package,
    # both by David H. Munro are included:
    create_files(
        names = {
            'gist_earth':    'Mapmaker\'s colors from dark blue deep ocean to green lowlands to brown highlands to white mountains',
            'gist_heat':     'Sequential increasing black-red-orange-white, to emulate blackbody radiation from an iron bar as it grows hotter',
            'gist_ncar':     'Pseudo-spectral black-blue-green-yellow-red-purple-white colormap from National Center for Atmospheric Research',
            'gist_rainbow':  'Runs through the colors in spectral order from red to violet at full saturation (like *hsv* but not cyclic)',
            'gist_stern':    '"Stern special" color table from Interactive Data Language software',
        },
        category=DataCategory.Sequential,
        origin="Yorick-GIST",
        recommended=False,
    )

    # Other miscellaneous schemes
    create_files(
        names = {
            'afmhot':        'Sequential black-orange-yellow-white blackbody spectrum, commonly used in atomic force microscopy',
            'brg':           'blue-red-green',
            'bwr':           'Diverging blue-white-red',
            'CMRmap':        'Default colormaps on color images often reproduce to confusing grayscale images. The proposed colormap'
                             'maintains an aesthetically pleasing color image that automatically reproduces to a monotonic grayscale with'
                             'discrete, quantifiable saturation levels.',
            'cubehelix':     'Unlike most other color schemes cubehelix was designed by D.A. Green to be monotonically increasing in terms'
                             'of perceived brightness. Also, when printed on a black and white postscript printer, the scheme results in a'
                             'greyscale with monotonically increasing brightness. This color scheme is named cubehelix because the (r, g, b)'
                             'values produced can be visualised as a squashed helix around the diagonal in the (r, g, b) color cube.',
            'gnuplot':       "Gnuplot's traditional pm3d scheme (black-blue-red-yellow)",
            'gnuplot2':      'Sequential color printable as gray (black-blue-violet-yellow-white)',
            'ocean':         'green-blue-white',
            'rainbow':       'Spectral purple-blue-green-yellow-orange-red colormap with diverging luminance',
            'seismic':       'Diverging blue-white-red',
            'nipy_spectral': 'black-purple-blue-green-yellow-red-white spectrum, originally from the Neuroimaging in Python project',
            'terrain':       "Mapmaker's colors, blue-green-yellow-brown-white, originally from IGOR Pro",
        },
        category=DataCategory.Sequential) # Some are diverging
    
    # This bipolar color map was generated from CoolWarmFloat33.csv of
    # "Diverging Color Maps for Scientific Visualization" by Kenneth Moreland.
    # <http://www.kennethmoreland.com/color-maps/>    
    create_files(
        names = {
            'coolwarm':      'diverging blue-gray-red, meant to avoid issues with 3D shading, color blindness, and ordering of colors',
        },
        category=DataCategory.Diverging,
        origin="Kenneth Moreland",
        recommended=True,
    )

    # An MIT licensed, colorblind-friendly heatmap from Wistia:
    #   https://github.com/wistia/heatmap-palette
    #   http://wistia.com/blog/heatmaps-for-colorblindness
    create_files(
        names = {
            'Wistia':    'An MIT licensed, colorblind-friendly heatmap',
        },
        category=DataCategory.Sequential,
        origin='Wistia',
        recommended=True,
    )

    # The following colormaps are redundant and may be removed in future
    # versions.  It's recommended to use the names in the descriptions
    # instead, which produce identical output:
    #   gist_gray  identical to *gray*
    #   gist_yarg  identical to *gray_r*
    #   binary     identical to *gray_r*



if __name__ == "__main__":
    logging.basicConfig(level='DEBUG', format=LOG_FMT)
    main()
