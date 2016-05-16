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
    parser.add_argument("-e", "--eth", help="Get network eth number to parse", type=int)
    parser.add_argument("-f", "--file", help="File to parse", type=str)
    parser.add_argument("-i", "--input", help="Directory to parse", type=str)
    parser.add_argument("-m", "--memory", help="If specified, only memory column is evaluated", action="store_true")
    parser.add_argument("-n", "--network", help="If specified, only total network column is evaluated", action="store_true")
    parser.add_argument("-p", "--processor", help="Get processor number to parse", type=int)
    parser.add_argument("-P", "--plot", help="If specified, charts will be plotted with matplotlib GUI (not saved)", action="store_true")
    parser.add_argument("-u", "--cpu", help="If specified, only total cpu column is evaluated", action="store_true")

    args = parser.parse_args()

    # arguments validating
    input_dir = args.input if args.input is not None else os.getcwd()
    filename = args.file.split("/")[-1] if args.file is not None else None
    processor = args.processor if args.processor is not None else None
    eth = args.eth if args.eth is not None else None
    comparison = args.comparison if args.comparison is not None else None
    if comparison is not None :
        if len(comparison) < 2:
            print "Comparison list should contains at least two elements"
            exit(-1)
        if len(comparison) > 3:
            print "Comparison columns list should contains up to three elements"
            exit(-1)
    memory = args.memory
    network = args.network
    cpu = args.cpu
    plot = args.plot

    shee(input_dir, filename, processor, eth, comparison, cpu, network, memory, plot)

if __name__ == "__main__":
    main()
