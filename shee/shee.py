#!/usr/bin/env python
# -*- coding: utf-8 -*

import os

import time

from DStatFrame import DStatCpu
from DStatFrame import DStatMemory
from DStatFrame import DStatNetwork
from DStatFrame import DStatCompare

from DStatFrame import DStatReadColumnsException

DIR = "/home/andrea/TESI/PYTHON/shee-project/shee/examples"


def evaluate_file(filename, fullname):
    return os.path.isfile(fullname) and filename.startswith('dstat') and filename.endswith('.csv')


def total_cpu_evaluation(fullname, dirname, plot):
    ds = DStatCpu(fullname)

    cpudir = dirname + "/cpu"
    if not os.path.exists(cpudir):
        os.makedirs(cpudir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['usr', 'sys', 'idl'], plot=plot)


def single_cpu_evaluation(fullname, dirname, plot, cpunum=None):
    n = cpunum if cpunum is not None else 1
    if cpunum is not None:
        try:
            ds = DStatCpu(fullname, cpu=n)

            ndir = dirname + "/cpu" + "/cpu" + str(n)
            if not os.path.exists(ndir):
                os.makedirs(ndir)

            ds.plot_together(plot=plot)
            ds.subplot_all(plot=plot)
            ds.plot_stacked(columns=['usr', 'sys', 'idl'], plot=plot)
        except DStatReadColumnsException:
            print "Wrong cpu core number selected: %s" % str(n)
    else:
        while True:
            # if cpu number is specified, evaluating only that cpu, elsewhere evaluating all cpus
            try:
                ds = DStatCpu(fullname, cpu=n)

                ndir = dirname + "/cpu" + "/cpu" + str(n)
                if not os.path.exists(ndir):
                    os.makedirs(ndir)

                ds.plot_together(plot=plot)
                ds.subplot_all(plot=plot)
                ds.plot_stacked(columns=['usr', 'sys', 'idl'], plot=plot)
                n += 1
            except DStatReadColumnsException:
                break


def total_network_evaluation(fullname, dirname, plot):
    ds = DStatNetwork(fullname)

    netdir = dirname + "/network"
    if not os.path.exists(netdir):
        os.makedirs(netdir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['send', 'recv'], plot=plot)


def single_network_evaluation(fullname, dirname, plot, ethnum=None):
    n = ethnum if ethnum is not None else 0
    if ethnum is not None:
        try:
            ds = DStatNetwork(fullname, eth=n)

            ndir = dirname + "/network" + "/eth" + str(n)
            if not os.path.exists(ndir):
                os.makedirs(ndir)

            ds.plot_together(plot=plot)
            ds.subplot_all(plot=plot)
            ds.plot_stacked(columns=['send', 'recv'], plot=plot)
        except DStatReadColumnsException:
            print "Wrong eth number selected: %s" % str(n)
    else:
        while True:
            try:
                ds = DStatNetwork(fullname, eth=n)

                ndir = dirname + "/network" + "/eth" + str(n)
                if not os.path.exists(ndir):
                    os.makedirs(ndir)

                ds.plot_together(plot=plot)
                ds.subplot_all(plot=plot)
                ds.plot_stacked(columns=['send', 'recv'], plot=plot)
                n += 1
            except DStatReadColumnsException:
                break


def total_memory_evaluation(fullname, dirname, plot):
    ds = DStatMemory(fullname)

    memdir = dirname + "/memory"
    if not os.path.exists(memdir):
        os.makedirs(memdir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['used', 'buff', 'cach', 'free'], plot=plot)
    # no multiple memory device evaluation here


def comparison_evaluation(fullname, dirname, columns, plot):
    try:
        ds = DStatCompare(fullname, columns)

        memdir = dirname + "/comparison"
        if not os.path.exists(memdir):
            os.makedirs(memdir)

        ds.subplot_all(columns, plot=plot)
    except DStatReadColumnsException as e:
        print "Wrong columns specified. " + e.message
        exit(-1)


def shee(input_dir, filename=None, processor=None, eth=None, comparison=None, cpu=None, network=None, memory=None, plot=False):
    """

    :param input_dir: input file directory - if not specified the working directory will be parsed
    :param filename: input file - if not specified each parsable file will be parsed
    :param processor: processor number - if specified only that processor will be parsed
    :param eth: network device number - if specified only that network device will be parsed
    :param comparison: list of columns that has to be compared - if not specified not comparison will be produced
    :param cpu:
    :param network:
    :param memory:
    :param plot:
    :return:
    """

    def evaluate_total_cpu():
        if cpu:
            return True
        elif not memory and not network and processor is None and eth is None and comparison is None:
            return True
        else:
            return False

    def evaluate_single_cpu():
        if processor is not None:
            return True
        elif not memory and not network and not cpu and eth is None and comparison is None:
            return True
        else:
            return False

    def evaluate_total_network():
        if network:
            return True
        elif not memory and not cpu and eth is None and processor is None and comparison is None:
            return True
        else:
            return False

    def evaluate_single_network():
        if eth is not None:
            return True
        elif not memory and not network and not cpu and processor is None and comparison is None:
            return True
        else:
            return False

    def evaluate_total_memory():
        if memory:
            return True
        elif not cpu and not network and eth is None and processor is None and comparison is None:
            return True
        else:
            return False

    # for each .csv file inside the directory computing the evaluation
    dir = input_dir
    file_list = os.listdir(dir)
    if filename is not None:  # one filename evaluation
        filename_list = [filename]
        file_list = list(set(file_list) & set(filename_list))
        if not len(file_list):
            print "Specified file not exists"
            exit(-1)
    for fn in file_list:
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
                total_cpu_evaluation(fullname, dn, plot)
            if evaluate_single_cpu():
                single_cpu_evaluation(fullname, dn, plot, processor)

            if evaluate_total_network():
                total_network_evaluation(fullname, dn, plot)
            if evaluate_single_network():
                single_network_evaluation(fullname, dn, plot, eth)

            if evaluate_total_memory():
                total_memory_evaluation(fullname, dn, plot)

            if comparison is not None:
                comparison_evaluation(fullname, dn, columns=comparison, plot=plot)

            print fn + " analysis completed.(Execution time: %s secs" % (time.time() - start_time) + ")"

        else:
            print "%s is a directory or a not parsable file" % fn


