#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import csv

import datetime

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as tick

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
            self.filename = ''
            self.device = None
            self._set_name(name)
        except Exception as e:
            raise DStatOpenCsvException(str(type(e)) + ': ' + e.message)
        try:
            self._to_datetime()
            self._drop_oversampled()
        except Exception as e:
            raise DStatDateTimeConversionException(str(type(e)) + ': ' + e.message)
        try:
            self._fix_columns()
        except Exception as e:
            raise DStatFixColumnsException(str(type(e)) + ': ' + e.message)

    def _set_name(self, name):
        if isinstance(name, list):  # comparison object construction
                temp = ''
                for s in name:
                    for ch in [" ", "/"]:
                        if ch in s:
                            s = s.replace(" ", "")
                            s = s.replace("/", "")
                    temp += (s + "-")
                self.name = temp[:-1]
        else:
            self.name = name

    def __eq__(self, other):
        return self.df.equals(other)

    def _open_csv(self, filename):
        header, to_skip = self._check_csv(filename)
        df = pd.read_csv(
            filepath_or_buffer=filename,
            sep=",",
            skiprows=to_skip,
            header=header,
            error_bad_lines=False,
            warn_bad_lines=False,
        )
        # df.columns = pd.MultiIndex.from_tuples(self._compute_default_cols())
        return df

    def _drop_oversampled(self):
        self.df = self.df.drop_duplicates(subset=('epoch','epoch'), keep='first')

    @staticmethod
    def _get_iter(iterr):
        ret = None
        for x in iterr:
            try:
                ret = x[0]
            except IndexError:
                ret = ''
            break
        if ret is None:
            raise StopIteration
        return ret if ret is not None else ''

    def _check_csv(self, filename):
        with open(filename, 'rb') as csvfile:
            print filename
            ok, skip = self._parse_raw(csvfile)
            csvfile.close()
        return ok, skip

    def _parse_raw(self, csvfile):
        """
        Two index identifiers are needed due to pandas.csv_read method
        f_idx points to rows that set columns
        idx points to line to be skipped
        pandas.read_csv method get a two steps parsing, first skip lines and then analyze file
        """
        raw = csv.reader(csvfile, delimiter=',')
        header = []
        skip = []
        idx = 0
        f_idx = 0
        while True:
            try:
                value = self._get_iter(raw)  # the iterator compute next line
                idx += 1
                f_idx += 1
                if value == 'epoch' and not len(header):
                    # header is provided
                    header = [f_idx - 1, f_idx]
                    next(raw)
                    idx += 1
                    f_idx += 1
                    continue
                elif not len(value) or re.match('^[0-9\.]+$', value) is None:
                    skip.append(idx-1)
                    f_idx -= 1
            except StopIteration:
                return header, skip

    @staticmethod
    def _compute_default_cols():
        cpus = ['usr','sys', 'idl', 'wai', 'hiq', 'siq']
        mems = ['used','buff','cach','free']
        nets = ['send', 'recv']
        dsk = ['read', 'writ']
        l = list()

        l.append(('epoch', 'epoch'))
        for x in range(6):
            l.append(('total cpu usage', cpus[x]))

        for y in range(15):
            for x in range(6):
                l.append(('cpu' + str(y+1) + ' usage', cpus[x]))

        for x in range(4):
            l.append(('memory usage', mems[x]))

        for x in range(2):
            l.append(('net/total', nets[x]))
        for x in range(2):
            l.append(('net/eth0', nets[x]))

        for x in range(2):
            l.append(('dsk/total',dsk[x]))

        for y in range(5):
            for x in range(2):
                l.append(('dsk/sd' + chr(ord('a') + y), dsk[x]))

        return l

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
        # self.df['epoch', 'epoch'] *= 1000 # that instruction needs unit option equal to 'ms' on below instruction
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
        self._set_ticks_units(ax)
        if plot:
            plt.show()
        else:
            self.save(save_title + "line")
            plt.close()

    def _set_ticks_units(self, ax):
        if self.name == 'disk':
            y_formatter = tick.FormatStrFormatter('%1.2f MB')
            ax.yaxis.set_major_formatter(y_formatter)

    def plot_stacked(self, columns=None, plot=False):
        """

        :param columns:
        :param plot:
        :return:
        """
        plot_title, save_title = self._get_titles()

        ax = self.df.plot.area(stacked=False, x='epoch', y=columns, title=plot_title)

        self._set_layout(ax)
        self._set_ticks_units(ax)

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
            return "bandwidth [Mbps]"
        elif name.startswith('dsk/') or name == 'disk':
            return 'disk volume usage [MB]'
        else:
            return "memory usage [GB]"

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
