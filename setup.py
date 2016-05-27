#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

#
# shee: a simple data visualization tool
#
# setup.py code is inspired by Michael Waskom code
# https://github.com/mwaskom/seaborn
#

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def check_dependencies():
    install_requires = []

    try:
        import numpy
    except ImportError:
        install_requires.append('numpy>=1.11')
    try:
        import matplotlib
    except ImportError:
        install_requires.append('matplotlib>=1.3.1')
    try:
        import pandas
    except ImportError:
        install_requires.append('pandas>=0.18')

    return install_requires

if __name__ == "__main__":

    install_requires = check_dependencies()

    setup(
        name='shee',
        author='Andrea Spina',
        author_email='74598@studenti.unimore.it',
        version='0.1',
        description='A simple data visualization tool.',
        url='https://gitlab.tubit.tu-berlin.de/andrea-spina/shee',
        license='uncommon',
        packages=['shee', 'shee.frames', 'shee.parse'],
        install_requires=install_requires,
        entry_points={
          'console_scripts': [
              'shee = shee.__main__:main'
          ]
        },
        zip_safe=False)

