#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

# To make a release follow these steps:
#   python setup.py bdist_wheel
# or a source distribution as needed for Anaconda
#   rm -rf build dist
#   python setup.py sdist --formats=zip
#   twine check dist/*
#   twine upload dist/cmlib-x.y.z-py3-none-any.whl

# If you get invalid command 'bdist_wheel', you must install the 'wheel' package first.

# see https://packaging.python.org/en/latest/distributing.html
# https://packaging.python.org/guides/


import sys

def err(*args, **kwargs):
    sys.stderr.write(*args, **kwargs)
    sys.stderr.write('\n')


try:
    from setuptools import setup, find_packages
except ImportError:
    err("CmLib requires setuptools for installation. (https://pythonhosted.org/an_example_pypi_project/setuptools.html)")
    err("You can download and install it simply from https://pypi.org/project/ez_setup/")
    sys.exit(1)


if sys.version_info < (2,7) or ((3,0) <= sys.version_info < (3, 5)):
    err("CmLib requires Python 2.7 and higher or 3.5 and higher. "
        "It might work with earlier versions but this has not been tested.")
    sys.exit(1)


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


# Don't require PyQt for two reasons. First users may use PySide2. Second, users may use Anaconda
# to install PyQt. Anaconda uses a different package name (pyqt) than pip (PyQt5) and the tools
# can't detect correctly if PyQt has been installed. This leads to trouble. See:
#   https://www.anaconda.com/using-pip-in-a-conda-environment/
#   https://github.com/ContinuumIO/anaconda-issues/issues/1554

install_requires = [
    #"PyQt5 >= 5.6.0", # Don't require PyQt. See comment above
    "numpy >= 1.11",
]


from os import listdir
catalog_dirs = ['data/{}/*'.format(path) for path in listdir('cmlib/data')]


#from cmlib.misc import __version__
import os.path

# Don't import __version__ from cmlib because this also tries to import PyQt, which
# can fail if PyQt is not installed.
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(MODULE_DIR, 'cmlib', 'version.txt')

with open(VERSION_FILE) as stream:
    __version__ = stream.readline().strip()

setup(
    name = 'cmlib',
    version = __version__,
    description = "Color Map Library with harmonized data from different catalogs. Includes PyQt selection widgets.",
    long_description = readme + '\n\n' + history,
    long_description_content_type = 'text/x-rst',
    author = "Pepijn Kenter",
    author_email = "titusjan@gmail.com",
    license = "BSD",
    url="https://github.com/titusjan/cmlib",
    packages = find_packages(exclude=('ingest',)),
    package_data = {'cmlib': ['version.txt', 'data/*'] + catalog_dirs},
    entry_points={'gui_scripts': ['cmlib_demo = cmlib.demo:main']},
    install_requires = install_requires,
    zip_safe = False,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
    ],
    keywords = 'color-maps',
    #test_suite='tests',
    #tests_require=test_requirements
)
