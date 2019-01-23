""" Demonstration of the colormap library and widgets
"""

import logging
import os.path

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from cmlib import ColorLib, ColorLibModel, ColorSelectionWidget, CmLibBrowserDialog
from cmlib.qtwidgets.qimg import arrayToQImage

logger = logging.getLogger("demo")


# the size of the colormap test images
SIZE_X = 500
SIZE_Y = 500

def makeConcentricCircles():
    """ Creates concentric cricle pattern.

        :return: 2D numpy array
    """
    x = np.linspace(-10, 10, num=SIZE_X)
    y = np.linspace(-10, 10, num=SIZE_Y)
    xx, yy = np.meshgrid(x, y, sparse=False)
    z = np.sin(xx**2 + yy**2) / (xx**2 + yy**2)
    return z


def makeRamp():
    """ Create 'ramp' function from Peter Karpov's blog http://inversed.ru/Blog_2.htm

        Slightly modified version of the test function introduced by Peter Kovesi
        Good Colour Maps: How to Design Them. Peter Kovesi, arxiv.org, 2015.
        http://arxiv.org/abs/1509.03700

        Allows to visually assess perceptual uniformity by observing the distance at which the sine \
        pattern fades.

        :return: 2D numpy array
    """
    x = np.linspace(0, 1, num=SIZE_X)
    y = np.linspace(0, 1, num=SIZE_Y)
    xx, yy = np.meshgrid(x, y, sparse=False)
    #z = yy + xx**2  # demonstrates banding
    z = yy + (xx**2) * np.sin(64 * 2 * np.pi * yy) / 12
    # z = np.clip(z, 0.0, 1.0) # Fails in PyQtGraph 2D plot :-/
    return z


def makeArcTan2():
    """ Create atan2(x, y), which is goog for testing circular color maps.
        :return: 2D numpy array
    """
    x = np.linspace(-1, 1, num=SIZE_X)
    y = np.linspace(-1, 1, num=SIZE_Y)
    xx, yy = np.meshgrid(x, y, sparse=False)
    return np.arctan2(xx, yy)


def makeSpiral():
    """ Create 'spiral' function from Peter Karpov's blog http://inversed.ru/Blog_2.htm

        Smoothness test, has a near-uniform distribution of values.
        :return: 2D numpy array
    """
    x = np.linspace(-1, 1, num=SIZE_X)
    y = np.linspace(-1, 1, num=SIZE_Y)
    xx, yy = np.meshgrid(x, y, sparse=False)
    return np.arcsin(np.sin(2 * 2 * np.pi * (xx**2 + yy**2) + np.arctan2(xx, yy)))


def makeSineProduct():
    """ Create 'two sines products' function from Peter Karpov's blog http://inversed.ru/Blog_2.htm

        Smoothness test.
        :return: 2D numpy array
    """
    x = np.linspace(-np.pi, np.pi, num=SIZE_X)
    y = np.linspace(-np.pi, np.pi, num=SIZE_Y)
    xx, yy = np.meshgrid(x, y, sparse=False)
    return np.sin(xx) * np.sin(yy) + np.sin(3*xx) * np.sin(3*yy)


def makeUniformNoise():
    """ Uniform noise between 0 and 1
    """
    return np.random.uniform(0.0, 1.0, size=(400, 300))


def colorizeImageArray(imageArr: np.ndarray, colorMap=None,
                       width=None, height=None, drawBorder=False):
    """ Creates a PixMap that visualizes the color map.
        This can be used in a QLabel to draw a legend.

        The resulting pixmap will be WxHxN ARGB
    """
    #rgba_arr = colorMap.argb_uint8_array

    # # Shuffle dimensions to BGRA from RGBA  (which what Qt uses for ARGB in little-endian mode)
    # # Do this by swapping index 0 and 2. If using bgra_arr = rgba_arr[:, [2, 1, 0, 3]], the
    # # resulting bgra_arr will be fortran-contiguous, which would have to fixed later on.
    # # Swapping dimensions is faster
    # bgra_arr = np.copy(rgba_arr)
    # bgra_arr[:, 0] = rgba_arr[:, 2]
    # bgra_arr[:, 2] = rgba_arr[:, 0]
    # del rgba_arr
    # imageArr = np.expand_dims(bgra_arr, 0)  # Add a dimension to get a N x 1 x 4 array

    assert imageArr.flags['C_CONTIGUOUS'], "expected C-contiguous array"

    imageArray256 = np.clip(imageArr * 256, 0, 255).astype(np.uint8)

    imageArrBGRA = np.multiply.outer(imageArray256, np.ones(shape=(4,), dtype=np.uint8))
    imageArrBGRA[:, :, 3] = 255  # Set all alpha values to 255

    print(imageArrBGRA)

    image = arrayToQImage(imageArrBGRA, share_memory=False)

    # Scale image if height of width are defined
    if width is not None or height is not None:
        if width is None:
            width = image.width()
        if height is None:
            height = image.height()

        image = image.scaled(width, height)

    pixmap = QtGui.QPixmap.fromImage(image)

    height, width = imageArr.shape

    if drawBorder:
        painter = QtGui.QPainter(pixmap)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QtCore.QRect(0, 0, width-1, height-1))
        painter.end()

    return pixmap


class DemoWindow(QtWidgets.QWidget):
    """ Demo window
    """
    def __init__(self, colorLibModel: ColorLibModel, **kwargs):
        """ Constructor
        """
        super().__init__(**kwargs)

        #pixMap = makeColorBarPixmap(colorMap, width=256, height=25)
        self.imageLabel = QtWidgets.QLabel()
        imageArrayFloat = makeRamp()
        pixMap = colorizeImageArray(imageArrayFloat, drawBorder=True)
        self.imageLabel.setPixmap(pixMap)

        self.highLightedLabel = QtWidgets.QLabel()
        self.selectedLabel = QtWidgets.QLabel()
        self.selectionWidget = ColorSelectionWidget(colorLibModel=colorLibModel)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addWidget(self.imageLabel)
        self.mainLayout.addWidget(self.highLightedLabel)
        self.mainLayout.addWidget(self.selectedLabel)
        self.mainLayout.addWidget(self.selectionWidget)

        self.selectionWidget.sigColorMapHighlighted.connect(self.updateHighlightedLabel)
        self.selectionWidget.sigColorMapChanged.connect(self.updateSelectedLabel)

        self.updateHighlightedLabel()
        self.updateSelectedLabel(self.selectionWidget.getCurrentColorMap())


    def updateHighlightedLabel(self, colorMap=None):
        """ Updates the label to show which cm has been highlighted in the table
        """
        if colorMap:
            self.highLightedLabel.setText("Highlighted: {}".format(colorMap.pretty_name))
        else:
            self.highLightedLabel.setText("Highlighted: <NONE>")


    def updateSelectedLabel(self, colorMap=None):
        """ Updates the label to show which cm has been selected
        """
        if colorMap:
            self.selectedLabel.setText("Selected: {}".format(colorMap.pretty_name))
        else:
            self.selectedLabel.setText("Selected: <NONE>")



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
        win = DemoWindow(colorLibModel=colorLibModel)
        win.move(10, 200)
    else:
        win = CmLibBrowserDialog(colorLibModel=colorLibModel)
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


