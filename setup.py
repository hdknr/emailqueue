#! /usr/bin/env python

NAME = 'emailqueue'
DESCRIPTION = 'Email Handler'
PACKAGES = ['emailqueue', ]

SITE = 'github.com'
USER = "hdknr"
PROJECT = NAME
URL = 'https://{0}/{1}/{2}'.format(SITE, USER, PROJECT)


def install():
    from setuptools import setup
    setup(
        license='Simplfied BSD License',
        author='Hideki Nara of LaFoaglia,Inc.',
        author_email='gmail [at] hdknr.com',
        maintainer='LaFoglia,Inc.',
        maintainer_email='gmail [at] hdknr.com',
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
        name=NAME,
        version=getattr(__import__(NAME), 'get_version')(),
        url=URL,
        description=DESCRIPTION,
        download_url=URL,
        package_dir={'': 'lib'},
        packages=PACKAGES,
        include_package_data=True,
        zip_safe=False,
        long_description=read('README.rst'),
        scripts=glob.glob('scripts/*.py'),
        install_requires=requires(),
        dependency_links=deps(),
    )

import sys
import os
import glob
import re

DEP = re.compile(r'-e\s+(.+)#egg=(.+)')
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'lib'))


def read(fname):
    return open(os.path.join(BASE_DIR, fname)).read()


def lines(fname):
    return [line.strip()
            for line in open(os.path.join(BASE_DIR, fname)).readlines()]


def deps(i=1):
    return [DEP.search(r).group(i) for r in lines("requirements/links.txt")]


def requires():
    return lines("requirements/install.txt") + deps(2)

if __name__ == '__main__':
    install()
