#!/usr/bin/env python
# -*- coding: utf-8 -*-

from frame import DStatFrame

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class DStatCompare(DStatFrame):
    def __init__(self, filename, columns, frame=None, grain=False):
        if frame is not None:
            self.df = frame.df
            self.device = frame.device
            self._set_name(columns)
        else:
            super(DStatCompare, self).__init__(filename, columns)
        sname = filename.split(".")[0]  # path completo fino al nome del file meno '.csv' cartella dedicata
        # setting nome file: la cartella sarà comparison, i nomi dei file saranno le colonne da confrontare
        self.filename = sname + '/comparison/' + sname.split("/")[-1]
        self.device = 'comparison'
        df = self._read_dataframe(['epoch'] + columns, grain=grain)
        df.columns = df.columns.droplevel()
        self.df = self._convert(df, ['epoch', 'usr', 'sys', 'idl', 'hiq', 'siq'], 1024*1024)

    @staticmethod
    def _convert(df, not_convert, div):
        cols = df.columns.difference(not_convert)
        df.ix[:, cols] = df.ix[:, cols].divide(div)
        return df

    @staticmethod
    def _select_plot_columns(name):
        if name == 'total cpu usage' or name.startswith('cpu'):
            return ['usr', 'sys', 'idl', 'wai', 'hiq', 'siq']
        elif name.startswith('net/'):
            return ['send', 'recv']
        elif name == 'memory usage':
            return ['used', 'buff', 'cach', 'free']

    def subplot_all(self, cols, plot=False, grain=False):
        plot_title, save_title = self._get_titles()

        hours = mdates.HourLocator()  # every year
        mins = mdates.MinuteLocator()  # every month
        secs = mdates.SecondLocator()  # every month

        if len(cols) == 2:
            # row and column sharing
            ax1 = plt.subplot(211)
            self._set_subplots_title_and_plot(ax1, 'epoch', self._select_plot_columns(cols[0]), cols[0])
            self._set_subplots_time(ax=ax1, hours=hours, mins=mins, secs=secs, grain=grain)
            ax1.set_ylabel(self._set_unit(cols[0]))
            # plt.setp(ax1.get_xticklabels(), rotation=30, horizontalalignment='right')
            ax1.xaxis.set_tick_params(which="major", pad=15)
            ax1.grid(True)
            ax1.legend(loc="upper left", bbox_to_anchor=[1, 1], shadow=True, fancybox=True)

            ax2 = plt.subplot(212)
            self._set_subplots_title_and_plot(ax2, 'epoch',  self._select_plot_columns(cols[1]), cols[1])
            self._set_subplots_time(ax=ax2, hours=hours, mins=mins, secs=secs, grain=grain)
            ax2.set_ylabel(self._set_unit(cols[1]))
            ax2.set_xlabel('time')
            # plt.setp(ax2.get_xticklabels(), rotation=30, horizontalalignment='right')
            ax2.xaxis.set_tick_params(which="major", pad=15)
            ax2.grid(True)
            ax2.legend(loc="upper left", bbox_to_anchor=[1, 1], shadow=True, fancybox=True)
        else:
            ax1 = plt.subplot(311)
            self._set_subplots_title_and_plot(ax1, 'epoch', self._select_plot_columns(cols[0]), cols[0])
            ax1.grid(True)
            self._set_subplots_time(ax=ax1, hours=hours, mins=mins, secs=secs, grain=grain)
            ax1.set_ylabel(self._set_unit(cols[0]))
            ax1.xaxis.set_tick_params(which="major", pad=15)
            ax1.legend(loc="upper left", bbox_to_anchor=[1, 1], shadow=True, fancybox=True)

            ax2 = plt.subplot(312)
            self._set_subplots_title_and_plot(ax2, 'epoch',  self._select_plot_columns(cols[1]), cols[1])
            ax2.grid(True)
            self._set_subplots_time(ax=ax2, hours=hours, mins=mins, secs=secs, grain=grain)
            ax2.set_ylabel(self._set_unit(cols[1]))
            ax2.xaxis.set_tick_params(which="major", pad=15)
            ax2.legend(loc="upper left", bbox_to_anchor=[1, 1], shadow=True, fancybox=True)

            ax3 = plt.subplot(313)
            self._set_subplots_title_and_plot(ax3, 'epoch',  self._select_plot_columns(cols[2]), cols[2])
            ax3.grid(True)
            self._set_subplots_time(ax=ax3, hours=hours, mins=mins, secs=secs, grain=grain)
            ax3.set_ylabel(self._set_unit(cols[2]))
            ax3.xaxis.set_tick_params(which="major", pad=15)
            ax3.set_xlabel('time')
            ax3.legend(loc="upper left", bbox_to_anchor=[1, 1], shadow=True, fancybox=True)

        plt.gcf().autofmt_xdate()

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
    def _set_subplots_time(ax, hours, mins, secs, grain):
        ax.xaxis.set_major_locator(hours)
        if grain:
            ax.xaxis.set_minor_locator(secs)
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%S'))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        else:
            ax.xaxis.set_minor_locator(mins)
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(''))