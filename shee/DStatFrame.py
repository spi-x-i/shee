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

    def __init__(self, filename):
        try:
            self.df = self._open_csv(filename)
            name = filename.split(".")[0]
            self.filename = name + '/' + name.split("/")[-1]
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
        # convert unix timestamp to datetime param
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


class DStatCpu(DStatFrame):

    def __init__(self, filename, cpu=None):
        super(DStatCpu, self).__init__(filename)
        if cpu is not None:
            df = self.df[['epoch', 'cpu' + str(cpu) + ' usage']]
            df.columns = df.columns.droplevel()
            self.df = df
        else:
            df = self.df[['epoch', 'total cpu usage']]
            df.columns = df.columns.droplevel()
            self.df = df

    def plot_all(self):
        pass

    def plot_together(self, plot=False):
        """
        This method plots all value in the second level of the column in one graph, no stacked lines
        :return:
        """
        ax = self.df.plot(kind='line', x='epoch', title="Total CPU Usage")

        ax.set_xlabel("time")
        ax.xaxis.grid(True)
        ax.set_ylabel("percentage")
        ax.yaxis.grid(True)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width, box.height])

        plt.legend(loc="upper left", bbox_to_anchor=(1, 0.5))

        if plot:
            plt.show()
        else:
            self.save('total-cpu-line')
            plt.close()

    def subplot_all(self, plot=False):
        # row and column sharing
        fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex='col', sharey='row')

        hours = mdates.HourLocator()  # every year
        mins = mdates.MinuteLocator()  # every month
        # yearsFmt = mdates.DateFormatter('%Y')

        ax1.set_title('usr')
        ax1.plot(self.df['epoch'], self.df['usr'])
        ax1.set_ylabel('Tot. cpu usage (%)')
        ax2.set_title('sys')
        ax2.plot(self.df['epoch'], self.df['sys'])
        ax3.set_title('idl')
        ax3.plot(self.df['epoch'], self.df['idl'])
        ax4.set_ylim([0, 100])
        ax4.set_title('wai')
        ax4.plot(self.df['epoch'], self.df['wai'])
        ax4.set_ylabel('Tot. cpu usage (%)')
        ax4.xaxis.set_major_locator(hours)
        ax4.xaxis.set_minor_locator(mins)
        ax4.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax4.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))
        ax5.set_title('hiq')
        ax5.plot(self.df['epoch'], self.df['hiq'])
        ax5.set_xlabel('time')
        ax5.xaxis.set_major_locator(hours)
        ax5.xaxis.set_minor_locator(mins)
        ax5.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax5.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))
        ax6.set_title('siq')
        ax6.plot(self.df['epoch'], self.df['siq'])
        ax6.xaxis.set_major_locator(hours)
        ax6.xaxis.set_minor_locator(mins)
        ax6.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax6.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))

        if plot:
            plt.show()
        else:
            self.save('total-cpu-subplot')
            plt.close()

    def plot_stacked(self, columns=None, plot=False):

        ax = self.df.plot.area(stacked=False, x='epoch', y=columns)

        ax.set_xlabel("time")
        ax.xaxis.grid(True)
        ax.set_ylabel("percent")
        ax.yaxis.grid(True)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width, box.height])

        plt.legend(loc="upper left", bbox_to_anchor=(1, 0.5))

        if plot:
            plt.show()
        else:
            name = 'total-cpu-stacked'
            for col in columns:
                name += ('-' + col)
            self.save(name)
            plt.close()
