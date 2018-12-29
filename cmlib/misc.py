""" Miscellaneous routines
"""
import logging
import os.path

import numpy as np


logger = logging.getLogger(__name__)
LOG_FMT = '%(asctime)s %(filename)25s:%(lineno)-4d : %(levelname)-7s: %(message)s'


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
    save_rgb_data(target_file, array)



def load_rgb_data(source_file, delimiter=', ', dtype=np.float32, **kwargs):
    """ Saves a color map array to a target file
    """
    logger.debug("Loading: {}".format(os.path.abspath(source_file)))
    array = np.loadtxt(source_file, delimiter=delimiter, dtype=dtype, **kwargs)
    return array


def save_rgb_data(target_file, array):
    """ Saves a color map array to a target file
    """
    logger.debug("Saving: {}".format(os.path.abspath(target_file)))
    np.savetxt(target_file, array, delimiter=', ', fmt='%8.6f')