#!/usr/bin/env python
# -*- coding: utf-8 -*-

from frame import DStatFrame
from shee.util import get_result_dir_name

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class DStatCpu(DStatFrame):

    def __init__(self, filename, frame=None, cpu=None, grain=False):
        if frame is not None:
            self.df = frame.df
            self.device = frame.device
            self._set_name('cpu')
        else:
            super(DStatCpu, self).__init__(filename, 'cpu')
        sname = get_result_dir_name(filename)
        if cpu is not None:
            self.filename = sname + '/cpu/cpu' + str(cpu) + '/' + sname.split("/")[-1]
            df = self._read_dataframe(['epoch', 'cpu' + str(cpu) + ' usage'], grain=grain)
            self.device = cpu
        else:
            self.filename = sname + '/cpu/' + sname.split("/")[-1]
            df = self._read_dataframe(['epoch', 'total cpu usage'], grain=grain)
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

        self._rotating_xticks_and_grid([ax1, ax2, ax3, ax4, ax5, ax6])

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