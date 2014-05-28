#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#  This file is part of "emailqeueue"
#
#  Copyright 2014 LaFoglia
#
#  Licensed under the Simplified BSD License;
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.freebsd.org/copyright/freebsd-license.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  NOTES
#
#  Create source distribution tarball:
#    python setup.py sdist --formats=gztar
#
#  Create binary distribution rpm:
#    python setup.py bdist --formats=rpm
#
#  Create binary distribution rpm with being able to change an option:
#    python setup.py bdist_rpm --release 7
#
#  Test installation:
#    python setup.py install --prefix=/usr --root=/tmp
#
#  Install:
#    python setup.py install
#  Or:
#    python setup.py install --prefix=/usr
#

######################################################
NAME = 'emailqeueue'
USER = 'hdknr'
DESCRIPTION = 'Email Handler'
PACKAGES = ['emailqueue', ]
VERSION = "0.1"
LICENSE = 'Simplfied BSD License'
AUTHOR = 'Hideki Nara of LaFoaglia,Inc.'
AUTHOR_EMAIL = 'gmail [at] hdknr.com'
MAINTAINER = AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL
URL = 'https://github.com/%s/%s' % (USER, NAME)
######################################################
import os
import glob
from setuptools import setup

SCRIPTS = glob.glob('scripts/*.py')


def read(fname):
    """Utility function to read the README file."""
    with open(os.path.join(os.path.dirname(__file__), fname)) as data:
        return data.read()
    return ""

try:
    INSTALL_REQUIRES = [
        r for r in
        read('requirements.txt').split('\n')
        if len(r) > 0 and not r.startswith('-e')
    ]
except:
    INSTALL_REQUIRES = []


if __name__ == '__main__':
    setup(
        name=NAME,
        version=VERSION,
        license=LICENSE,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        url=URL,
        description=DESCRIPTION,
        long_description=read('README.rst'),
        download_url=URL,
        platforms=['any'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Library',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Simplifed BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
        ],
        package_dir={'': 'lib'},
        packages=PACKAGES,
        include_package_data=True,
        zip_safe=False,
        scripts=SCRIPTS,
    )
