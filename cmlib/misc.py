""" Miscellaneous routines
"""
from __future__ import print_function

import logging
import os.path
import sys

import numpy as np


DEBUGGING = False
LOG_FMT = '%(asctime)s %(filename)25s:%(lineno)-4d : %(levelname)-7s: %(message)s'

logger = logging.getLogger(__name__)



# Reads the version of the program from the first line of version.txt
try:
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the pyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        MODULE_DIR = os.path.join(sys._MEIPASS, 'cmlib')
        if DEBUGGING:
            print("Module dir from meipass: {}".format(MODULE_DIR), file=sys.stderr)
    else:
        MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
        if DEBUGGING:
            print("Module dir from __file__: {}".format(MODULE_DIR), file=sys.stderr)

    VERSION_FILE = os.path.join(MODULE_DIR, 'version.txt')
    if DEBUGGING:
        print("Reading version from: {}".format(VERSION_FILE), file=sys.stderr)
    logger.debug("Reading version from: {}".format(VERSION_FILE))
    with open(VERSION_FILE) as stream:
        __version__ = stream.readline().strip()
except Exception as ex:
    __version__ = "?.?.?"
    logger.error("Unable to read version number: {}".format(ex))
    raise


DATA_DIR = os.path.join(MODULE_DIR, "data")

def is_an_array(var, allow_none=False):
    """ Returns True if var is a numpy array.
    """
    return isinstance(var, np.ndarray) or (var is None and allow_none)


def check_is_an_array(var, allow_none=False):
    """ Calls is_an_array and raises a TypeError if the check fails.
    """
    if not is_an_array(var, allow_none=allow_none):
        raise TypeError("var must be a NumPy array, however type(var) is {}"
                        .format(type(var)))


def check_class(var, cls, allowNone=False):
    """ Checks if a variable is an instance of the cls class, raises TypeError if the check fails.
    """
    if not isinstance(var, cls) and not (allowNone and var is None):
        raise TypeError("Unexpected type {}, was expecting {}".format(type(var), cls))



def copy_data(source_file, target_file): # TODO: obsolete
    """ Copies data file by reading it with numpy.loadtxt and saving with numpy.savetxt.

        This ensures all data has the same format and future users (possibly non-python users)
        can use a single import routine.
    """
    logger.info("Copying: {} -> {}".format(source_file, target_file))
    array = np.loadtxt(source_file)
    save_rgb_floats(target_file, array)



def load_rgb_floats(source_file, delimiter=',', dtype=np.float32, **kwargs):
    """ Loads a color map array from a source file.
        Returns Nx3 array of 32 bits floats
    """
    source_file = os.path.abspath(source_file)
    logger.debug("Loading RGB values: {}".format(source_file))
    array = np.loadtxt(source_file, delimiter=delimiter, dtype=dtype, **kwargs)
    return array


def save_rgb_floats(target_file, array):
    """ Saves a color map array to a target file.

        The array is expected to consist of floats.
    """
    logger.debug("Saving RGB values: {}".format(os.path.abspath(target_file)))
    np.savetxt(target_file, array, delimiter=', ', fmt='%8.6f')


