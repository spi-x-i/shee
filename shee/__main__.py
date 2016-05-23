#!/usr/bin/env python
# -*- coding: utf-8 -*

import os

import sys
import warnings
import argparse

from shee import shee

def main(args=None):

    if args is None:
        args = sys.argv[1:]

    warnings.filterwarnings("ignore")

    # argument parsing
    parser = argparse.ArgumentParser()

    # input -> if not given returns None
    # cpu -> if not given returns False
    # file -> if not given returns None
    # plot -> if not given returns False
    # memory -> if not given returns False
    # network -> if not given returns False
    # processor -> if not given returns None
    # eth -> if not given returns None

    parser.add_argument("-c", "--comparison", help="Get columns to compare (usage: -c col1" + " -c col2)", action='append')
    parser.add_argument("-f", "--file", help="File to parse", type=str)
    parser.add_argument("-i", "--input", help="Directory to parse", type=str)
    parser.add_argument("-O", "--noparse", help="If specified, no parsing will be done (only with -w option)", action='store_true')

    parser.add_argument("-m", "--memory", help="If specified, only memory column is evaluated", action="store_true")
    parser.add_argument("-n", "--network", help="If specified, only total network column is evaluated", action="store_true")
    parser.add_argument("-u", "--cpu", help="If specified, only total cpu column is evaluated", action="store_true")
    parser.add_argument("-d", "--disk", help="If specified, only total disk column is evaluated", action="store_true")

    parser.add_argument("-p", "--processor", help="Get processor number to parse", type=int)
    parser.add_argument("-e", "--eth", help="Get network eth number to parse", type=int)
    parser.add_argument("-D", "--sd", help="Get disk sd letter to parse (should be a string)", type=str)

    parser.add_argument("-P", "--plot", help="If specified, charts will be plotted with matplotlib GUI (not saved)", action="store_true")
    parser.add_argument("-T", "--time", help="If specified, a time interval will be requested", action="store_true")
    parser.add_argument("-w", "--web", help="If specified, an html page will be rendered", action="store_true")

    parser.add_argument("-a", "--aggregate", help="If specified, aggregated results will be computed", action="store_true")
    parser.add_argument("-s", "--save_agg", help="Stores a new .csv file with global aggregated results", action="store_true")
    parser.add_argument("-F", "--file_agg", help="Searches FILE_AGG file in the working directory and computes evaluation", type=str)

    args = parser.parse_args()

    # arguments validating
    input_dir = args.input if args.input is not None else os.getcwd()
    filename = args.file.split("/")[-1] if args.file is not None else None
    comparison = args.comparison if args.comparison is not None else None
    if comparison is not None :
        if len(comparison) < 2:
            print "Comparison list should contains at least two elements"
            exit(-1)
        if len(comparison) > 3:
            print "Comparison columns list should contains up to three elements"
            exit(-1)

    processor = args.processor if args.processor is not None else None
    eth = args.eth if args.eth is not None else None
    sd = args.sd if args.sd is not None else None

    memory = args.memory
    network = args.network
    cpu = args.cpu
    disk = args.disk

    plot = args.plot
    time = args.time
    web = args.web

    aggregate = args.aggregate
    save_agg = args.save_agg
    file_agg = args.file_agg

    if (save_agg or file_agg is not None) and not aggregate:
        print " %s option allowed only with -a option" % ("-s [--save_agg]" if save_agg else "-F [--file_agg]")

    if (args.noparse) and (not web and not aggregate):
        print " -O [--noparse] option allowed only with -w option"
        exit(-1)
    noparse = args.noparse

    shee(input_dir, filename, processor, eth, sd, comparison, cpu, network, memory,
         disk, plot, time, web, noparse, aggregate, save_agg, file_agg)

if __name__ == "__main__":
    main()
