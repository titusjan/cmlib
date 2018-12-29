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


