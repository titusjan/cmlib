""" Demonstration of the colormap library and widgets
"""

import logging
import os.path

from PyQt5 import QtWidgets


from cmlib import ColorLib, ColorLibModel, ColorSelectionWidget, CmLibBrowser


logger = logging.getLogger("demo")


def main():
    app = QtWidgets.QApplication([])

    data_dir=os.path.abspath("data")

    colorLib = ColorLib()
    colorLib.load_catalog(os.path.join(data_dir, 'CET'))
    colorLib.load_catalog(os.path.join(data_dir, 'MatPlotLib'))
    colorLib.load_catalog(os.path.join(data_dir, 'SciColMaps'))

    logger.debug("Number of color maps: {}".format(len(colorLib.color_maps)))

    # Set some random favorites to test the favorite checkbox

    for colorMap in colorLib.color_maps:
        if colorMap.key in ['SciColMaps/Oleron', 'CET/CET-CBL1', 'MatPlotLib/Cubehelix']:
            colorMap.meta_data.favorite = True

    colorLibModel = ColorLibModel(colorLib)
    if 1:
        win = ColorSelectionWidget(colorLibModel=colorLibModel)
        win.move(10, 200)
    else:
        win = CmLibBrowser(colorLibModel=colorLibModel)
        win.setGeometry(10, 10, 1200, 500)

    win.show()
    win.raise_()
    app.exec_()

    logger.debug("Favorites:")
    for colorMap in colorLib.color_maps:
        if colorMap.meta_data.favorite:
            logger.debug("  {}".format(colorMap.meta_data.name))


if __name__ == "__main__":
    LOG_FMT = '%(asctime)s %(filename)25s:%(lineno)-4d : %(levelname)-7s: %(message)s'
    logging.basicConfig(level='DEBUG', format=LOG_FMT)
    main()


