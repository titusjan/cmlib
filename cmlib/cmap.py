""" Classes to represent color maps and meta data from various sources in uniform way.

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


    Perceptually uniform: maps in which equal steps in data are perceived as equal steps in the
        color space. For many applications, a perceptually uniform colormap is the best choice.

    Black & white friendly: color maps where the lightness strictly increases over the range.
        Only sequential maps can be bw-friendly, but not all sequential maps are.

    Isoluminant: colour maps are constructed from colours of equal perceptual lightness. These
        colour maps are designed for use with relief shading. On their own these colour maps are
        not very useful because features in the data are very hard to discern. However, when used
        in conjunction with relief shading their constant lightness means that the colour map does
        not induce an independent shading pattern that will interfere with, or even hide, the
        structures induced by the relief shading. The relief shading provides the structural
        information and the colours provide the data classification information.

    Texture: useful as textures on 3D object or in combination with hill shading. This category
        includes rainbow color maps.
        color maps that have a medium to lightness (L*) over the complete range. Are
        The ideal texture map has a constant lightness (so that the
        rendered lightness is fully dependend on 3D shadows) and varies perceptually uniform
        in hue. Most (older) rainbow maps do not meet these criteria.


    Recommended

    Avoid the dreaded rainbow.
    https://github.com/djoshea/matlab-utils/blob/master/libs/perceptuallyImprovedColormaps/Rainbow%20Color%20Map%20-Still-%20Considered%20Harmful.pdf
"""
import abc
import enum
import glob
import json
import logging
import os.path

from collections import OrderedDict

from cmlib.misc import check_class, check_is_an_array, load_rgb_data

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
        logger.debug("Loading: {}".format(os.path.abspath(file_name)))
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
        self.file_name = ""
        self.category = DataCategory.Other
        self.perceptually_uniform = False
        self.black_white_friendly = False
        self.color_blind_friendly = False
        self.isoluminant = False
        self.notes = ''
        self.tags = []


    def from_dict(self, dct):
        self.name = dct['name']
        self.file_name = dct['file_name']
        self.category = DataCategory[dct['category']]
        self.perceptually_uniform = dct.get('perceptually_uniform', False)
        self.black_white_friendly = dct.get('black_white_friendly', False)
        self.color_blind_friendly = dct.get('color_blind_friendly', False)
        self.isoluminant = dct.get('isoluminant', False)
        self.notes = dct.get('notes', '')
        self.tags = dct.get('tags', [])


    def as_dict(self):
        return OrderedDict(
            name=self.name,
            file_name = self.file_name,
            category = self.category.name,
            perceptually_uniform = self.perceptually_uniform,
            black_white_friendly = self.black_white_friendly,
            color_blind_friendly = self.color_blind_friendly,
            isoluminant = self.isoluminant,
            notes = self.notes,
            tags = self.tags)


class CatalogMetaData(AbstractMetaData):
    """ Catalog info. All color maps of a single source (e.g. CET, Matplotlib) make up a catalog.
    """
    DEFAULT_FILE_NAME = "_catalog.json"

    def __init__(self, name=""):
        self.name = name
        self.version = ""
        self.date = ""
        self.author = ""
        self.url = ""
        self.doi = ""  # Digital Object Identifier (e.g. from Zenodo)
        self.license = ""

    def from_dict(self, dct):
        self.name = dct['name']
        self.version = dct.get('version', '')
        self.date = dct.get('date', '')
        self.author = dct.get('author', '')
        self.url = dct.get('url', '')
        self.doi = dct.get('doi', '')
        self.license = dct.get('license', '')


    def as_dict(self):
        return OrderedDict(
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
    def __init__(self, meta_data, source_meta_data, rgb_file_name=None):
        self._rgb_data = None
        self._meta_data = None
        self._source_meta_data = None

        self.rgb_file_name = rgb_file_name

        self.meta_data = meta_data
        self.source_meta_data = source_meta_data


    @property
    def meta_data(self):
        return self._meta_data

    @meta_data.setter
    def meta_data(self, md):
        check_class(md, CmMetaData, allowNone=True)
        self._meta_data = md

    @property
    def source_meta_data(self):
        return self._source_meta_data

    @source_meta_data.setter
    def source_meta_data(self, smd):
        check_class(smd, CatalogMetaData, allowNone=True)
        self._source_meta_data = smd

    @property
    def rgb_data(self):
        """ Gets the rgb data. Loads the data from file if needed.
        """
        if self._rgb_data is None:
            self.load_rgb_data()
        return self._rgb_data


    def load_rgb_data(self, file_name=None):
        """ Loads the rgb data from file.

            :param str file_name: the rgb file. If None, the rgb_file_name property will be used.
        """
        if file_name is None:
            file_name = self.rgb_file_name
        self._rgb_data = load_rgb_data(file_name)


    def set_rgb_data(self, rgb_arr):
        """ Explicitly sets the rgb data.

            Typically not used directly because the rgb data is loaded automatically when needed.
        """
        check_is_an_array(rgb_arr)
        assert rgb_arr.ndim == 2, "Expected 2D array. Got {}D".format(rgb_arr.ndim)
        _, n_cols = rgb_arr.shape
        assert n_cols == 3, "Expected 3 columns. Got: {}".format(n_cols)
        self._rgb_data = rgb_arr


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


    def load_catalog(self, catalog_dir):
        """ Loads all color maps from a catalogue directory

            Loads metadata. The actual color data is lazy loaded (i.e. when needed).
        """
        catalog_file = os.path.abspath(os.path.join(catalog_dir, CatalogMetaData.DEFAULT_FILE_NAME))
        smd = CatalogMetaData.create_from_json(catalog_file)

        json_files_glob = os.path.join(catalog_dir, '*.json')
        for md_file_name in glob.iglob(json_files_glob):
            if md_file_name.endswith(CatalogMetaData.DEFAULT_FILE_NAME):
                continue # skip catalog json file

            md_file_path = os.path.join(catalog_dir, md_file_name)
            md = CmMetaData.create_from_json(md_file_path)

            rgb_file_path = os.path.join(catalog_dir, md.file_name)

            colorMap = ColorMap(meta_data=md, source_meta_data=smd, rgb_file_name=rgb_file_path)
            logger.info("Color map size: {}".format(colorMap.rgb_data.shape))