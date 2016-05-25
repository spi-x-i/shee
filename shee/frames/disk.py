#!/usr/bin/env python
# -*- coding: utf-8 -*-

from frame import DStatFrame

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tick

class DStatDisk(DStatFrame):

    def __init__(self, filename, disk=None, grain=False):
        super(DStatDisk, self).__init__(filename, 'disk')
        sname = filename.split(".")[0]
        if disk is not None:
            self.filename = sname + '/disk/sd' + disk + '/' + sname.split("/")[-1]
            df = self._read_dataframe(['epoch', 'dsk/sd' + disk], grain=grain)
            self.device = disk
        else:
            self.filename = sname + '/disk/' + sname.split("/")[-1]
            df = self._read_dataframe(['epoch', 'dsk/total'], grain=grain)

        df.columns = df.columns.droplevel()
        df.ix[:, df.columns != 'epoch'] = df.ix[:, df.columns != 'epoch'].divide(1000)
        self.df = df

    def subplot_all(self, plot=False):
        plot_title, save_title = self._get_titles()

        # row and column sharing
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

        hours = mdates.HourLocator()  # every year
        mins = mdates.MinuteLocator()  # every month

        y_formatter = tick.FormatStrFormatter('%d K')

        self._set_subplots_title_and_plot(ax1, 'epoch', 'read')
        ax1.set_ylabel(plot_title + ' (count)')
        ax1.yaxis.set_major_formatter(y_formatter)

        self._set_subplots_title_and_plot(ax2, 'epoch', 'writ')
        self._set_subplots_time(ax=ax2, hours=hours, mins=mins)

        ax2.yaxis.set_major_formatter(y_formatter)
        ax2.set_ylabel(plot_title + ' (count)')
        ax2.set_xlabel('time')

        self._rotating_xticks_and_grid([ax1, ax2])


        plt.tight_layout(pad=1, w_pad=1, h_pad=1)
        if plot:
            plt.show()
        else:
            self.save(save_title + "subplots")
            plt.close()

    def _set_subplots_title_and_plot(self, ax, xlab, ylab):
        ax.set_title(ylab)
        ax.plot(self.df[xlab], self.df[ylab])

    @staticmethod
    def _rotating_xticks_and_grid(axs):
        for ax in axs:
            ax.grid(True)
            ax.tick_params(axis='x', pad=20)
            plt.setp(ax.xaxis.get_minorticklabels(), rotation=40)

    @staticmethod
    def _set_subplots_time(ax, hours, mins):
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_minor_locator(mins)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))