""" Table model and view classes for examining the color map library
"""
import logging
import os.path

from PyQt5 import QtWidgets

from cmlib.cmap import ColorLib
from cmlib.misc import LOG_FMT


class MyWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        tableView = QtWidgets.QTableView()
        self.mainLayout.addWidget(tableView)



def main():
    app = QtWidgets.QApplication([])

    win = MyWidget()
    win.show()
    win.raise_()
    app.exec_()


def load(data_dir):

    colorLib = ColorLib()
    colorLib.load_catalog(os.path.join(data_dir, 'CET'))


if __name__ == "__main__":
    logging.basicConfig(level='DEBUG', format=LOG_FMT)
    load(data_dir=os.path.abspath("../../data"))


