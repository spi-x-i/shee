#!/usr/bin/env python
# -*- coding: utf-8 -*

import os

import sys
import warnings

from parse import SheeParser

from shee import shee


def main(args=None):
    """
    :param args: void
    :return:
    """
    if args is None:
        args = sys.argv[1:]

    warnings.filterwarnings("ignore")
    # argument parsing
    parser = SheeParser()
    args = parser.get_args()

    # arguments validating
    input_dir = os.path.abspath(args.input) if args.input is not None else os.getcwd()
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
