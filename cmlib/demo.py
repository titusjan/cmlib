""" Demonstration of the colormap library and widgets
"""
import logging
import os.path

import numpy as np

from cmlib.qtwidgets.bindings import QtCore, QtGui, QtWidgets, Qt, QtSlot
from cmlib.qtwidgets.bindings import PYQT_VERSION, QT_VERSION, QT_API_NAME
from cmlib.qtwidgets.qimg import arrayToQImage
from cmlib import CmLib, CmLibModel, ColorSelectionWidget, CmLibBrowserDialog, DATA_DIR

logger = logging.getLogger("demo")

# the size of the colormap test images
SIZE_X = 350
SIZE_Y = 350


def normalize(img):
    """ Normalizes image values to be between 0 and 1
    """
    zMin, zMax = np.amin(img), np.amax(img)
    offset = zMin
    zRange = zMax - zMin
    return (img - offset )/ zRange



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
    y = np.linspace(1, 0, num=SIZE_Y)
    xx, yy = np.meshgrid(x, y, sparse=False)
    #z = yy + (xx**2) * np.sin(64 * 2 * np.pi * yy) / 12
    z = xx + (yy**2) * np.sin(64 * 2 * np.pi * xx) / 12  # Transposed
    # z = np.clip(z, 0.0, 1.0) # Fails in PyQtGraph 2D plot :-/
    return z


def makeBandTest():
    """ Create 'ramp' function from Peter Karpov's blog http://inversed.ru/Blog_2.htm

        Slightly modified version of the test function introduced by Peter Kovesi
        Good Colour Maps: How to Design Them. Peter Kovesi, arxiv.org, 2015.
        http://arxiv.org/abs/1509.03700

        :return: 2D numpy array
    """
    x = np.linspace(0, 1, num=SIZE_X)
    y = np.linspace(1, 0, num=SIZE_Y)
    xx, yy = np.meshgrid(x, y, sparse=False)
    z = yy + xx**2  # demonstrates banding
    return z


def makeConcentricCircles():
    """ Creates a concentric circle pattern.

        :return: 2D numpy array
    """
    x = np.linspace(-10, 10, num=SIZE_X)
    y = np.linspace(-10, 10, num=SIZE_Y)
    xx, yy = np.meshgrid(x, y, sparse=False)
    z = np.sin(xx**2 + yy**2) / (xx**2 + yy**2)
    return z


def makeArcTan2():
    """ Create atan2(x, y), which is good for testing circular color maps.
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
    return np.random.uniform(0.0, 1.0, size=(SIZE_X, SIZE_Y))


def colorizeImageArray(imageArr, colorMap=None,
                       width=None, height=None, drawBorder=False):
    """ Creates a PixMap that visualizes the color map.
        This can be used in a QLabel to draw a legend.

        The resulting pixmap will be WxHxN ARGB
    """
    assert imageArr.flags['C_CONTIGUOUS'], "expected C-contiguous array"

    if colorMap is None:
        imageArray256 = np.clip(imageArr * (256), 0, 255).astype(np.uint8)

        imageArrBGRA = np.multiply.outer(imageArray256, np.ones(shape=(4,), dtype=np.uint8))
        imageArrBGRA[:, :, 3] = 255  # Set all alpha values to 255
    else:
        rgba_arr = colorMap.rgba_uint8_array

        numColors = len(rgba_arr)
        imageArray256 = np.clip(imageArr * (numColors), 0, numColors-1).astype(np.uint8)
        # Shuffle dimensions to BGRA from RGBA  (which is what Qt uses for ARGB in little-endian mode)
        # Do this by swapping index 0 and 2. If using bgra_arr = rgba_arr[:, [2, 1, 0, 3]], the
        # resulting bgra_arr will be fortran-contiguous, which would have to be fixed later on.
        # Swapping dimensions is faster
        bgra_arr = np.copy(rgba_arr)
        bgra_arr[:, 0] = rgba_arr[:, 2]
        bgra_arr[:, 2] = rgba_arr[:, 0]
        del rgba_arr

        # Apply colormap
        imageArrBGRA = np.take(bgra_arr, imageArray256, axis=0, mode='clip')

    assert imageArrBGRA.flags['C_CONTIGUOUS'], "expected C-contiguous array"
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
    def __init__(self, cmLibModel, **kwargs):
        """ Constructor
        """
        super(DemoWindow, self).__init__(**kwargs)

        self._drawBorder = True
        #self._imageArray = makeRamp()

        self._currentColorMap = None

        self.imageComboBox = QtWidgets.QComboBox()
        self.imageComboBox.addItem("Ramp", userData=makeRamp)
        self.imageComboBox.addItem("Banding", userData=makeBandTest)
        self.imageComboBox.addItem("Concentric Circles", userData=makeConcentricCircles)
        self.imageComboBox.addItem("ArcTan2", userData=makeArcTan2)
        self.imageComboBox.addItem("Spirals", userData=makeSpiral)
        self.imageComboBox.addItem("Sine Product", userData=makeSineProduct)
        self.imageComboBox.addItem("Uniform Noise", userData=makeUniformNoise)

        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setMinimumHeight(150)
        self.imageLabel.setMinimumWidth(150)
        self.imageLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.highLightedLabel = QtWidgets.QLabel()
        self.selectedLabel = QtWidgets.QLabel()
        self.selectionWidget = ColorSelectionWidget(cmLibModel=cmLibModel)
        self.selectionWidget.setButtonText("More...")

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addWidget(self.imageComboBox)
        self.mainLayout.addWidget(self.imageLabel)
        self.mainLayout.addWidget(self.highLightedLabel)
        self.mainLayout.addWidget(self.selectedLabel)
        self.mainLayout.addWidget(self.selectionWidget)

        for i in range(self.mainLayout.count()):
            self.mainLayout.setStretch(i, 0)
        self.mainLayout.setStretch(1, 1)

        self.selectionWidget.sigColorMapHighlighted.connect(self.updateHighlightedLabel)
        self.selectionWidget.sigColorMapChanged.connect(self.updateSelectedLabel)
        self.imageComboBox.currentIndexChanged.connect(self._onImageChanged)

        self._onImageChanged()
        self.updateHighlightedLabel()
        self.updateSelectedLabel(self.selectionWidget.getCurrentColorMap())


    def updateHighlightedLabel(self, colorMap=None):
        """ Updates the label to show which cm has been highlighted in the table
        """
        if colorMap:
            self.highLightedLabel.setText("Highlighted: {}".format(colorMap.pretty_name))
        else:
            self.highLightedLabel.setText("Highlighted: <NONE>")

        self.updateImageLabel(colorMap)


    def updateSelectedLabel(self, colorMap=None):
        """ Updates the label to show which cm has been selected
        """
        if colorMap:
            self.selectedLabel.setText("Selected: {}".format(colorMap.pretty_name))
        else:
            self.selectedLabel.setText("Selected: <NONE>")

        self.updateImageLabel(colorMap)


    def updateImageLabel(self, colorMap=None):
        """ Colorizes the image with the color map.
        """
        self._currentColorMap = colorMap
        pixMap = colorizeImageArray(self._imageArray, colorMap=colorMap,
                                    drawBorder=self._drawBorder)
        self.imageLabel.setPixmap(pixMap)


    @QtSlot()
    def _onImageChanged(self):
        """ Draws and colorizes the selected image
        """
        imgFunction = self.imageComboBox.currentData()
        logger.debug("On image changed: {}".format(imgFunction))
        self._imageArray = normalize(imgFunction())

        logger.debug("Image value range: ({:5.2f}, {:5.2f})"
                     .format(np.amin(self._imageArray), np.amax(self._imageArray)))

        self.updateImageLabel(self._currentColorMap)


def main():
    app = QtWidgets.QApplication([])

    cm_lib = CmLib()
    cm_lib.load_catalog(os.path.join(DATA_DIR, 'ColorBrewer2'))
    cm_lib.load_catalog(os.path.join(DATA_DIR, 'CET'))
    cm_lib.load_catalog(os.path.join(DATA_DIR, 'MatPlotLib'))
    cm_lib.load_catalog(os.path.join(DATA_DIR, 'SciColMaps'))

    logger.debug("Number of color maps: {}".format(len(cm_lib.color_maps)))

    # Set some random favorites to test the favorite checkbox

    for colorMap in cm_lib.color_maps:
        if colorMap.key in ['SciColMaps/Oleron', 'CET/CET-CBL1', 'MatPlotLib/Cubehelix']:
            colorMap.meta_data.favorite = True

    cmLibModel = CmLibModel(cm_lib)
    if 1:
        win = DemoWindow(cmLibModel=cmLibModel)
        win.move(10, 200)
    else:
        win = CmLibBrowserDialog(cmLibModel=cmLibModel)
        win.setGeometry(10, 10, 1200, 500)

    win.selectionWidget.setColorMapByKey("SciColMaps/Hawaii")

    win.show()
    win.raise_()
    app.exec_()

    logger.debug("Favorites:")
    for colorMap in cm_lib.color_maps:
        if colorMap.meta_data.favorite:
            logger.debug("  {}".format(colorMap.meta_data.name))


if __name__ == "__main__":
    LOG_FMT = '%(asctime)s %(filename)25s:%(lineno)-4d : %(levelname)-7s: %(message)s'
    logging.basicConfig(level='DEBUG', format=LOG_FMT)
    logger.info("Imported Qt bindings: {}, version {}, Qt version: {}"
                .format(QT_API_NAME, PYQT_VERSION, QT_VERSION))


    main()


