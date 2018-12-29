""" Functions to ingest the data from the source_directory to the data dir

    The source_data directory contains the data in the original format as downloaded from the
    various websites.

    The data directory will contain the data in a common format. It will contain a sub dir for
    every color map source. This contains a text file for each color map. Every line will contain
    3 or 4 RGB tuples of floating points values between 0 and 1.

    Every source subdir also contains a metadata.json file.


    Color maps on the internet:

        https://github.com/jiffyclub/palettable/issues
        http://www.fabiocrameri.ch/colourmaps.php
        http://colorcet.pyviz.org/ which comes from https://peterkovesi.com/projects/colourmaps/
"""
import logging
import os.path
import numpy as np

logger = logging.getLogger(__name__)

LOG_FMT = '%(asctime)s %(filename)25s:%(lineno)-4d : %(levelname)-7s: %(message)s'


def copy_data(source_file, target_file):
    """ Copies data file by reading it with numpy.loadtxt and saving with numpy.savetxt.

        This ensures all data has the same format and future users (possibly non-python users)
        can use a single import routine.

        The
    """
    logger.info("Copying: {} -> {}".format(source_file, target_file))
    array = np.loadtxt(source_file)
    save_data(target_file, array)

def save_data(target_file, array):
    logger.info("Saving: {}".format(os.path.abspath(target_file)))
    np.savetxt(target_file, array, delimiter=', ', fmt='%8.6f')
