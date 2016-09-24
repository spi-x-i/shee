#!/usr/bin/env python
# -*- coding: utf-8 -*

import os
import time

from shee.web import WebObject
from shee.util import get_result_dir_name

from shee.frames import DStatAggregate
from shee.frames import DStatCompare
from shee.frames import DStatCpu
from shee.frames import DStatDisk
from shee.frames import DStatFrame
from shee.frames import DStatMemory
from shee.frames import DStatNetwork
from shee.frames import DStatReadColumnsException


def evaluate_file(filename, fullname):
    return os.path.isfile(fullname) and filename.startswith('dstat') and filename.endswith('.csv')


def total_cpu_evaluation(fullname, dirname, plot, grain=False, df=None):
    ds = DStatCpu(fullname, frame=df, grain=grain)

    cpudir = dirname + "/cpu"
    if not os.path.exists(cpudir):
        os.makedirs(cpudir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['usr', 'sys', 'idl'], plot=plot)


def single_cpu_evaluation(fullname, dirname, plot, cpunum=None, grain=False, df=None):
    n = cpunum if cpunum is not None else 1
    if cpunum is not None:
        try:
            ds = DStatCpu(fullname, cpu=n, grain=grain, frame=df)

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
                ds = DStatCpu(fullname, cpu=n, grain=grain, frame=df)

                ndir = dirname + "/cpu" + "/cpu" + str(n)
                if not os.path.exists(ndir):
                    os.makedirs(ndir)

                ds.plot_together(plot=plot)
                ds.subplot_all(plot=plot)
                ds.plot_stacked(columns=['usr', 'sys', 'idl'], plot=plot)
                n += 1
            except DStatReadColumnsException:
                break


def total_network_evaluation(fullname, dirname, plot, grain=False, df=None):
    ds = DStatNetwork(fullname, grain=grain, frame=df)

    netdir = dirname + "/network"
    if not os.path.exists(netdir):
        os.makedirs(netdir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['send', 'recv'], plot=plot)


def single_network_evaluation(fullname, dirname, plot, ethnum=None, grain=False, df=None):
    n = ethnum if ethnum is not None else 0
    if ethnum is not None:
        try:
            ds = DStatNetwork(fullname, eth=n, grain=grain, frame=df)

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
                ds = DStatNetwork(fullname, eth=n, grain=grain, frame=df)

                ndir = dirname + "/network" + "/eth" + str(n)
                if not os.path.exists(ndir):
                    os.makedirs(ndir)

                ds.plot_together(plot=plot)
                ds.subplot_all(plot=plot)
                ds.plot_stacked(columns=['send', 'recv'], plot=plot)
                n += 1
            except DStatReadColumnsException:
                break


def total_memory_evaluation(fullname, dirname, plot, grain=False, df=None):
    ds = DStatMemory(fullname, grain=grain, frame=df)

    memdir = dirname + "/memory"
    if not os.path.exists(memdir):
        os.makedirs(memdir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['used', 'buff', 'cach', 'free'], plot=plot)
    # no multiple memory device evaluation here


def total_disk_evaluation(fullname, dirname, plot, grain=False, df=None):
    ds = DStatDisk(fullname, grain=grain, frame=df)

    dskdir = dirname + "/disk"
    if not os.path.exists(dskdir):
        os.makedirs(dskdir)

    ds.plot_together(plot=plot)
    ds.subplot_all(plot=plot)
    ds.plot_stacked(columns=['read', 'writ'], plot=plot)


def single_disk_evaluation(fullname, dirname, plot, sdnum=None, grain=False, df=None):
    n = sdnum if sdnum is not None else 'a'
    if sdnum is not None:
        try:
            ds = DStatDisk(fullname, disk=n, grain=grain, frame=df)

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
                ds = DStatDisk(fullname, disk=n, grain=grain, frame=df)

                ndir = dirname + "/disk" + "/sd" + n
                if not os.path.exists(ndir):
                    os.makedirs(ndir)

                ds.plot_together(plot=plot)
                ds.subplot_all(plot=plot)
                ds.plot_stacked(columns=['read', 'writ'], plot=plot)
                n = chr(ord(n) + 1)
            except DStatReadColumnsException:
                break


def comparison_evaluation(fullname, dirname, columns, plot, grain=False, df=None):
    try:
        ds = DStatCompare(fullname, columns, grain=grain, frame=df)

        memdir = dirname + "/comparison"
        if not os.path.exists(memdir):
            os.makedirs(memdir)

        ds.subplot_all(columns, plot=plot, grain=grain)
    except DStatReadColumnsException as e:
        print "Wrong columns specified. " + e.message
        exit(-1)


def aggregating_evaluation(dir, save=False, filename="", plot=False, grain=False):

    file_list = os.listdir(dir)

    aggr_dir = dir + '/aggregation'
    if not os.path.exists(aggr_dir):
        os.makedirs(aggr_dir)

    if filename:  # a file name is given in input, initialize DStatAggregate object with given filename
        dfs = None
    else:
        dfs = []
        for fn in file_list:
            # from here the path has to be absolute
            fullname = os.path.join(dir, fn)
            if evaluate_file(fn, fullname):
                try:
                    df = DStatFrame(fullname, get_result_dir_name(fullname))
                    dfs.append(df)
                except DStatReadColumnsException as e:
                    print "Wrong columns specified. " + e.message
                    exit(-1)
    dagg = DStatAggregate(dir, aggr_dir, dfs, filename=filename, grain=grain)

    if save:
        dagg.to_csv()

    for k, v in dagg.get_dict().iteritems():
        dagg.plot_aggr(v, mod=k, plot=plot)
        dagg.plot_clean(v, mod=k, plot=plot)

    return dagg.get_date(), dagg.get_nodes_list()


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def aggregating_evaluation_benchmark(suite_dir, save=False, filename="", plot=False, grain=False):
    dagg_list = []
    items_max = dict()
    items_max['runtimeMax'] = -1

    dir_list = get_immediate_subdirectories(suite_dir)

    #calculate statistics
    for dir in dir_list:
        file_list = os.listdir(dir)

        aggr_dir = dir + '/aggregation_benchmark'
        if not os.path.exists(aggr_dir):
            os.makedirs(aggr_dir)

        if filename:  # a file name is given in input, initialize DStatAggregate object with given filename
            dfs = None
        else:
            dfs = []
            for fn in file_list:
                # from here the path has to be absolute
                fullname = os.path.join(dir, fn)
                if evaluate_file(fn, fullname):
                    try:
                        df = DStatFrame(fullname, get_result_dir_name(fullname))
                        dfs.append(df)
                    except DStatReadColumnsException as e:
                        print "Wrong columns specified. " + e.message
                        exit(-1)
        dagg = DStatAggregate(dir, aggr_dir, dfs, filename=filename, grain=grain)
        dagg_list.append(dagg)



        #check maxima
        for k, v in dagg.get_dict().iteritems():
            # check maximum runtime
            df = v
            start = df.index.values[0]
            end = df.index.values[-1]
            if (end - start > items_max['runtimeMax']):
                items_max['runtimeMax'] = end - start

            for column in list(v.columns.values):
                c = ""
                current_max = -1
                if (column[1] == ""):
                    c = column[0]
                    current_max = df[[c]].max(axis=0).max(axis=0)
                else:
                    c = column[2]
                    current_max = df.iloc[:, df.columns.get_level_values(2) == c].max(axis=0).max(axis=0)
                if c in items_max:
                    items_max[c] = current_max if current_max > items_max[c] else items_max[c]
                else:
                    items_max[c] = current_max

    #draw charts
    for dagg in dagg_list:
        if save:
            dagg.to_csv()

        for k, v in dagg.get_dict().iteritems():
            dagg.plot_aggr(v, mod=k, plot=plot)
            dagg.plot_clean(v, mod=k, plot=plot, maxima=items_max)



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
    :param noparse:
    :param aggregate:
    :param save_agg:
    :param file_agg:
    :return:
    """
    def evaluate_total_cpu():
        if cpu or web:
            return True
        elif (not memory and not network and
              not disk and processor is None and
              eth is None and sd is None and
              comparison is None):
            return True
        else:
            return False

    def evaluate_single_cpu():
        if processor is not None or web:
            return True
        elif (not memory and not network and
              not cpu and not disk and
              sd is None and eth is None and
              comparison is None):
            return True
        else:
            return False

    def evaluate_total_network():
        if network or web:
            return True
        elif (not memory and not cpu and
              not disk and eth is None and
              processor is None and sd is None and
              comparison is None):
            return True
        else:
            return False

    def evaluate_single_network():
        if eth is not None or web:
            return True
        elif (not memory and not network and
              not disk and not cpu and
              sd is None and processor is None and
              comparison is None):
            return True
        else:
            return False

    def evaluate_total_memory():
        if memory or web:
            return True
        elif (not cpu and not network and
              not disk and eth is None and
              processor is None and sd is None and
              comparison is None):
            return True
        else:
            return False

    def evaluate_total_disk():
        if disk or web:
            return True
        elif (not memory and not cpu and
              not network and eth is None and
              processor is None and sd is None and
              comparison is None):
            return True
        else:
            return False

    def evaluate_single_disk():
        if sd is not None or web:
            return True
        elif (not memory and not network and
              not cpu and not disk and
              processor is None and eth is None and
              comparison is None):
            return True
        else:
            return False

    print "Opening the following dstat files ..."

    if not os.path.exists(input_dir):
        print "Specified input directory doesn't exists"
        exit(-1)

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
                # dn = fullname.split('.')[0]
                # if not os.path.exists(dn):
                #     os.makedirs(dn)

                # get result allows also dotted absolute paths
                dn = get_result_dir_name(fullname)
                if not os.path.exists(dn):
                    os.makedirs(dn)

                frame = DStatFrame(fullname, 'base')

                if evaluate_total_cpu():
                    total_cpu_evaluation(fullname, dn, plot, grain, frame)
                if evaluate_single_cpu():
                    single_cpu_evaluation(fullname, dn, plot, processor, grain, frame)

                if evaluate_total_network():
                    total_network_evaluation(fullname, dn, plot, grain, frame)
                if evaluate_single_network():
                    single_network_evaluation(fullname, dn, plot, eth, grain, frame)

                if evaluate_total_memory():
                    total_memory_evaluation(fullname, dn, plot, grain, frame)

                if evaluate_total_disk():
                    total_disk_evaluation(fullname, dn, plot, grain, frame)

                if evaluate_single_disk():
                    single_disk_evaluation(fullname, dn, plot, sd, grain, frame)

                if comparison is not None:
                    comparison_evaluation(fullname, dn, columns=comparison, plot=plot, grain=grain, df=frame)

                print fn + " analysis completed.(Execution time: %s secs" % (time.time() - start_time) + ")"

            else:
                print "%s is a directory or a not parsable file" % fn

    date, nodes = None, None
    if aggregate or web:
        save = save_agg
        filename = file_agg if file_agg is not None else ''
        #date, nodes = aggregating_evaluation(input_dir, save=save, filename=filename, plot=plot, grain=grain)
        aggregating_evaluation_benchmark(input_dir, save=save, filename=filename, plot=plot, grain=grain)

    if web:
        web_obj = WebObject()
        if os.path.isabs(input_dir):
            work_dir = input_dir
            web_obj.set_dirname(work_dir + '/html')
            web_obj.set_pathtree(work_dir)
            if not os.path.exists(work_dir + '/html'):
                os.makedirs(work_dir + '/html')
        else:
            work_dir = os.getcwd() + '/' + '/'.join(input_dir.split('/'))
            web_obj.set_dirname(work_dir + '/html')
            web_obj.set_pathtree(work_dir)
            if not os.path.exists(work_dir + '/html'):
                os.makedirs(work_dir + '/html')
        web_obj.set_filename('mainpage')

        web_obj.page(agg_date=date, agg_nodes=nodes)
        exit(0)
