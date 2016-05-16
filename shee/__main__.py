#!/usr/bin/env python
# -*- coding: utf-8 -*

import os

import sys
import time
import argparse

from DStatFrame import DStatCpu
from DStatFrame import DStatMemory
from DStatFrame import DStatNetwork
from DStatFrame import DStatCompare

from DStatFrame import DStatReadColumnsException

DIR = "/home/andrea/TESI/PYTHON/shee-project/shee/examples"


def evaluate_file(filename, fullname):
    return os.path.isfile(fullname) and filename.startswith('dstat') and filename.endswith('.csv')


def total_cpu_evaluation(fullname, dirname):
    ds = DStatCpu(fullname)

    cpudir = dirname + "/cpu"
    if not os.path.exists(cpudir):
        os.makedirs(cpudir)

    ds.plot_together()
    ds.subplot_all(True)
    ds.plot_stacked(columns=['usr', 'sys', 'idl'])


def single_cpu_evaluation(fullname, dirname, cpunum=None):
    n = cpunum if cpunum is not None else 1
    if cpunum is not None:
        ndir = dirname + "/cpu" + "/cpu" + str(n)
        if not os.path.exists(ndir):
            os.makedirs(ndir)
        try:
            ds = DStatCpu(fullname, cpu=n)
            ds.plot_together()
            ds.subplot_all(True)
            ds.plot_stacked(columns=['usr', 'sys', 'idl'])
        except DStatReadColumnsException:
            print "Wrong cpu core number selected: %s".format(str(n))
    else:
        while True:
            # if cpu number is specified, evaluating only that cpu, elsewhere evaluating all cpus
            ndir = dirname + "/cpu" + "/cpu" + str(n)
            if not os.path.exists(ndir):
                os.makedirs(ndir)
            try:
                ds = DStatCpu(fullname, cpu=n)
                ds.plot_together()
                ds.subplot_all(True)
                ds.plot_stacked(columns=['usr', 'sys', 'idl'])
                n += 1
            except DStatReadColumnsException:
                break


def total_network_evaluation(fullname, dirname):
    ds = DStatNetwork(fullname)

    netdir = dirname + "/network"
    if not os.path.exists(netdir):
        os.makedirs(netdir)

    ds.plot_together()
    ds.subplot_all()
    ds.plot_stacked(columns=['send', 'recv'])


def single_network_evaluation(fullname, dirname, ethnum=None):
    n = ethnum if ethnum is not None else 1
    if ethnum is not None:
        ndir = dirname + "/eth" + str(n)
        if not os.path.exists(ndir):
            os.makedirs(ndir)
        try:
            ds = DStatNetwork(fullname, eth=n)
            ds.plot_together()
            ds.subplot_all()
            ds.plot_stacked(columns=['send', 'recv'])
        except DStatReadColumnsException:
            print "Wrong cpu core number selected: %s".format(str(n))
    else:
        while True:
            ndir = dirname + "/eth" + str(n)
            if not os.path.exists(ndir):
                os.makedirs(ndir)
            try:
                ds = DStatNetwork(fullname, eth=n)
                ds.plot_together()
                ds.subplot_all()
                ds.plot_stacked(columns=['send', 'recv'])
                n += 1
            except DStatReadColumnsException:
                print "Wrong eth number selected: %s".format(str(n))
                break


def total_memory_evaluation(fullname, dirname):
    ds = DStatMemory(fullname)

    memdir = dirname + "/memory"
    if not os.path.exists(memdir):
        os.makedirs(memdir)

    ds.plot_together()
    ds.subplot_all()
    ds.plot_stacked(columns=['used', 'buff', 'cach', 'free'], plot=False)
    # no multiple memory device evaluation here


def comparison_evaluation(fullname, dirname, columns):
    try:
        ds = DStatCompare(fullname, columns)

        memdir = dirname + "/comparison"
        if not os.path.exists(memdir):
            os.makedirs(memdir)

        ds.subplot_all(['total cpu usage', 'net/total', 'memory usage'])
    except DStatReadColumnsException as e:
        print "Wrong columns specified: " + e.message
        exit(-1)


def shee(input_dir, filename=None, processor=None, eth=None, comparison=None, cpu=None, network=None, memory=None):
    """

    :param input_dir: input file directory - if not specified the working directory will be parsed
    :param filename: input file - if not specified each parsable file will be parsed
    :param processor: processor number - if specified only that processor will be parsed
    :param eth: network device number - if specified only that network device will be parsed
    :param comparison: list of columns that has to be compared - if not specified not comparison will be produced
    :param cpu:
    :param network:
    :param memory:
    :return:
    """

    def evaluate_total_cpu():
        if cpu is not None:
            return True
        elif memory is None and network is None and processor is None:
            return True
        else:
            return False

    def evaluate_single_cpu():
        if processor is not None:
            return True
        elif memory is None and network is None and cpu is None and processor is not None:
            return True
        else:
            return False

    def evaluate_total_network():
        if network is not None:
            return True
        elif memory is None and cpu is None and eth is None:
            return True
        else:
            return False

    def evaluate_single_network():
        if eth is not None:
            return True
        elif memory is None and network is None and cpu is None and eth is not None:
            return True
        else:
            return False

    def evaluate_total_memory():
        if memory is not None:
            return True
        elif cpu is None and network is None:
            return True
        else:
            return False

    # for each .csv file inside the directory computing the evaluation
    dir = input_dir
    file_list = os.listdir(dir)
    if filename is not None:  # one filename evaluation
        file_list = list(set(file_list) & set(list(filename)))
        if not len(file_list):
            print "Specified file not exists"
            exit(-1)
    for fn in os.listdir(dir):
        # from here the path has to be absolute
        fullname = os.path.join(dir, fn)
        if evaluate_file(fn, fullname):

            start_time = time.time()
            print "Evaluating : " + fullname

            # create results directory
            dn = fullname.split('.')[0]
            if not os.path.exists(dn):
                os.makedirs(dn)

            if evaluate_total_cpu():
                total_cpu_evaluation(fullname, dn)
            if evaluate_single_cpu():
                single_cpu_evaluation(fullname, dn, processor)

            if evaluate_total_network():
                total_network_evaluation(fullname, dn)
            if evaluate_single_network():
                single_network_evaluation(fullname, dn, eth)

            if evaluate_total_memory():
                total_memory_evaluation(fullname, dn)

            comparison_evaluation(fullname, dn, columns=['total cpu usage', 'net/total', 'memory usage'])

            print fn + " analysis completed.(Execution time: %s secs" % (time.time() - start_time) + ")"

        else:
            print "%s is a directory or a not parsable file" % fn


def main(args=None):
    """
    The tool must provide following functions:
    when run, like shee, il tool parsa tutti i file .csv della directory corrente, crea una directory out e salva i
    grafici all'interno della stessa cartella
    :return:
    """
    if args is None:
        args = sys.argv[1:]

    # qualcosa tipo if not newdir
    dir = DIR

    # argument parsing
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--comparison", help="Get columns that has to be compared (usage: -c col1" +
                                                   " -c col2)", action='append')
    parser.add_argument("-e", "--eth", help="Get network eth number that has to be parsed", type=int)
    parser.add_argument("-f", "--file", help="File that has to be parsed", type=str)
    parser.add_argument("-i", "--input", help="Directory that has to be parsed", type=str)
    parser.add_argument("-m", "--memory", help="If specified, only memory column is evaluated", action="store_true")
    parser.add_argument("-n", "--network", help="If specified, only total network column is evaluated", action="store_true")
    parser.add_argument("-p", "--processor", help="Get processor number that has to be parsed", type=int)
    parser.add_argument("-u", "--cpu", help="If specified, only total cpu column is evaluated", action="store_true")

    args = parser.parse_args()

    input_dir = args.input if args.input is not None else os.getcwd()
    filename = args.file if args.file is not None else None
    processor = args.processor if args.processor is not None else None
    eth = args.eth if args.eth is not None else None
    comparison = args.comparison if args.comparison is not None else None
    if len(comparison) < 2:
        print "Comparison list should contains at least two elements"
        exit(-1)
    memory = args.memory if args.memory is not None else None
    network = args.network if args.network is not None else None
    cpu = args.cpu if args.cpu is not None else None

    shee(input_dir, filename, processor, eth, comparison, cpu, network, memory)

if __name__ == "__main__":
    main()
