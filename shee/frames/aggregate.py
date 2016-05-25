#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

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
    def __init__(self, input_dir, output_dir, dfs=None, filename=""):
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

            df = self._join_dfs(dfs)
            df = self._reshape(df)

            self.df = self._to_dict(df)

        self.nodes = self.filename.split('/')[-1].split('.')[0].split('-')[1::2]
        self.date = self.df.itervalues().next().index[0]
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
            v.to_csv(self.filename + '_' + k + '.csv', tupleize_cols=False,) #date_format='%Y-%m-%d %H:%M:%S.%f')

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
            df.ix[:, df.columns] = df.ix[:, df.columns].divide(1000)
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
        :return:
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
        elif mod == 'mem':
            self._plot_together(df[['avg_used', 'std_used']], 'Memory usage: used [GB]', 'mem', 'used', plot)
            self._plot_together(df[['avg_free', 'std_free']], 'Memory usage: free [GB]', 'mem', 'free', plot)
            self._plot_together(df[['avg_buff', 'std_buff']], 'Memory usage: buff [GB]', 'mem', 'buff', plot)
            self._plot_together(df[['avg_cach', 'std_cach']], 'Memory usage: cach [GB]', 'mem', 'cach', plot)
        else:  # disk
            self._plot_together(df[['avg_read', 'std_read']], 'Disk ops: reads', 'dsk', 'read', plot)
            self._plot_together(df[['avg_writ', 'std_writ']], 'Disk ops: writes', 'dsk', 'writ', plot)

    def _plot_together(self, df, plot_title, device, metric, plot=False):
        """
        Plots all values in the second level of the column in one graph, no stacked lines
        :param plot:
        """

        hours = mdates.HourLocator()
        mins = mdates.MinuteLocator()

        save_title = df.index[0].strftime('%Y-%m-%d') + '-' + device + '-' + metric

        plt.figure()
        plt.title(plot_title)
        plt.plot(df.index, df['avg_' + metric], 'k', label=metric + ' avg')
        plt.fill_between(df.index,
                         df['avg_' + metric] - 2*df['std_' + metric],
                         df['avg_' + metric] + 2*df['std_' + metric],
                         color='b',
                         alpha=0.2)

        self._set_layout(plt.gca(), plot_title, hours, mins, device)
        self._set_ticks_units(plt.gca(), device)

        if plot:
            plt.show()
        else:
            self.save(save_title, device)
            plt.close()

    @staticmethod
    def _set_ticks_units(ax, device):
        if device == 'dsk':
            y_formatter = tick.FormatStrFormatter('%d K')
            ax.yaxis.set_major_formatter(y_formatter)

    def _set_layout(self, ax, ylab, hours, mins, device):
        """
        Setters of plotting layout
        :param ax: get matplotlib axes object
        :param ylab: y axis label
        :param hours: Major x-label formatter
        :param mins: Minor x-label formatter
        :param device: current device
        :return:
        """
        ax.set_xlabel("time")
        ax.xaxis.grid(True)
        ax.set_ylabel(ylab)  # self._set_unit()
        ax.yaxis.grid(True)
        self._set_subplots_time(ax=ax, hours=hours, mins=mins)

        if device == 'mem' or device == 'net':
            ax.get_yaxis().get_major_formatter().set_useOffset(False)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width, box.height])

        plt.legend(loc="upper left", bbox_to_anchor=(1, 0.5))

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
