#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse


class SheeParser(object):
    def __init__(self):
            self.parser = argparse.ArgumentParser()

    def get_args(self):
        """
        Arguments parsing:
        comparison -> if not given returns empty-list
        file -> if not given returns None
        input -> if not given returns None
        noparse -> if not given returns False

        memory -> if not given returns False
        network -> if not given returns False
        cpu -> if not given returns False
        disk -> if not given returns False

        processor -> if not given returns None
        eth -> if not given returns None
        sd -> if not given returns None

        plot -> if not given returns False
        time -> if not given returns False
        web -> if not given returns False

        aggregate -> if not given returns False
        save_agg -> if not given returns False
        file_agg -> if not given returns None
        :return:
        """
        self.parser.add_argument("-c", "--comparison", help="Get columns to compare (usage: -c col1" + " -c col2)", action='append')
        self.parser.add_argument("-f", "--file", help="File to parse", type=str)
        self.parser.add_argument("-i", "--input", help="Directory to parse", type=str)
        self.parser.add_argument("-O", "--noparse", help="If specified, no parsing will be done (only with -w option)", action='store_true')

        self.parser.add_argument("-m", "--memory", help="If specified, only memory column is evaluated", action="store_true")
        self.parser.add_argument("-n", "--network", help="If specified, only total network column is evaluated", action="store_true")
        self.parser.add_argument("-u", "--cpu", help="If specified, only total cpu column is evaluated", action="store_true")
        self.parser.add_argument("-d", "--disk", help="If specified, only total disk column is evaluated", action="store_true")

        self.parser.add_argument("-p", "--processor", help="Get processor number to parse", type=int)
        self.parser.add_argument("-e", "--eth", help="Get network eth number to parse", type=int)
        self.parser.add_argument("-D", "--sd", help="Get disk sd letter to parse (should be a string)", type=str)

        self.parser.add_argument("-P", "--plot", help="If specified, charts will be plotted with matplotlib GUI (not saved)", action="store_true")
        self.parser.add_argument("-T", "--time", help="If specified, a time interval will be requested", action="store_true")
        self.parser.add_argument("-w", "--web", help="If specified, an html page will be rendered", action="store_true")

        self.parser.add_argument("-a", "--aggregate", help="If specified, aggregated results will be computed", action="store_true")
        self.parser.add_argument("-s", "--save_agg", help="Stores a new .csv file with global aggregated results", action="store_true")
        self.parser.add_argument("-F", "--file_agg", help="Searches FILE_AGG file in the working directory and computes evaluation", type=str)

        return self.parser.parse_args()
