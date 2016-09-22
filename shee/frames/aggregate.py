#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import datetime

import numpy as np
import pandas as pd

import matplotlib.dates as mdates
import matplotlib.ticker as tick
import matplotlib.pyplot as plt

from frame import DStatException
from frame import DStatOpenCsvException
from frame import DStatReadColumnsException


class DStatAggregateNoValidExperiments(DStatException):
    """
    Raised when pandas.read_csv fails
    """
    pass


class DStatAggregate(object):

    COLORS = [
                '#FFC107',
                '#3F51B5'
                #'#F44336',
                #'#4CAF50',
            ]

    def __init__(self, input_dir, output_dir, dfs=None, filename="", grain=False):
        """
        The init function here should provide there ordered steps:
            - select overlapped dfs and save those in one aggregating dfs dictionary - keyed by following columns:
                . total cpu usage
                . net/total
                . memory usage
                . dsk/total
        Joining these columns needs to cover following rules:
            - dfs cols must be overlapped
            - dfs not present values must have a valid absent value
        :param input_dir: working directory
        :param output_dir: output directory for aggregated results
        :param dfs: list o base dfs inside main directory
        :param filename: base abspath input filename
        """
        if len(filename):
            self.filename = input_dir + filename
            self.df = self._read_csv(self.filename)

        elif dfs is not None:
            dfs = self._filter_dfs(dfs)
            if not len(dfs):
                raise DStatAggregateNoValidExperiments('Experiments provided are not intersected; no aggregation is possible.')

            for df in dfs:
                self._select_global(df)
                self._add_multindex(df)

            self.filename = self._set_filename(dfs, input_dir)

            dfs = self._time_as_index_topandas(dfs)  # returns dataframes

            # method returns the aggregated dataframe
            df = self._join_dfs(dfs)
            df = self._reshape(df)

            if grain:
                # filter by selected time range
                df = self._partition_time(df)

            # save the main object variable
            self.df = self._to_dict(df)

        self.nodes = self.filename.split('/')[-1].split('.')[0].split('-')[1::2]
        self.date = self.df.itervalues().next().index[0]

        # turn the indexes from datetimes to runtimes in seconds
        self._to_runtime()

        self.outdir = output_dir

    def get_dict(self):
        """ getter method """
        return self.df

    def get_date(self):
        """ get date """
        return self.date

    def get_nodes_list(self):
        """ get nodes list """
        return self.nodes

    def to_csv(self):
        """Export dict-like object dataframes in .csv sheets """

        for k, v in self.df.iteritems():
            v.to_csv(self.filename + '_' + k + '.csv', tupleize_cols=False,) # date_format='%Y-%m-%d %H:%M:%S.%f')

    def _to_dict(self, df):
        """
        Structure a keyed by metric dictionary with dataframe data
            - cpu: cl1-totcpusage - cl2-totcpusage - - cln-totcpusage
            - network: cl1-net/total - cl2-net/total - - cln-net/total
            - memory: cl1 -net/total - cl2-memoryusage - - cln-memoryusage
            - disk: cl1-dsk/total - cl2-dsk/total - - cln-dsk/usage
        :param df: joined cleaned dataframe
        :return: dataframe as a dict object keyed by metric
        """
        ret = {}
        print 'Saving dataframe. . .'
        cpu = pd.DataFrame(df.iloc[:, df.columns.get_level_values(1) == 'total cpu usage'], index=df.index)
        cpu = self._compute_df(cpu, 'cpu')
        ret['cpu'] = cpu

        net = pd.DataFrame(df.iloc[:, df.columns.get_level_values(1) == 'net/total'], index=df.index)
        net = self._compute_df(net, 'net')
        ret['net'] = net

        mem = pd.DataFrame(df.iloc[:, df.columns.get_level_values(1) == 'memory usage'], index=df.index)
        mem = self._compute_df(mem, 'mem')
        ret['mem'] = mem

        dsk = pd.DataFrame(df.iloc[:, df.columns.get_level_values(1) == 'dsk/total'], index=df.index)
        dsk = self._compute_df(dsk, 'dsk')
        ret['dsk'] = dsk

        return ret

    def _compute_df(self, df, mod=''):
        """
        Computes main operations on data. Operation are:
        - average on data for each inner column
        - standard deviation on data for each inner column
        :param df: joined and cleaned dataframe
        :param mod: current device
        :return: new dataframe with result columns
        """
        if mod == 'cpu':
            return self._compute_cpu(df)
        elif mod == 'net':
            df.ix[:, df.columns] = df.ix[:, df.columns].divide(1024*1024)
            return self._compute_net(df)
        elif mod == 'mem':
            df.ix[:, df.columns] = df.ix[:, df.columns].divide(1024*1024*1024)
            return self._compute_mem(df)
        else:  # disk
            df.ix[:, df.columns] = df.ix[:, df.columns].divide(1024*1024)
            return self._compute_dsk(df)

    @staticmethod
    def _compute_cpu(df):
        """
        Computes main operations on cpu data
        :param df: input dataframe
        :return: new dataframe with result columns
        """
        df['avg_sys'] = df.iloc[:, df.columns.get_level_values(2) == 'sys'].mean(axis=1)
        df['avg_usr'] = df.iloc[:, df.columns.get_level_values(2) == 'usr'].mean(axis=1)
        df['avg_idl'] = df.iloc[:, df.columns.get_level_values(2) == 'idl'].mean(axis=1)
        df['avg_wai'] = df.iloc[:, df.columns.get_level_values(2) == 'wai'].mean(axis=1)
        df['avg_hiq'] = df.iloc[:, df.columns.get_level_values(2) == 'hiq'].mean(axis=1)
        df['avg_siq'] = df.iloc[:, df.columns.get_level_values(2) == 'siq'].mean(axis=1)

        df['std_sys'] = df.iloc[:, df.columns.get_level_values(2) == 'sys'].std(axis=1)
        df['std_usr'] = df.iloc[:, df.columns.get_level_values(2) == 'usr'].std(axis=1)
        df['std_idl'] = df.iloc[:, df.columns.get_level_values(2) == 'idl'].std(axis=1)
        df['std_wai'] = df.iloc[:, df.columns.get_level_values(2) == 'wai'].std(axis=1)
        df['std_hiq'] = df.iloc[:, df.columns.get_level_values(2) == 'hiq'].std(axis=1)
        df['std_siq'] = df.iloc[:, df.columns.get_level_values(2) == 'siq'].std(axis=1)

        return df

    @staticmethod
    def _compute_net(df):
        """
        Computes main operations on cpu data
        :param df: input dataframe
        :return: new dataframe with result columns
        """
        df['avg_send'] = df.iloc[:, df.columns.get_level_values(2) == 'send'].mean(axis=1)
        df['avg_recv'] = df.iloc[:, df.columns.get_level_values(2) == 'recv'].mean(axis=1)

        df['sum_send'] = df.iloc[:, df.columns.get_level_values(2) == 'send'].sum(axis=1)
        df['sum_recv'] = df.iloc[:, df.columns.get_level_values(2) == 'recv'].sum(axis=1)

        df['cumsum_send'] = df['sum_send'].cumsum()
        df['cumsum_recv'] = df['sum_recv'].cumsum()

        df['std_send'] = df.iloc[:, df.columns.get_level_values(2) == 'send'].std(axis=1)
        df['std_recv'] = df.iloc[:, df.columns.get_level_values(2) == 'recv'].std(axis=1)

        return df

    @staticmethod
    def _compute_mem(df):
        """
        Computes main operations on cpu data
        :param df: input dataframe
        :return: new dataframe with result columns
        """
        df['avg_used'] = df.iloc[:, df.columns.get_level_values(2) == 'used'].mean(axis=1)
        df['avg_buff'] = df.iloc[:, df.columns.get_level_values(2) == 'buff'].mean(axis=1)
        df['avg_free'] = df.iloc[:, df.columns.get_level_values(2) == 'free'].mean(axis=1)
        df['avg_cach'] = df.iloc[:, df.columns.get_level_values(2) == 'cach'].mean(axis=1)

        df['std_used'] = df.iloc[:, df.columns.get_level_values(2) == 'used'].std(axis=1)
        df['std_buff'] = df.iloc[:, df.columns.get_level_values(2) == 'buff'].std(axis=1)
        df['std_free'] = df.iloc[:, df.columns.get_level_values(2) == 'free'].std(axis=1)
        df['std_cach'] = df.iloc[:, df.columns.get_level_values(2) == 'cach'].std(axis=1)

        df['sum_used'] = df.iloc[:, df.columns.get_level_values(2) == 'used'].sum(axis=1)
        df['cumsum_used'] = df['sum_used'].cumsum()

        return df

    @staticmethod
    def _compute_dsk(df):
        """
        Computes main operations on cpu data
        :param df: input dataframe
        :return: new dataframe with result columns
        """
        df['avg_read'] = df.iloc[:, df.columns.get_level_values(2) == 'read'].mean(axis=1)
        df['avg_writ'] = df.iloc[:, df.columns.get_level_values(2) == 'writ'].mean(axis=1)

        df['sum_read'] = df.iloc[:, df.columns.get_level_values(2) == 'read'].sum(axis=1)
        df['sum_writ'] = df.iloc[:, df.columns.get_level_values(2) == 'writ'].sum(axis=1)

        df['cumsum_read'] = df['sum_read'].cumsum()
        df['cumsum_writ'] = df['sum_writ'].cumsum()

        df['std_read'] = df.iloc[:, df.columns.get_level_values(2) == 'read'].std(axis=1)
        df['std_writ'] = df.iloc[:, df.columns.get_level_values(2) == 'writ'].std(axis=1)

        return df

    def _read_csv(self, filename=""):
        """
        Reading csvs method. Two use-cases:
            - a filename is given, try to read the file and build dict-like object dataframes from that file
            - each file already exists in the working directory, attempting to read each one and build df dict
        :param filename: filename to read
        :return: dict like object
        """
        dfs = {}
        if len(filename):
            try:
                df = pd.read_csv(
                    filename,
                    sep=',',
                    header=0,
                    index_col=0,
                    tupleize_cols=True
                    )
                dfs[filename.split('_')[-1].split('.')[0]] = df
            except Exception as e:
                raise DStatOpenCsvException(e.message)
        else:
            suffixs = ['_cpu.csv', '_mem.csv', '_net.csv', '_dsk.csv']
            for suff in suffixs:
                try:
                    df = pd.read_csv(self.filename + suff,
                                     sep=',',
                                     header=0,
                                     index_col=0,
                                     tupleize_cols=True
                                     )
                    dfs[suff.split('.')[0][0:]] = df
                except Exception as e:
                    raise DStatOpenCsvException(e.message)
        return dfs

    @staticmethod
    def _filter_dfs(dfs):
        """
        For each DStat frame object, compute intersection with each other dataframe, push inside a set intersecting
        dataframes,excluding not intersecting dataframes.
        :param dfs: list of base DStat frame objects concerning the whole experiments inside the current directory
        :return: list of intersected DStat Frame Objects.
        """
        ret = set()
        for outer in dfs:
            found = False
            sout = set(outer.df['epoch', 'epoch'])
            if not len(ret):
                ret.add(outer)
                continue
            for inner in ret:
                sin = set(inner.df['epoch', 'epoch'])
                if len(sout.intersection(sin)):
                    found = True
                    break
            if found:
                ret.add(outer)

        if not len(ret):
            print "Aggregation is not possible; no files founded. Please check input directory."
            exit(1)
        print str(len(ret)) + ' nodes found for the experiment %s' % (next(iter(ret)).df['epoch', 'epoch'][0]).strftime('%Y-%m-%d')

        return list(ret)

    @staticmethod
    def _select_global(df):
        """
        Filters input DStat frame objects collecting only needed - global - information.
        :param dfs: list of intersecting DStat frame objects.
        :return: filtered DStat frame objects.
        """
        try:
            new = df.df[['epoch', 'total cpu usage', 'net/total', 'memory usage', 'dsk/total']]  # original df
        except KeyError as e:
            raise DStatReadColumnsException(e.message)
        df.set_df(other=new)

    @staticmethod
    def _add_multindex(df):
        """
        Adds outer column level for each experiment - which matches the name of the experiment
        :param dfs: intersected and filtered DStat frame objects
        :return: list of DStat frame objects
        """
        cols = []
        tmp = df.df.columns.values
        for idx in range(0, len(tmp)):
            tmp[idx] = (df.name.split('/')[-1],) + tmp[idx]
            cols.append(tmp[idx])
        df.df.columns = pd.MultiIndex.from_tuples(cols)

    @staticmethod
    def _set_filename(dfs, input_dir):
        """
        Function that build output base filename - e.g. cloud-x-cloud-y-cloud-z, where x,y,z are node numbers
        :param dfs: list of pandas dataframes
        :param input_dir: working directory
        :return: self.filename
        """
        print 'Setting new filenames. . .'
        ret = ""
        for df in dfs:
            ret += '-'.join(df.name.split('-')[-2:])
            ret += '-'
        if len(ret) > 255:
            red = ""
            red += '-'.join(df.name.split('-')[-1])
            red += '-'
            ret = red
        return input_dir + '/' + ret[:-1]

    @staticmethod
    def _time_as_index_topandas(dfs):
        """
        Converts 'epoch' column in the dataframe index
        :param dfs: DStat frames objects
        :return: pandas dataframes
        """
        print 'Setting indexing. . .'
        items = [df.df.set_index(df.df[df.name.split('/')[-1], 'epoch', 'epoch']) for df in dfs]
        for item in items:
            item.index.name = 'epoch'
        return items

    def _join_dfs(self, dfs):
        """
        Create a tmp dataframe with a new datetime objects index which covers the entire observation period
        and left outer joins each dataframe with it
        :param dfs: list of dataframes
        :return: the aggregated dataframe
        """
        print 'Joining Dataframes'
        left_df = self._create_left_df(dfs)
        left_df = left_df.join(dfs, how='left', rsuffix='_r', lsuffix='_l')
        return left_df

    @staticmethod
    def _create_left_df(dfs):
        """
        Create a tmp dataframe with a new datetime objects index which covers the entire observation period
        :param dfs: list of dataframes
        :return: temporary full-indexed dataframe
        """
        time = set()
        for df in dfs:
            for value in np.ndenumerate(df.index.values):
                time.add(value[1])
        sorted = list(time)
        sorted.sort()
        index = pd.Index(data=sorted, name='epoch')
        return pd.DataFrame(data=sorted, index=index, columns=['epoch'])

    def _reshape(self, df):
        """
        Reshape column and index after the join
        Call drop_duplicates function
        :param df: joined dataframe
        :return: cleaned joined dataframe
        """
        print 'Final reshaping'
        tmp = df.columns.values
        cols = []
        for idx in range(0, len(tmp)):
            cols.append(tmp[idx] if isinstance(tmp[idx], tuple) else (tmp[idx],))
        df.columns = pd.MultiIndex.from_tuples(cols)
        return self._drop_duplicates(df)

    @staticmethod
    def _drop_duplicates(df):
        """
        Drop duplicates due to left outer multiple join operation
        :param df: joined and reshaped dataframe
        :return: cleaned join dataframe
        """
        to_drop = df.filter(regex="epoch")
        df.drop(to_drop.columns.values, axis=1, inplace=True)
        return df

    def plot_aggr(self, df, mod='', plot=False):
        """
        Plotting aggregating results for each device metrics
        :param df: input dataframe which contains results to plot
        :param mod: current device - needed to select matching metrics (e.g. if mod is 'cpu' then select 'usr,sys,idl..'
        :param plot: Boolean, if True results will be plotted
        :return:
        """

        # here we need a method for printing runtimes instead of datetime timestamps
        # df = self._to_runtimes(df)
        # print df['epoch']

        if mod == 'cpu':
            self._plot_together(df[['avg_usr', 'std_usr']], 'CPU usage: user [%]', 'cpu', 'usr', plot)
            self._plot_together(df[['avg_sys', 'std_sys']], 'CPU usage: system [%]', 'cpu', 'sys', plot)
            self._plot_together(df[['avg_idl', 'std_idl']], 'CPU usage: idle [%]', 'cpu', 'idl', plot)
            self._plot_together(df[['avg_wai', 'std_wai']], 'CPU usage: wait [%]', 'cpu', 'wai', plot)
            self._plot_together(df[['avg_hiq', 'std_hiq']], 'CPU usage: hiq [%]', 'cpu', 'hiq', plot)
            self._plot_together(df[['avg_siq', 'std_siq']], 'CPU usage: siq [%]', 'cpu', 'siq', plot)
        elif mod == 'net':
            self._plot_together(df[['avg_send', 'std_send']], 'Network Bandwidth: sent [MBps]', 'net', 'send', plot)
            self._plot_together(df[['avg_recv', 'std_recv']], 'Network Bandwidth: received [MBps]', 'net', 'recv', plot)
            self._plot_together(df[['sum_send', 'cumsum_send']], 'Cumulative Network Bandwidth: sent [MBps]', 'net', ['sum_send', 'cumsum_send'], plot, clean=True)
            self._plot_together(df[['sum_recv', 'cumsum_recv']], 'Cumulative Network Bandwidth: received [MBps]', 'net', ['sum_recv', 'cumsum_recv'], plot, clean=True)
        elif mod == 'mem':
            self._plot_together(df[['avg_used', 'std_used']], 'Memory usage: used [GB]', 'mem', 'used', plot)
            self._plot_together(df[['avg_free', 'std_free']], 'Memory usage: free [GB]', 'mem', 'free', plot)
            self._plot_together(df[['avg_buff', 'std_buff']], 'Memory usage: buff [GB]', 'mem', 'buff', plot)
            self._plot_together(df[['avg_cach', 'std_cach']], 'Memory usage: cach [GB]', 'mem', 'cach', plot)
            self._plot_together(df[['sum_used', 'cumsum_used']], 'Cumulative Memory usage: used [GB]', 'mem', ['sum_used', 'cumsum_used'], plot, clean=True)
        else:  # disk
            self._plot_together(df[['avg_read', 'std_read']], 'Disk Volume: read [MB]', 'dsk', 'read', plot)
            self._plot_together(df[['avg_writ', 'std_writ']], 'Disk volume: write [MB]', 'dsk', 'writ', plot)
            self._plot_together(df[['sum_read', 'cumsum_read']], 'Cumulative Disk Volume: read [MB]', 'dsk', ['sum_read', 'cumsum_read'], plot, clean=True)
            self._plot_together(df[['sum_writ', 'cumsum_writ']], 'Cumulative Disk volume: write [MB]', 'dsk', ['sum_writ', 'cumsum_writ'], plot, clean=True)

    def plot_clean(self, df, mod='', plot=False):
        """
        Plotting aggregating results for each device metrics without stddev info and in a <paper shaped> way
        There are two cases with multiple metrics to plot:
        - network: send and received
        - disk: read and write
        In this case, a new aggregated metric will be plotted as the sum of the two metrics
        :param df: input dataframe which contains results to plot
        :param mod: current device - needed to select matching metrics (e.g. if mod is 'cpu' then select 'usr,sys,idl..'
        :param plot: Boolean, if True results will be plotted
        :return:
        """

        if mod == 'cpu':
            self._plot_together(df[['avg_usr']], 'CPU usage [%]', 'cpu', ['usr'], plot, clean=True)
        elif mod == 'net':
            tmp = df
            tmp['total'] = df['avg_send'] + df['avg_recv']
            self._plot_together(tmp[['avg_send','total']], 'Network [MBps]', 'net', ['send', 'Total'], plot, clean=True)
        elif mod == 'mem':
            self._plot_together(df[['avg_used']], 'Memory [GB]', 'mem', ['used'], plot, clean=True)
        else:  # disk
            tmp = df
            tmp['total'] = df['avg_read'] + df['avg_writ']
            self._plot_together(tmp[['avg_read', 'total']], 'Disk Volume [MB]', 'dsk', ['read', 'Total'], plot, clean=True)


    def _to_runtime(self):
        """
        Turn dataframes indexes to runtimes in seconds
        :return:
        """
        ret = dict()
        for device, df in self.df.iteritems():
            df = df.set_index((df['epoch'].index.values - df['epoch'].index.values[0])
                            .astype('timedelta64[s]')
                            .astype(int))
            ret[device] = df
        self.df = ret

    @staticmethod
    def _trim(metrics, sep='-'):
        """
        Trim a list to a string with a sep character
        :param metrics:
        :param sep: sep character
        :return:
        """
        assert len(sep) == 1, "Separator charachter should be a char (str retrieved)"

        ret = ''
        if isinstance(metrics, str):
            ret += metrics
            return ret
        else:
            for m in metrics:
                ret += (m + sep)
            return ret[:-1]

    def _plot_together(self, df, plot_title, device, metrics, plot=False, clean=False):
        """

        Plot together handles the aggregated plots, we have a two cases
        - clean:
            Plotting of main aggregated results in a paper shaped way: the following metrics will be printed:
            . cpu -> usr
            . mem -> used
            - dsk -> read, total [= read + writ]
            - net -> sent, total [= send + recv]
        - not clean:
            Plotting each aggregated results and the standard deviation range
        :param df: Aggregated dataframe
        :param plot_title: the plot title
        :param device: string with the following allowed values: cpu, mem, net, dsk
        :param metrics: metrics to take in account for plotting related to the device
        :param plot: Boolean. If it is True, the plot will be shown
        :param clean: Boolean. If it is True, the paper shaped plotting is executed
        :return:
        """

        # Since we have not datetime indexes, we don't need the date formatter
        # hours = mdates.HourLocator()
        # mins = mdates.MinuteLocator()

        save_title = self.date.date().strftime('%Y-%m-%d') + '-' + device + '-' + self._trim(metrics)

        if clean:
            save_title += '-clean'

            # rename columns in order to get easier plot labelling
            df.columns = metrics

            if len(metrics) == 1:
                ax = df.plot.area(
                    stacked=False,
                    alpha=1.0,
                    figsize=(25.9, 3.7),
                    linewidth=4,
                    fontsize=30,
                    color=self.COLORS[1],
                    clip_on=True)
            else:
                ax = plt.gca()
                # met is the reversed list of metrics - print the Total in background then the rest on it
                # i preserves the original metrics indexing - needed for style purposes
                for i, met in reversed(list(enumerate(metrics))):
                    ax = df.plot(
                        kind='area',
                        y=met,
                        ax=ax,
                        colors=self.COLORS[i],
                        figsize=(25.9, 3.7),
                        fontsize=30,
                        alpha=1.0,
                        linewidth=3+i,
                        stacked=False,
                        clip_on=True)

            ax = plt.gca() if ax is None else ax
            self._set_layout(ax, plot_title, device, fontsize=30)

        else:
            plt.figure()
            plt.title(plot_title)
            plt.plot(df.index, df['avg_' + metrics], 'k', label=metrics + ' avg')
            plt.fill_between(
                df.index,
                df['avg_' + metrics] - 2*df['std_' + metrics],
                df['avg_' + metrics] + 2*df['std_' + metrics],
                color='b',
                alpha=0.2)
            ax = plt.gca()
            self._set_layout(ax, plot_title, device)

        self._set_ticks_units(ax, device)

        if plot:
            plt.show()
        else:
            self.save(save_title, device)
            plt.close()

    @staticmethod
    def _set_ticks_units(ax, device):
        if device == 'dsk':
            y_formatter = tick.FormatStrFormatter('%1.2f MB')
            ax.yaxis.set_major_formatter(y_formatter)

    def _set_layout(self, ax, ylab, device, fontsize=12, hours=None, mins=None):
        """
        Setters of plotting layout
        :param ax: get matplotlib axes object
        :param ylab: y axis label
        :param hours: Major x-label formatter
        :param mins: Minor x-label formatter
        :param device: current device
        :return:
        """
        ax.set_xlabel("runtime [sec]", fontsize=fontsize)
        ax.xaxis.grid(True)
        ax.set_ylabel(ylab, fontsize=fontsize)  # self._set_unit()
        ax.yaxis.grid(True)

        if hours is not None and mins is not None:
            self._set_subplots_time(ax=ax, hours=hours, mins=mins)

        if device == 'mem' or device == 'net':
            ax.get_yaxis().get_major_formatter().set_useOffset(False)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width, box.height])

        # anchoring the legend outside of the chart scope
        # plt.legend(loc="upper left", bbox_to_anchor=(1, 0.5))

    @staticmethod
    def _set_subplots_time(ax, hours, mins):
        """ Setting x-labels format """
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_minor_locator(mins)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M:%S'))

    def save(self, save_title, device):
        """ Save plot on disk
        :param save_title: '<save_title>.png' file will be saved
        :param device: current device
        :return:
        """
        outdir = self.outdir + '/' + device
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        outname = outdir + '/' + save_title + '.png'
        plt.savefig(outname, bbox_inches='tight')
        print outname + ' created'

    @staticmethod
    def _numpyds64_to_datetime(nptime):
        ts = (nptime - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        return datetime.datetime.utcfromtimestamp(ts)

    def _partition_time(self, df):
        start = self._numpyds64_to_datetime(df.index.values[0])
        end = self._numpyds64_to_datetime(df.index.values[-1])
        while True:
            print "\n"
            print "Start observation date time: %s" % str(start)
            print "End observation date time: %s" % str(end)
            print "Observation interval request (format: %H:%M:%S , e.g. 00:00:00)"
            new_start = raw_input("    Select a new starting observation time >> ")
            new_end = raw_input("    Select a new ending observation time >> ")
            try:
                final_start = datetime.datetime.strptime(new_start, '%H:%M:%S')
                final_start = final_start.replace(year=start.date().year, month=start.date().month, day=start.date().day )
                final_end = datetime.datetime.strptime(new_end, '%H:%M:%S')
                final_end = final_end.replace(year=end.date().year, month=end.date().month, day=end.date().day )
            except ValueError as e:
                print e.message
                continue
            # evaluating correctness of time given
            if (final_start < start):
                print "Starting time is not a valid time. Try again."
                continue
            elif (final_end > end):
                print "Ending time is not a valid time. Try again."
                continue
            elif (final_start > final_end):
                print "Ending date is prior starting date. Try again."
            else:
                # here is possible to partition and return partitioned dataframe
                ret = df[(df.index > final_start) & (df.index < final_end)]
                return ret
