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



def create_files(names, category, bw_friendly=False):

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
        md.notes = ''
        md.black_white_friendly = bw_friendly

        if name in ['viridis', 'plasma', 'inferno', 'magma', 'cividis']:
            md.recommended = True
            md.perceptually_uniform = True

        if name in ['gist_rainbow', 'rainbow', 'jet', 'nipy_spectral']:
            md.tags.append('rainbow')

        if name in ['ocean', 'gist_earth', 'terrain']:
            md.tags.append('geo')

        if name in ['flag', 'prism']:
            md.tags.append('repetitive')

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
    create_files(MAPS[0][1], DataCategory.Sequential, bw_friendly=True)
    create_files(MAPS[1][1], DataCategory.Sequential, bw_friendly=True)
    create_files(MAPS[2][1], DataCategory.Sequential)
    create_files(MAPS[3][1], DataCategory.Diverging)
    create_files(MAPS[4][1], DataCategory.Cyclic)
    create_files(MAPS[5][1], DataCategory.Qualitative)
    create_files(MAPS[6][1], DataCategory.Other)


if __name__ == "__main__":
    logging.basicConfig(level='DEBUG', format=LOG_FMT)
    main()
