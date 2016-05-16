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


class DStatOpenCsvException(DStatException):
    """
    Raised when pandas.read_csv fails
    """
    pass


class DStatDateTimeConversionException(DStatException):
    """
    Raised when pandas.to_datetime fails
    """
    pass


class DStatFixColumnsException(DStatException):
    """
    Raised when fix_columns internal method fails
    """
    pass

class DStatReadColumnsException(DStatException):
    """
    Raised when attempting to read a column that it doesn't exists
    """
    pass


class DStatFrame(object):

    def __init__(self, filename, name):
        try:
            self.df = self._open_csv(filename)
            self.filename = ""
            self.device = None
            if isinstance(name, list):
                temp = ""
                for s in name:
                    for ch in [" ", "/"]:
                        if ch in s:
                            s = s.replace(" ", "")
                    temp += (s + "-")
                self.name = temp[:-1]
            else:
                self.name = name
        except Exception as e:
            raise DStatOpenCsvException(e.message)
        try:
            self._to_datetime()
        except Exception as e:
            raise DStatDateTimeConversionException(e.message)
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

    def _read_dataframe(self, columns):
        try:
            df = self.df[columns]
            return df
        except KeyError as e:
            raise DStatReadColumnsException(e.message)

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

    def _set_unit(self, compare=None):
        name = compare if compare is not None else self.name
        if name in ['cpu','total cpu usage']:
            return "percentage"
        elif name in ['network','net/total']:
            return "bandwidth [MBps]"
        else:
            return "memory usage [MB]"

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
            device_name = 'eth' if self.name == 'network' else self.name
            plot_title = device_name.upper() + str(self.device) + " Usage"
            if self.device == 'comparison':
                save_title = self.name + "-"
            else:
                save_title = self.name + "-" + device_name + str(self.device) + "-"
        else:
            plot_title = "Total " + self.name.upper() + " Usage"
            save_title = "total-" + self.name + "-"
        return plot_title, save_title


class DStatCpu(DStatFrame):

    def __init__(self, filename, cpu=None):
        super(DStatCpu, self).__init__(filename, 'cpu')
        sname = filename.split(".")[0]
        if cpu is not None:
            self.filename = sname + '/cpu/cpu' + str(cpu) + '/' + sname.split("/")[-1]
            df = self._read_dataframe(['epoch', 'cpu' + str(cpu) + ' usage'])
            self.device = cpu
        else:
            self.filename = sname + '/cpu/' + sname.split("/")[-1]
            df = self._read_dataframe(['epoch', 'total cpu usage'])
        df.columns = df.columns.droplevel()
        self.df = df

    def plot_all(self):
        pass

    def subplot_all(self, plot=False):
        plot_title, save_title = self._get_titles()

        # row and column sharing
        fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex=True, sharey=True)

        hours = mdates.HourLocator()  # every year
        mins = mdates.MinuteLocator()  # every month

        self._set_subplots_title_and_plot(ax1, 'epoch', 'usr')
        ax1.set_ylabel(plot_title + '(%)')

        self._set_subplots_title_and_plot(ax2, 'epoch', 'sys')

        self._set_subplots_title_and_plot(ax3, 'epoch', 'idl')

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

    def __init__(self, filename, eth=None):
        super(DStatNetwork, self).__init__(filename, 'network')
        sname = filename.split(".")[0]
        if eth is not None:
            self.filename = sname + '/network/eth' + str(eth) + '/' + sname.split("/")[-1]
            df = self._read_dataframe(['epoch', 'net/eth' + str(eth)])
            self.device = eth
        else:
            self.filename = sname + '/network/' + sname.split("/")[-1]
            df = self._read_dataframe(['epoch', 'net/total'])

        df.columns = df.columns.droplevel()
        df.ix[:, df.columns != 'epoch'] = df.ix[:, df.columns != 'epoch'].divide(1024*1024*8)
        self.df = df

    def subplot_all(self, plot=False):
        plot_title, save_title = self._get_titles()

        # row and column sharing
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

        hours = mdates.HourLocator()  # every year
        mins = mdates.MinuteLocator()  # every month

        self._set_subplots_title_and_plot(ax1, 'epoch', 'send')
        ax1.set_ylabel(plot_title + 'MBps')

        self._set_subplots_title_and_plot(ax2, 'epoch', 'recv')
        self._set_subplots_time(ax=ax2, hours=hours, mins=mins)
        ax2.set_ylabel(plot_title + 'MBps')
        ax2.set_xlabel('time')

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

    def __init__(self, filename):
        super(DStatMemory, self).__init__(filename, 'memory')
        sname = filename.split(".")[0]
        self.filename = sname + '/memory/' + sname.split("/")[-1]
        df = self._read_dataframe(['epoch', 'memory usage'])
        df.columns = df.columns.droplevel()
        df.ix[:, df.columns != 'epoch'] = df.ix[:, df.columns != 'epoch'].divide(1024*1024*8)
        self.df = df

    def subplot_all(self, plot=False):
        plot_title, save_title = self._get_titles()

        # row and column sharing
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex=True, sharey=True)

        hours = mdates.HourLocator()  # every year
        mins = mdates.MinuteLocator()  # every month

        self._set_subplots_title_and_plot(ax1, 'epoch', 'used')
        ax1.set_ylabel(plot_title)

        self._set_subplots_title_and_plot(ax2, 'epoch', 'buff')

        self._set_subplots_title_and_plot(ax3, 'epoch', 'free')
        self._set_subplots_time(ax=ax3, hours=hours, mins=mins)
        ax3.set_ylabel(plot_title)
        ax3.set_xlabel('time')

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


class DStatCompare(DStatFrame):
    def __init__(self, filename, columns):
        super(DStatCompare, self).__init__(filename, columns)
        sname = filename.split(".")[0] # path completo fino al nome del file meno '.csv' cartella dedicata
        # setting nome file: la cartella sarà comparison, i nomi dei file saranno le colonne da confrontare
        self.filename = sname + '/comparison/' + sname.split("/")[-1]
        self.device = 'comparison'
        df = self._read_dataframe(['epoch'] + columns)
        df.columns = df.columns.droplevel()
        self.df = self._convert(df, ['epoch','usr','sys','idl','hiq','siq'], 1024*1024*8)

    @staticmethod
    def _convert(df, not_convert, div):
        cols = df.columns.difference(not_convert)
        df.ix[:, cols] = df.ix[:, cols].divide(div)
        return df

    def _select_plot_columns(self, name):
        if name == 'total cpu usage':
            return ['usr', 'sys', 'idl', 'wai', 'hiq', 'siq']
        elif name == 'net/total':
            return ['send', 'recv']
        elif name == 'memory usage':
            return ['used','buff','cach','free']

    def subplot_all(self, cols, plot=False):
        plot_title, save_title = self._get_titles()

        hours = mdates.HourLocator()  # every year
        mins = mdates.MinuteLocator()  # every month

        if len(cols) == 2:
            # row and column sharing
            ax1 = plt.subplot(211)
            self._set_subplots_title_and_plot(ax1, 'epoch', self._select_plot_columns(cols[0]), cols[0])
            self._set_subplots_time(ax=ax1, hours=hours, mins=mins)
            ax1.set_ylabel(self._set_unit(cols[0]))
            ax1.grid(True)
            ax1.legend(loc="upper left", bbox_to_anchor=[1, 1], shadow=True, fancybox=True)

            ax2 = plt.subplot(211)
            self._set_subplots_title_and_plot(ax2, 'epoch',  self._select_plot_columns(cols[1]), cols[1])
            self._set_subplots_time(ax=ax2, hours=hours, mins=mins)
            ax2.set_ylabel(self._set_unit(cols[1]))
            ax2.set_xlabel('time')
            ax2.grid(True)
            ax2.legend(loc="upper left", bbox_to_anchor=[1,1], shadow=True, fancybox=True)
        else:
            # fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
            ax1 = plt.subplot(311)
            self._set_subplots_title_and_plot(ax1, 'epoch', self._select_plot_columns(cols[0]), cols[0])
            ax1.grid(True)
            self._set_subplots_time(ax=ax1, hours=hours, mins=mins)
            ax1.set_ylabel(self._set_unit(cols[0]))
            ax1.legend(loc="upper left", bbox_to_anchor=[1,1], shadow=True, fancybox=True)

            ax2 = plt.subplot(312)
            self._set_subplots_title_and_plot(ax2, 'epoch',  self._select_plot_columns(cols[1]), cols[1])
            ax2.grid(True)
            self._set_subplots_time(ax=ax2, hours=hours, mins=mins)
            ax2.set_ylabel(self._set_unit(cols[1]))
            ax2.legend(loc="upper left", bbox_to_anchor=[1, 1], shadow=True, fancybox=True)

            ax3 = plt.subplot(313)
            self._set_subplots_title_and_plot(ax3, 'epoch',  self._select_plot_columns(cols[2]), cols[2])
            ax3.grid(True)
            self._set_subplots_time(ax=ax3, hours=hours, mins=mins)
            ax3.set_ylabel(self._set_unit(cols[2]))
            ax3.set_xlabel('time')
            plt.legend(loc="upper left", bbox_to_anchor=[1, 1], shadow=True, fancybox=True)

        if plot:
            plt.show()
        else:
            self.save(save_title + "subplots")
            plt.close()

    def _set_subplots_title_and_plot(self, ax, xlab, ylab, title):
        ax.set_title(title)
        for idx, col in enumerate(self.df[ylab]):
            plt.plot(self.df[xlab], self.df[col], label=col)

    @staticmethod
    def _set_subplots_time(ax, hours, mins):
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_minor_locator(mins)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))


