""" Classes to represent color maps and meta data from various sources in uniform way.


    How to pick a good color map:
        1) Select a map category depending on your data: sequenitial, diverging, cyclic
        2) Select a good quality map.
        3) Select a map for your domain and application. Geographical, textures.

    Color maps are divided in categories. Which category is the best depends on the data that
    you want to visualise. There is no consensus on the different categories. The categories here
    are based on Peter Kovesi's (https://peterkovesi.com/projects/colourmaps/), the MatPlotLib
    categories (https://matplotlib.org/tutorials/colors/colormaps.html.) and ColorBrewer
    http://colorbrewer2.org/#type=sequential&scheme=BuGn&n=3

    The following categories are defined.

        Sequential: change in lightness and often saturation of color incrementally, often using a
            single hue; should be used for representing information that has ordering.

        Diverging: change in lightness and possibly saturation of two different colors that meet in
            the middle at an unsaturated color; should be used when the information being plotted
            has a critical middle value, such as topography or when the data deviates around zero.

        Qualitative: often are miscellaneous colors; should be used to represent information which
            does not have ordering or relationships.

        Cyclic: change in lightness of two different colors that meet in the middle and
            beginning/end at an unsaturated color; should be used for values that wrap around at
            the endpoints, such as phase angle, wind direction, or time of day.

        Other: color maps that don't fit in one of the above categories. This includes
            typical rainbow maps. Researchers have found that the human brain perceives changes in
            the lightness parameter as changes in the data much better than, for example, changes
            in hue. Therefore the Sequential maps should be preferred to visualize ordered data.


    2) Quality:

    Perceptually uniform: maps in which equal steps in data are perceived as equal steps in the
        color space. For many applications, a perceptually uniform colormap is the best choice.

    Isoluminant: color maps are constructed from colors of equal perceptual lightness. These
        colour maps are designed for use with relief shading. On their own these colour maps are
        not very useful because features in the data are very hard to discern. However, when used
        in conjunction with relief shading their constant lightness means that the colour map does
        not induce an independent shading pattern that will interfere with, or even hide, the
        structures induced by the relief shading. The relief shading provides the structural
        information and the colours provide the data classification information.

    Black & white friendly: color maps where the lightness strictly increases over the range.
        Only sequential maps can be bw-friendly, but not all sequential maps are.

    Colorblind friendly: limited to colors that can be distinguished by most color blind people.

    Recommended:
        A color map that has been design with quality in mind. So not the dreaded rainbow.
        https://github.com/djoshea/matlab-utils/blob/master/libs/perceptuallyImprovedColormaps/Rainbow%20Color%20Map%20-Still-%20Considered%20Harmful.pdf

    3) Domain and application.
    Tags:
        - GeoGraphical:
        - 3D friendly: for use as textures on 3D objects and hill shading

"""
import abc
import enum
import glob
import json
import logging
import os.path

from collections import OrderedDict

import numpy as np

from .misc import check_class, check_is_an_array, load_rgb_floats

logger = logging.getLogger(__name__)

class DataCategory(enum.Enum):
    Sequential = 1
    Cyclic = 2
    Diverging = 3
    Qualitative = 4
    Other = 5




# TODO: in the future we perhaps could use Python 3.7 Data Classes
class AbstractMetaData(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def from_dict(self, dct):
        raise NotImplementedError()

    @abc.abstractmethod
    def as_dict(self):
        raise NotImplementedError()

    def load_from_json(self, file_name):
        logger.debug("Loading meta data: {}".format(os.path.abspath(file_name)))
        with open(file_name, 'r') as fp:
            return self.from_dict(json.load(fp))

    def save_to_json_file(self, file_name):
        logger.debug("Saving: {}".format(os.path.abspath(file_name)))
        with open(file_name, 'w') as fp:
            json.dump(self.as_dict(), fp, indent=4)

    @classmethod
    def create_from_json(cls, file_name):
        obj = cls()
        obj.load_from_json(file_name)
        return obj


class CmMetaData(AbstractMetaData):

    def __init__(self, name=""):
        self.name = name
        self.pretty_name = self.make_pretty_name(name)
        self.file_name = ""
        self.recommended = False
        self.category = DataCategory.Other
        self.perceptually_uniform = False
        self.black_white_friendly = False
        self.color_blind_friendly = False
        self.isoluminant = False
        self.notes = ''
        self.tags = []
        self.favorite = None # Not persistent unless explicitly set to True or False


    @classmethod
    def make_pretty_name(cls, name):
        """ Replaces underscore with hyphens. Capitalizes the first letter and after hyphens.
        """
        partsIn = name.replace('_', '-').split('-')
        partsOut = []

        for part in partsIn:
            # We cant user string.capitalize because it will make lower case of some letters
            partsOut.append(part[:1].upper() + part[1:])

        return "-".join(partsOut)


    def from_dict(self, dct):
        self.name = dct['name']
        self.pretty_name = dct['pretty_name']
        self.file_name = dct['file_name']
        self.category = DataCategory[dct['category']]
        self.recommended = dct.get('recommended', False)
        self.perceptually_uniform = dct.get('perceptually_uniform', False)
        self.black_white_friendly = dct.get('black_white_friendly', False)
        self.color_blind_friendly = dct.get('color_blind_friendly', False)
        self.isoluminant = dct.get('isoluminant', False)
        self.notes = dct.get('notes', '')
        self.tags = dct.get('tags', [])
        self.favorite = dct.get('favorite', False)


    def as_dict(self):
        dct = OrderedDict(
            name = self.name,
            pretty_name = self.pretty_name,
            file_name = self.file_name,
            category = self.category.name,
            recommended = self.recommended,
            perceptually_uniform = self.perceptually_uniform,
            black_white_friendly = self.black_white_friendly,
            color_blind_friendly = self.color_blind_friendly,
            isoluminant = self.isoluminant,
            notes = self.notes,
            tags = self.tags)

        # Only persistent if explicitly set to True or False
        if self.favorite is not None:
            dct['favorite'] = self.favorite

        return dct



class CatalogMetaData(AbstractMetaData):
    """ Catalog info. All color maps of a single source (e.g. CET, Matplotlib) make up a catalog.
    """
    DEFAULT_FILE_NAME = "_catalog.json"

    def __init__(self, key="", name=""):
        self.key = key   # unique idenfifier for the color map
        self.name = name
        self.version = ""
        self.date = ""
        self.author = ""
        self.url = ""
        self.doi = ""  # Digital Object Identifier (e.g. from Zenodo)
        self.license = ""


    def from_dict(self, dct):
        self.key = dct['key']
        self.name = dct['name']
        self.version = dct.get('version', '')
        self.date = dct.get('date', '')
        self.author = dct.get('author', '')
        self.url = dct.get('url', '')
        self.doi = dct.get('doi', '')
        self.license = dct.get('license', '')


    def as_dict(self):
        return OrderedDict(
            key = self.key,
            name = self.name,
            version = self.version,
            date = self.date,
            author = self.author,
            url = self.url,
            doi = self.doi,
            license = self.license)



class ColorMap():
    """ Represents color map data.
    """
    def __init__(self, meta_data, catalog_meta_data, rgb_file_name=None):
        self._key = None
        self._prettyName = None
        self._rgb_float_array = None
        self._argb_uint8_array = None
        self._meta_data = None
        self._catalog_meta_data = None

        self.rgb_file_name = rgb_file_name
        self.meta_data = meta_data
        self.catalog_meta_data = catalog_meta_data

    def __repr__(self):
        return "<ColorMap {}>".format(self.key)


    @property
    def pretty_name(self):
        """ The pretty name from the metadata."""
        return self.meta_data.pretty_name


    @property
    def key(self):
        """ Uniquely identifies the map."""
        if self._key is None:
            # Using pretty_name which all start with capitals. This yields better sorting.
            self._key = "{}/{}".format(self.catalog_meta_data.key, self.meta_data.pretty_name)
        return self._key


    @property
    def meta_data(self):
        return self._meta_data


    @meta_data.setter
    def meta_data(self, md):
        check_class(md, CmMetaData, allowNone=True)
        self._meta_data = md
        self._key = None # invalidate cache


    @property
    def catalog_meta_data(self):
        return self._catalog_meta_data


    @catalog_meta_data.setter
    def catalog_meta_data(self, cmd):
        check_class(cmd, CatalogMetaData, allowNone=True)
        self._catalog_meta_data = cmd
        self._key = None # invalidate cache


    @property
    def rgb_float_array(self):
        """ Gets the rgb data. Loads the data from file if needed.
        """
        if self._rgb_float_array is None:
            self.load_rgb_float_array()
        return self._rgb_float_array


    def load_rgb_float_array(self, file_name=None):
        """ Loads the rgb data from file.

            :param str file_name: the rgb file. If None, the rgb_file_name property will be used.
        """
        if file_name is None:
            file_name = self.rgb_file_name

        self.set_rgb_float_array(load_rgb_floats(file_name))


    def set_rgb_float_array(self, rgb_arr):
        """ Explicitly sets the rgb data.

            Typically not used directly because the rgb data is loaded automatically when needed.
        """
        check_is_an_array(rgb_arr)
        assert rgb_arr.ndim == 2, "Expected 2D array. Got {}D".format(rgb_arr.ndim)
        _, n_cols = rgb_arr.shape
        assert n_cols == 3, "Expected 3 columns. Got: {}".format(n_cols)
        if rgb_arr.dtype != np.float32:
            raise TypeError("Expected np.float32. Got: {}".format(rgb_arr.dtype))

        self._rgb_float_array = rgb_arr


    @property
    def argb_uint8_array(self):
        """ Gets the argb data as bytes. Loads the data from file if needed.

            Returns 4xN array (ARGB). This format can be used to create Qt images.
        """
        if self._argb_uint8_array is None:
            self.load_argb_uint8_array()
        return self._argb_uint8_array


    def load_argb_uint8_array(self, file_name=None):
        """ Loads the rgb data from file.

            :param str file_name: the rgb file. If None, the rgb_file_name property will be used.
        """
        if file_name is None:
            file_name = self.rgb_file_name
        rgb_floats = load_rgb_floats(file_name)

        # Convert from float to bytes and append column
        rgb_floats *= 256
        rgb_floats = np.clip(rgb_floats, 0, 255)
        n_rows, depth = rgb_floats.shape
        assert depth == 3, "sanity check"

        argb_ints = np.ones(shape=(n_rows, 4), dtype=np.uint8) * 255
        argb_ints[:, 0:3] = rgb_floats.astype(np.uint8)

        self.set_argb_unit8_array(argb_ints)


    def set_argb_unit8_array(self, argb_arr):
        """ Explicitly sets the ARGB uint8 data.

            Typically not used directly because the argb data is loaded automatically when needed.
        """
        check_is_an_array(argb_arr)
        assert argb_arr.ndim == 2, "Expected 2D array. Got {}D".format(argb_arr.ndim)
        _, n_cols = argb_arr.shape
        assert n_cols == 4, "Expected 3 columns. Got: {}".format(n_cols)
        if argb_arr.dtype != np.uint8:
            raise TypeError("Expected np.float32. Got: {}".format(argb_arr.dtype))

        self._argb_uint8_array = argb_arr



class ColorLib():
    """ The color library.

        Consists of a list of color maps and a directory name where the data is stored.
    """
    def __init__(self):
        self._color_maps = []


    @property
    def color_maps(self):
        """ The list of color maps"""
        return self._color_maps


    def clear(self):
        """ Removes all color maps
        """
        self._color_maps.clear()


    def load_catalog(self, catalog_dir):
        """ Loads all color maps from a catalogue directory

            Loads metadata. The actual color data is lazy loaded (i.e. when needed).
        """
        catalog_file = os.path.abspath(os.path.join(catalog_dir, CatalogMetaData.DEFAULT_FILE_NAME))
        cmd = CatalogMetaData.create_from_json(catalog_file)

        json_files_glob = os.path.join(catalog_dir, '*.json')
        for md_file_name in glob.iglob(json_files_glob):
            if md_file_name.endswith(CatalogMetaData.DEFAULT_FILE_NAME):
                continue # skip catalog json file

            md_file_path = os.path.join(catalog_dir, md_file_name)
            md = CmMetaData.create_from_json(md_file_path)

            rgb_file_path = os.path.join(catalog_dir, md.file_name)

            colorMap = ColorMap(meta_data=md, catalog_meta_data=cmd, rgb_file_name=rgb_file_path)
            self._color_maps.append(colorMap)