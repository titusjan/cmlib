""" Functionality to browse through the color maps in a library
"""
import logging
import os.path


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal

from cmlib.cmap import ColorLib, ColorMap
from cmlib.misc import LOG_FMT, check_class
from cmlib.qtwidgets.table import ColorLibModel, ColorLibTableViewer


logger = logging.getLogger(__name__)



class CmLibBrowser(QtWidgets.QWidget):
    """ Widget to browse the though the color library
    """

    def __init__(self, data_dir, parent=None):
        super().__init__(parent=parent)

        self._colorLib = ColorLib()
        self._colorLib.load_catalog(os.path.join(data_dir, 'CET'))
        self._colorLib.load_catalog(os.path.join(data_dir, 'MatPlotLib'))
        self._colorLib.load_catalog(os.path.join(data_dir, 'SciColMaps'))
        self._colorLibModel = ColorLibModel(self._colorLib, parent=self)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.tableView = ColorLibTableViewer(model=self._colorLibModel)
        self.mainLayout.addWidget(self.tableView)

        self.tableView.sigColorMapSelected.connect(self._onColorMapSelected)


    def _onColorMapSelected(self, colorMap):
        logger.debug("Selected ColorMap: {}".format(colorMap))


    def sizeHint(self):
        """ Holds the recommended size for the widget.
        """
        return QtCore.QSize(800, 600)



def main():
    app = QtWidgets.QApplication([])

    win = CmLibBrowser(data_dir=os.path.abspath("../../data"))
    win.show()
    win.raise_()
    app.exec_()



if __name__ == "__main__":
    logging.basicConfig(level='DEBUG', format=LOG_FMT)
    main()


