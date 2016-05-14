#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class DStatException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class OpenCsvException(DStatException):
    """
    Raised when pandas.read_csv fails
    """


class DateTimeConversionException(DStatException):
    """
    Raised when pandas.to_datetime fails
    """


class DStatFixColumnsException(DStatException):
    """
    Raised when fix_columns internal method fails
    """


class DStatFrame(object):

    def __init__(self, filename, name):
        try:
            self.df = self._open_csv(filename)
            sname = filename.split(".")[0]
            self.filename = sname + '/' + sname.split("/")[-1]
            self.device = None
            self.name = name
        except Exception as e:
            raise OpenCsvException(e.message)
        try:
            self._to_datetime()
        except Exception as e:
            raise DateTimeConversionException(e.message)
        try:
            self._fix_columns()
        except Exception as e:
            raise DStatFixColumnsException(e.message)

    @staticmethod
    def _open_csv(filename):
        return pd.read_csv(
            filepath_or_buffer=filename,
            sep=",",
            skip_blank_lines=True,
            header=[2, 3],
        )

    def _to_datetime(self):
        """
        Method converting unix timestamp Series column to datetime column UTC+1
        :return:
        """
        # add on hour time (UTC:+1:00)
        self.df['epoch', 'epoch'] += 3600
        self.df['epoch', 'epoch'] = pd.to_datetime(self.df['epoch', 'epoch'], unit='s')

    def _fix_columns(self, level=0, to_replace='Unnamed'):
        """
        Fix column method: replace columns unnamed values; needed for multi-indexing plotting

        :param level:
        :param to_replace:
        :return:
        """
        cols = self.df.columns.values
        replace_value = ""
        new_cols = {}

        for col in cols:
            if to_replace in col[level]:
                new_cols[col[level]] = replace_value
            else:
                replace_value = col[level]

        self.df.rename(columns=new_cols, inplace=True)

    def save(self, suffix):
        outname = self.filename + '-' + suffix + '.png'
        plt.savefig(outname, bbox_inches='tight')
        print outname + " created"

    def plot_together(self, plot=False):
        """
        This method plots all value in the second level of the column in one graph, no stacked lines
        """
        plot_title, save_title = self._get_titles()

        ax = self.df.plot(kind='line', x='epoch', title=plot_title)

        self._set_layout(ax)

        if plot:
            plt.show()
        else:
            self.save(save_title + "line")
            plt.close()

    def plot_stacked(self, columns=None, plot=False):
        """

        :param columns:
        :param plot:
        :return:
        """
        plot_title, save_title = self._get_titles()

        ax = self.df.plot.area(stacked=False, x='epoch', y=columns, title=plot_title)

        self._set_layout(ax)

        if plot:
            plt.show()
        else:
            name = save_title + 'stacked'
            for col in columns:
                name += ('-' + col)
            self.save(name)
            plt.close()

    def _set_unit(self):
        if self.name == 'cpu':
            return "percentage"
        elif self.name == 'network':
            return "bandwidth [MBps]"
        else:
            return "memory usage"

    def _set_layout(self, ax):
        unit = self._set_unit()
        ax.set_xlabel("time")
        ax.xaxis.grid(True)
        ax.set_ylabel(self._set_unit())
        ax.yaxis.grid(True)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width, box.height])

        plt.legend(loc="upper left", bbox_to_anchor=(1, 0.5))

    def _get_titles(self):
        if self.device is not None:
            plot_title = self.name.upper() + str(self.device) + " Usage"
            save_title = self.name + "-" + str(self.device) + "-"
        else:
            plot_title = "Total " + self.name.upper() + " Usage"
            save_title = "total-" + self.name + "-"
        return plot_title, save_title


class DStatCpu(DStatFrame):

    def __init__(self, filename, name, cpu=None):
        super(DStatCpu, self).__init__(filename, name)
        if cpu is not None:
            df = self.df[['epoch', 'cpu' + str(cpu) + ' usage']]
            df.columns = df.columns.droplevel()
            self.df = df
            self.device = cpu
        else:
            df = self.df[['epoch', 'total cpu usage']]
            df.columns = df.columns.droplevel()
            self.df = df

    def plot_all(self):
        pass

    def subplot_all(self, plot=False):
        plot_title, save_title = self._get_titles()

        # row and column sharing
        fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex='col', sharey='row')

        hours = mdates.HourLocator()  # every year
        mins = mdates.MinuteLocator()  # every month

        self._set_subplots_title_and_plot(ax1, 'epoch', 'usr')
        ax1.set_ylabel(plot_title + '(%)')

        self._set_subplots_title_and_plot(ax1, 'epoch', 'sys')

        self._set_subplots_title_and_plot(ax1, 'epoch', 'idl')

        ax4.set_ylim([0, 100])
        self._set_subplots_title_and_plot(ax4, 'epoch', 'wai')
        self._set_subplots_time(ax=ax4, hours=hours, mins=mins)
        ax4.set_ylabel(plot_title + '(%)')

        self._set_subplots_title_and_plot(ax5, 'epoch', 'hiq')
        self._set_subplots_time(ax=ax5, hours=hours, mins=mins)
        ax5.set_xlabel('time')

        self._set_subplots_title_and_plot(ax6, 'epoch', 'siq')
        self._set_subplots_time(ax=ax6, hours=hours, mins=mins)

        if plot:
            plt.show()
        else:
            self.save(save_title + "subplots")
            plt.close()

    def _set_subplots_title_and_plot(self, ax, xlab, ylab):
        ax.set_title(ylab)
        ax.plot(self.df[xlab], self.df[ylab])

    @staticmethod
    def _set_subplots_time(ax, hours, mins):
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_minor_locator(mins)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))


class DStatNetwork(DStatFrame):

    def __init__(self, filename, name, eth=None):
        super(DStatNetwork, self).__init__(filename, name)
        if eth is not None:
            df = self.df[['epoch', 'net/eth' + str(eth)]]
            df.columns = df.columns.droplevel()
            self.df = df
            self.device = eth
        else:
            df = self.df[['epoch', 'net/total']]
            df.columns = df.columns.droplevel()
            df.ix[:,df.columns != 'epoch'] = df.ix[:,df.columns != 'epoch'].divide(1024*1024*8)
            self.df = df

    def subplot_all(self, plot=False):
        plot_title, save_title = self._get_titles()

        # row and column sharing
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex='col')

        hours = mdates.HourLocator()  # every year
        mins = mdates.MinuteLocator()  # every month

        self._set_subplots_title_and_plot(ax1, 'epoch', 'send')
        ax1.set_ylabel(plot_title + '(%)')

        # ax2.set_ylim([0, 100])
        self._set_subplots_title_and_plot(ax2, 'epoch', 'recv')
        self._set_subplots_time(ax=ax2, hours=hours, mins=mins)
        ax2.set_ylabel(plot_title + '(%)')

        if plot:
            plt.show()
        else:
            self.save(save_title + "subplots")
            plt.close()

    def _set_subplots_title_and_plot(self, ax, xlab, ylab):
        ax.set_title(ylab)
        ax.plot(self.df[xlab], self.df[ylab])

    @staticmethod
    def _set_subplots_time(ax, hours, mins):
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_minor_locator(mins)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))


class DStatMemory(DStatFrame):

    def __init__(self, filename, name):
        super(DStatMemory, self).__init__(filename, name)
        df = self.df[['epoch', 'memory usage']]
        df.columns = df.columns.droplevel()
        df.ix[:,df.columns != 'epoch'] = df.ix[:,df.columns != 'epoch'].divide(1024*1024*8)
        self.df = df

    def subplot_all(self, plot=False):
        plot_title, save_title = self._get_titles()

        # row and column sharing
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row')

        hours = mdates.HourLocator()  # every year
        mins = mdates.MinuteLocator()  # every month

        self._set_subplots_title_and_plot(ax1, 'epoch', 'used')
        ax1.set_ylabel(plot_title + '(%)')

        self._set_subplots_title_and_plot(ax2, 'epoch', 'buff')

        self._set_subplots_title_and_plot(ax3, 'epoch', 'free')
        self._set_subplots_time(ax=ax3, hours=hours, mins=mins)
        ax3.set_ylabel(plot_title)

        self._set_subplots_title_and_plot(ax4, 'epoch', 'cach')
        self._set_subplots_time(ax=ax4, hours=hours, mins=mins)
        ax4.set_xlabel('time')

        if plot:
            plt.show()
        else:
            self.save(save_title + "subplots")
            plt.close()

    def _set_subplots_title_and_plot(self, ax, xlab, ylab):
        ax.set_title(ylab)
        ax.plot(self.df[xlab], self.df[ylab])

    @staticmethod
    def _set_subplots_time(ax, hours, mins):
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_minor_locator(mins)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))

