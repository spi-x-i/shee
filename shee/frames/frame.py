#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

import pandas as pd

import matplotlib.pyplot as plt


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
                            s = s.replace("/", "")
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

    def __eq__(self, other):
        return self.df.equals(other)

    @staticmethod
    def _open_csv(filename):
        return pd.read_csv(
            filepath_or_buffer=filename,
            sep=",",
            skip_blank_lines=True,
            header=[2, 3],
        )

    def set_df(self, other):
        self.df = other

    def _read_dataframe(self, columns, grain):
        try:
            df = self.df[columns]
        except KeyError as e:
            raise DStatReadColumnsException(e.message)
        if grain:
            df = self._partition_time(df)
        return df

    @staticmethod
    def _partition_time(df):
        start = df['epoch'].iloc[0][0]
        end = df['epoch'].iloc[-1][0]
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
                ret = df[(df.epoch.epoch > final_start) & (df.epoch.epoch < final_end)]
                return ret



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
        print outname + ' created'

    def plot_together(self, plot=False):
        """
        This method plots all value in the second level of the column in one graph, no stacked lines
        :param plot:
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
            for col in columns:
                save_title += (col + '-')
            name = save_title + 'stacked'
            self.save(name)
            plt.close()

    def _set_unit(self, compare=None):
        name = compare if compare is not None else self.name
        if name == 'total cpu usage' or name == 'cpu' or name.startswith('cpu'):
            return "percentage"
        elif name.startswith('net/') or name == 'network':
            return "bandwidth [MBps]"
        elif name.startswith('dsk/') or name == 'disk':
            return '#count'
        else:
            return "memory usage [MB]"

    def _set_layout(self, ax):
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