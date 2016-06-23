#!/usr/bin/env python
# -*- coding: utf-8 -*-

from frame import DStatFrame
from shee.util import get_result_dir_name

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class DStatMemory(DStatFrame):

    def __init__(self, filename, frame=None, grain=False):
        if frame is not None:
            self.df = frame.df
            self.device = frame.device
            self._set_name('memory')
        else:
            super(DStatMemory, self).__init__(filename, 'memory')
        sname = get_result_dir_name(filename)
        self.filename = sname + '/memory/' + sname.split("/")[-1]
        df = self._read_dataframe(['epoch', 'memory usage'], grain=grain)
        df.columns = df.columns.droplevel()
        df.ix[:, df.columns != 'epoch'] = df.ix[:, df.columns != 'epoch'].divide(1024*1024*1024)
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

        self._rotating_xticks_and_grid([ax1, ax2, ax3, ax4])

        plt.tight_layout(pad=1, w_pad=1, h_pad=1)
        if plot:
            plt.show()
        else:
            self.save(save_title + "subplots")
            plt.close()

    @staticmethod
    def _rotating_xticks_and_grid(axs):
        for ax in axs:
            ax.grid(True)
            ax.tick_params(axis='x', pad=20)
            plt.setp(ax.xaxis.get_minorticklabels(), rotation=40)

    def _set_subplots_title_and_plot(self, ax, xlab, ylab):
        ax.set_title(ylab)
        ax.plot(self.df[xlab], self.df[ylab])

    @staticmethod
    def _set_subplots_time(ax, hours, mins):
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_minor_locator(mins)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))