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
    from distutils import setup

def check_dependencies():
    install_requires = []

    try:
        import numpy
    except ImportError:
        install_requires.append('numpy')
    try:
        import matplotlib
    except ImportError:
        install_requires.append('matplotlib')
    try:
        import pandas
    except ImportError:
        install_requires.append('pandas')

if __name__ == "__main__":

    install_requires = check_dependencies()

    setup(
        name='shee',
        author='Andrea Spina',
        author_email='74598@studenti.unimore.it',
        version='0.1',
        description='A simple data visualization tool.',
        url='bla',
        license='uncommon',
        packages=['shee'],
        install_requires=install_requires,
        zip_safe=False)

