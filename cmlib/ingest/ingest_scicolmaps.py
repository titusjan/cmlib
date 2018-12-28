""" Ingests the Scientific color maps into the data directory.

    Since the source data is already in the common format (text files with RGB floats 0 to 1),
    we only have to copy the files and add meta-data.
"""


SOURCE_DIR = "../../source_data/ScientificColourMaps4"
TARGET_DIR = "../../data/ScientificColourMaps4"

import os.path
import shutil

from cmlib.cmap import DataCategory, CmMetaData, SourceMetaData


MAPS = [
    ("acton", DataCategory.Sequential),
    ("bamako", DataCategory.Sequential),
    ("batlow", DataCategory.Sequential),
    ("berlin", DataCategory.Diverging),
    ("bilbao", DataCategory.Sequential),
    ("broc", DataCategory.Diverging),
    ("buda", DataCategory.Sequential),
    ("cork", DataCategory.Diverging),
    ("davos", DataCategory.Sequential),
    ("devon", DataCategory.Sequential),
    ("grayC", DataCategory.Sequential),
    ("hawaii", DataCategory.Sequential),
    ("imola", DataCategory.Sequential),
    ("lajolla", DataCategory.Sequential),
    ("lapaz", DataCategory.Sequential),
    ("lisbon", DataCategory.Diverging),
    ("nuuk", DataCategory.Sequential),
    ("oleron", DataCategory.Other),
    ("oslo", DataCategory.Sequential),
    ("roma", DataCategory.Sequential),
    ("tofino", DataCategory.Diverging),
    ("tokyo", DataCategory.Sequential),
    ("turku", DataCategory.Sequential),
    ("vik", DataCategory.Diverging),
]

def ingest_files():

    smd = SourceMetaData()
    smd.name = "Scientific Colour-Maps"
    smd.version = "4.0.1"
    smd.author = "Crameri, F."
    smd.url = "http://www.fabiocrameri.ch/colourmaps.php"
    smd.doi = "10.5281/zenodo.2527899"
    smd.license = "Creative Commons Attribution 4.0 International License"

    smd.save_to_json_file(os.path.join(TARGET_DIR, SourceMetaData.DEFAULT_FILE_NAME))

    for name, category in MAPS:
        data_file = "{}.txt".format(name)
        source_file = os.path.join(SOURCE_DIR, name, data_file)
        print("copying: {} -> {}".format(source_file, TARGET_DIR))
        shutil.copy2(source_file, TARGET_DIR)

        md = CmMetaData(name)
        md.file_name = data_file
        md.category = category
        md.perceptually_uniform = True

        md.black_white_friendly = name in ("oslo", "grayC", "turku")

        if name == "oleron":
            md.tags = ['geo']
        elif name == "batlow":
            md.tags = ['rainbow']
        elif name == "roma":
            "seismic-tomography"

        md.save_to_json_file(os.path.join(TARGET_DIR, "{}.json".format(name)))



if __name__ == "__main__":
    ingest_files()

