#!/usr/bin/env python
# -*- coding: utf-8 -*-

from frame import DStatFrame

import matplotlib.pyplot as plt
import matplotlib.dates as mdates



class DStatNetwork(DStatFrame):

    def __init__(self, filename, eth=None, grain=False):
        super(DStatNetwork, self).__init__(filename, 'network')
        sname = filename.split(".")[0]
        if eth is not None:
            self.filename = sname + '/network/eth' + str(eth) + '/' + sname.split("/")[-1]
            df = self._read_dataframe(['epoch', 'net/eth' + str(eth)], grain=grain)
            self.device = eth
        else:
            self.filename = sname + '/network/' + sname.split("/")[-1]
            df = self._read_dataframe(['epoch', 'net/total'], grain=grain)

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