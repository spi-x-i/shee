#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse


class SheeParser(object):

    HELPS = {
        'comparison': 'Get columns to compare (usage: -c col1" + " -c col2)',
        'file': 'File to parse',
        'input': 'Directory to parse',
        'noparse': 'If specified, no parsing will be done (only with -w option)',
        'memory': 'If specified, only memory column is evaluated',
        'network': 'If specified, only total network column is evaluated',
        'cpu': 'If specified, only total cpu column is evaluated',
        'disk': 'If specified, only total disk column is evaluated',
        'processor': 'Get processor number to parse',
        'eth': 'Get network eth number to parse',
        'sd': 'Get disk sd letter to parse (should be a string)',
        'plot': 'If specified, charts will be plotted with matplotlib GUI (not saved)',
        'time': 'If specified, a time interval will be requested',
        'web': 'If specified, an html page will be rendered',
        'aggregate': 'If specified, aggregated results will be computed',
        'comparable': 'If specified, all charts for all experiments will have the same metrics',
        'save_agg': 'Stores new .csv files with global aggregated results (one per metric)',
        'file_agg': 'Searches FILE_AGG file in the working directory and computes evaluation',
    }

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
        self.parser.add_argument("-c", "--comparison",  help=self.HELPS['comparison'],  action='append')
        self.parser.add_argument("-f", "--file",        help=self.HELPS['file'],        type=str)
        self.parser.add_argument("-i", "--input",       help=self.HELPS['input'],       type=str)
        self.parser.add_argument("-O", "--noparse",     help=self.HELPS['noparse'],     action='store_true')

        self.parser.add_argument("-m", "--memory",      help=self.HELPS['memory'],      action="store_true")
        self.parser.add_argument("-n", "--network",     help=self.HELPS['network'],     action="store_true")
        self.parser.add_argument("-u", "--cpu",         help=self.HELPS['cpu'],         action="store_true")
        self.parser.add_argument("-d", "--disk",        help=self.HELPS['disk'],        action="store_true")

        self.parser.add_argument("-p", "--processor",   help=self.HELPS['processor'],   type=int)
        self.parser.add_argument("-e", "--eth",         help=self.HELPS['eth'],         type=int)
        self.parser.add_argument("-D", "--sd",          help=self.HELPS['sd'],          type=str)

        self.parser.add_argument("-P", "--plot",        help=self.HELPS['plot'],        action="store_true")
        self.parser.add_argument("-T", "--time",        help=self.HELPS['time'],        action="store_true")
        self.parser.add_argument("-w", "--web",         help=self.HELPS['web'],         action="store_true")

        self.parser.add_argument("-a", "--aggregate",   help=self.HELPS['aggregate'],   action="store_true")
        self.parser.add_argument("-cmp", "--comparable",help=self.HELPS['comparable'],   action="store_true")
        self.parser.add_argument("-s", "--save_agg",    help=self.HELPS['save_agg'],    action="store_true")
        self.parser.add_argument("-F", "--file_agg",    help=self.HELPS['file_agg'],    type=str)

        return self.parser.parse_args()
