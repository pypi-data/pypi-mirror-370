#! /usr/bin/env python3
# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2025 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

#
# Memorandum:
#
# Install from sources:
#     git clone https://github.com/oasys-esrf-kit/OASYS1-XRT
#     cd OASYS1-XRT
#     python -m pip install -e . --no-deps --no-binary :all:
#
# Upload to pypi (when uploading, increment the version number):
#     python setup.py register (only once, not longer needed)
#     python setup.py sdist
#     python -m twine upload dist/...
#
# Install from pypi:
#     pip install OASYS1-XRT
#

import os

try:
    from setuptools import find_packages, setup
except AttributeError:
    from setuptools import find_packages, setup

NAME = 'OASYS1-XRT'
VERSION = '0.0.01'
ISRELEASED = False

DESCRIPTION = 'XRT'
README_FILE = os.path.join(os.path.dirname(__file__), 'README.md')
LONG_DESCRIPTION = open(README_FILE).read()
AUTHOR = 'Manuel Sanchez del Rio'
AUTHOR_EMAIL = 'srio@esrf.eu'
URL = 'https://github.com/oasys-esrf-kit/OASYS1-XRT'
DOWNLOAD_URL = 'https://github.com/oasys-esrf-kit/OASYS1-XRT'
LICENSE = 'MIT'

KEYWORDS = (
    'simulator',
    'oasys1',
)

CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Console',
    'Environment :: Plugins',
    'Programming Language :: Python :: 3',
    'Intended Audience :: Science/Research',
)

SETUP_REQUIRES = (
    'setuptools',
)

INSTALL_REQUIRES = (
    'oasys1>=1.2.131',
    'syned-gui>=1.0.3',
    'xrt',
)

PACKAGES = find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests'))

PACKAGE_DATA = {
    "orangecontrib.xrt.widgets.sources":["icons/*.png", "icons/*.jpg"],
    "orangecontrib.xrt.widgets.beamline_elements":["icons/*.png", "icons/*.jpg"],
    "orangecontrib.xrt.widgets.tools":["icons/*.png", "icons/*.jpg", "misc/*.png"],
}

NAMESPACE_PACAKGES = ["orangecontrib", "orangecontrib.xrt", "orangecontrib.xrt.widgets"]

ENTRY_POINTS = {
    'oasys.addons' : ("xrt = orangecontrib.xrt", ),
    'oasys.widgets' : (
        "XRT Light Sources = orangecontrib.xrt.widgets.light_sources",
        "XRT Optical Elements = orangecontrib.xrt.widgets.beamline_elements",
        "XRT Tools = orangecontrib.xrt.widgets.tools",
    ),
}

if __name__ == '__main__':
    try:
        import PyMca5, PyQt4

        raise NotImplementedError("This package doesn't work with Oasys1 beta.\nPlease install OASYS1 final release: http://www.elettra.eu/oasys.html")
    except:
        setup(
              name = NAME,
              version = VERSION,
              description = DESCRIPTION,
              long_description = LONG_DESCRIPTION,
              author = AUTHOR,
              author_email = AUTHOR_EMAIL,
              url = URL,
              download_url = DOWNLOAD_URL,
              license = LICENSE,
              keywords = KEYWORDS,
              classifiers = CLASSIFIERS,
              packages = PACKAGES,
              package_data = PACKAGE_DATA,
              setup_requires = SETUP_REQUIRES,
              install_requires = INSTALL_REQUIRES,
              entry_points = ENTRY_POINTS,
              namespace_packages=NAMESPACE_PACAKGES,
              include_package_data = True,
              zip_safe = False,
              )
