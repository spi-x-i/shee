#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

import pandas as pd

from shee.frames import DStatFrame


class DStatFrameTest(unittest.TestCase):

    testfilesdir = 'examples/'

    def test_dstat_frame_constructor(self):

        dir = os.path.abspath(self.testfilesdir)
        file_list = os.listdir(dir)

        if not len(file_list):
            print "Impossible start test: input test .csv files not exists in 'examples' directory"
            exit(-1)

        for fn in file_list:
            fullname = os.path.join(dir, fn)
            frame = DStatFrame(fullname, 'cpu')

            self.assertIsInstance(frame.df, pd.DataFrame)
