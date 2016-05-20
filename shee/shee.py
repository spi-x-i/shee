#!/usr/bin/env python
# -*- coding: utf-8 -*

import os

import time

from page import WebObject

from frames import DStatFrame
from frames import DStatCpu
from frames import DStatDisk
from frames import DStatMemory
from frames import DStatNetwork
from frames import DStatCompare
from frames import DStatAggregate

from frames import DStatReadColumnsException

DIR = "/home/andrea/TESI/PYTHON/shee-project/shee/examples"


def evaluate_file(filename, fullname):
    return os.path.isfile(fullname) and filename.startswith('dstat') and filename.endswith('.csv')


def total_cpu_evaluation(fullname, dirname, plot, grain=False):
    ds = DStatCpu(fullname, grain=grain)

    cpudir = dirname + "/cpu"
    if not os.path.exists(cpudir):
        os.makedirs(cpudir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['usr', 'sys', 'idl'], plot=plot)


def single_cpu_evaluation(fullname, dirname, plot, cpunum=None, grain=False):
    n = cpunum if cpunum is not None else 1
    if cpunum is not None:
        try:
            ds = DStatCpu(fullname, cpu=n, grain=grain)

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
                ds = DStatCpu(fullname, cpu=n, grain=grain)

                ndir = dirname + "/cpu" + "/cpu" + str(n)
                if not os.path.exists(ndir):
                    os.makedirs(ndir)

                ds.plot_together(plot=plot)
                ds.subplot_all(plot=plot)
                ds.plot_stacked(columns=['usr', 'sys', 'idl'], plot=plot)
                n += 1
            except DStatReadColumnsException:
                break


def total_network_evaluation(fullname, dirname, plot, grain=False):
    ds = DStatNetwork(fullname, grain=grain)

    netdir = dirname + "/network"
    if not os.path.exists(netdir):
        os.makedirs(netdir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['send', 'recv'], plot=plot)


def single_network_evaluation(fullname, dirname, plot, ethnum=None, grain=False):
    n = ethnum if ethnum is not None else 0
    if ethnum is not None:
        try:
            ds = DStatNetwork(fullname, eth=n, grain=grain)

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
                ds = DStatNetwork(fullname, eth=n, grain=grain)

                ndir = dirname + "/network" + "/eth" + str(n)
                if not os.path.exists(ndir):
                    os.makedirs(ndir)

                ds.plot_together(plot=plot)
                ds.subplot_all(plot=plot)
                ds.plot_stacked(columns=['send', 'recv'], plot=plot)
                n += 1
            except DStatReadColumnsException:
                break


def total_memory_evaluation(fullname, dirname, plot, grain=False):
    ds = DStatMemory(fullname, grain=grain)

    memdir = dirname + "/memory"
    if not os.path.exists(memdir):
        os.makedirs(memdir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['used', 'buff', 'cach', 'free'], plot=plot)
    # no multiple memory device evaluation here


def total_disk_evaluation(fullname, dirname, plot, grain=False):
    ds = DStatDisk(fullname, grain=grain)

    dskdir = dirname + "/disk"
    if not os.path.exists(dskdir):
        os.makedirs(dskdir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['read', 'writ'], plot=plot)


def single_disk_evaluation(fullname, dirname, plot, sdnum=None, grain=False):
    n = sdnum if sdnum is not None else 'a'
    if sdnum is not None:
        try:
            ds = DStatDisk(fullname, disk=n, grain=grain)

            ndir = dirname + "/disk" + "/sd" + n
            if not os.path.exists(ndir):
                os.makedirs(ndir)

            ds.plot_together(plot=plot)
            ds.subplot_all(plot=plot)
            ds.plot_stacked(columns=['read', 'writ'], plot=plot)
        except DStatReadColumnsException:
            print "Wrong eth number selected: %s" % n
    else:
        while True:
            try:
                ds = DStatDisk(fullname, disk=n, grain=grain)

                ndir = dirname + "/disk" + "/sd" + n
                if not os.path.exists(ndir):
                    os.makedirs(ndir)

                ds.plot_together(plot=plot)
                ds.subplot_all(plot=plot)
                ds.plot_stacked(columns=['read', 'writ'], plot=plot)
                n = chr(ord(n) + 1)
            except DStatReadColumnsException:
                break

def comparison_evaluation(fullname, dirname, columns, plot, grain=False):
    try:
        ds = DStatCompare(fullname, columns, grain=grain)

        memdir = dirname + "/comparison"
        if not os.path.exists(memdir):
            os.makedirs(memdir)

        ds.subplot_all(columns, plot=plot, grain=grain)
    except DStatReadColumnsException as e:
        print "Wrong columns specified. " + e.message
        exit(-1)


def aggregating(input_dir, save=False, file=""):

    dir = input_dir
    file_list = os.listdir(dir)
    if file:
        dagg = DStatAggregate(input_dir, filename=file)
        dagg.plot_stacked_avg()
    else:
        dfs = []
        for fn in file_list:
            # from here the path has to be absolute
            fullname = os.path.join(dir, fn)
            if evaluate_file(fn, fullname):
                try:
                    df = DStatFrame(fullname, fullname.split('.')[0])
                    dfs.append(df)
                except DStatReadColumnsException as e:
                    print "Wrong columns specified. " + e.message
                    exit(-1)
        dagg = DStatAggregate(input_dir, dfs, save=save)
        dagg.plot_stacked_avg()

def shee(input_dir, filename=None, processor=None, eth=None, sd=None, comparison=None, cpu=None, network=None,
         memory=None, disk=None, plot=False, grain=False, web=False, noparse=False, aggregate=False, save_agg=False,
         file_agg=None):
    """

    :param input_dir: input file directory - if not specified the working directory will be parsed
    :param filename: input file - if not specified each parsable file will be parsed
    :param processor: processor number - if specified only that processor will be parsed
    :param eth: network device number - if specified only that network device will be parsed
    :param sd:
    :param comparison: list of columns that has to be compared - if not specified not comparison will be produced
    :param cpu:
    :param network:
    :param memory:
    :param disk:
    :param plot:
    :param grain:
    :param web:
    :return:
    """

    def evaluate_total_cpu():
        if cpu or web:
            return True
        elif not memory and not network and not disk and processor is None and eth is None and sd is None and comparison is None:
            return True
        else:
            return False

    def evaluate_single_cpu():
        if processor is not None or web:
            return True
        elif not memory and not network and not cpu and not disk and sd is None and eth is None and comparison is None:
            return True
        else:
            return False

    def evaluate_total_network():
        if network or web:
            return True
        elif not memory and not cpu and not disk and eth is None and processor is None and sd is None and comparison is None:
            return True
        else:
            return False

    def evaluate_single_network():
        if eth is not None or web:
            return True
        elif not memory and not network and not disk and not cpu and sd is None and processor is None and comparison is None:
            return True
        else:
            return False

    def evaluate_total_memory():
        if memory or web:
            return True
        elif not cpu and not network and not disk and eth is None and processor is None and sd is None and comparison is None:
            return True
        else:
            return False

    def evaluate_total_disk():
        if disk or web:
            return True
        elif not memory and not cpu and not network and eth is None and processor is None and sd is None and comparison is None:
            return True
        else:
            return False

    def evaluate_single_disk():
        if sd is not None or web:
            return True
        elif not memory and not network and not cpu and not disk and processor is None and eth is None and comparison is None:
            return True
        else:
            return False

    web_obj = None
    if web:
        web_obj = WebObject()
        if os.path.isabs(input_dir):
            work_dir = input_dir
            web_obj.set_dirname(work_dir + '/html')
            web_obj.set_pathtree(work_dir)
            if not os.path.exists(work_dir + '/html'):
                os.makedirs(work_dir + '/html')
        else:
            work_dir = os.getcwd() + '/' + input_dir.split('/')[-2]
            web_obj.set_dirname(work_dir + '/html')
            web_obj.set_pathtree(work_dir)
            if not os.path.exists(work_dir + '/html'):
                os.makedirs(work_dir + '/html')
        web_obj.set_filename('mainpage')

    if not noparse:
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
                    total_cpu_evaluation(fullname, dn, plot, grain)
                if evaluate_single_cpu():
                    single_cpu_evaluation(fullname, dn, plot, processor, grain)

                if evaluate_total_network():
                    total_network_evaluation(fullname, dn, plot, grain)
                if evaluate_single_network():
                    single_network_evaluation(fullname, dn, plot, eth, grain)

                if evaluate_total_memory():
                    total_memory_evaluation(fullname, dn, plot, grain)

                if evaluate_total_disk():
                    total_disk_evaluation(fullname, dn, plot, grain)

                if evaluate_single_disk():
                    single_disk_evaluation(fullname, dn, plot, sd, grain)

                if comparison is not None:
                    comparison_evaluation(fullname, dn, columns=comparison, plot=plot, grain=grain)

                print fn + " analysis completed.(Execution time: %s secs" % (time.time() - start_time) + ")"

            else:
                print "%s is a directory or a not parsable file" % fn
    if web:
        web_obj.page()
        exit(0)

    if aggregate:
        if save_agg:
            aggregating(input_dir, save=True)
        elif file_agg is not None:
            aggregating(input_dir, file=file_agg)
        else:
            aggregating(input_dir)

