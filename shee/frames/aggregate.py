#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from ast import literal_eval

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from datetime import datetime


class DStatAggregate(object):
    def __init__(self, input_dir, dfs=None, save=False, filename=""):
        """
        The init function here should provide there ordered steps:
        - select overlapped dfs and save those in one aggregating df - selecting the following columns:
            . total cpu usage
            . net/total
            . memory usage
            . dsk/total
        Joining these columns needs to cover following rules:
        - dfs cols must be overlapped
        - dfs not present values must have a valid absent value
        :param dfs: list o hoef base dfs inside main directory
        :return:
        """
        if len(filename):
            self.filename = input_dir + '/' + filename
            self.df = self._read_csv(self.filename)

        elif dfs is not None:
            dfs = self._filter_dfs(dfs)
            dfs = self._add_multindex(dfs)
            self.filename = input_dir + '/' + self._set_filename(dfs)
            dfs = self._time_as_index(dfs) # returns dataframes
            df = self._join_dfs(dfs)
            df = self._drop_duplicates(df)
            df.to_csv(self.filename, tupleize_cols=True)
            if not save:
                self.df = self._read_csv(self.filename)

    def plot_stacked_avg(self, plot=False):
        # groupy = self.df.groupby('epoch', axis=0, level=1)
        item = self.df.stack(level=1)
        item.describe()

    def _set_filename(self, dfs):
        ret = ""
        for df in dfs:
            ret += '-'.join(df.name.split('-')[-2:])
            ret += '-'
        return ret[:-1] + '.csv'

    def _read_csv(self, filename):
        df = pd.read_csv(filename,
                         sep=',',
                         header=0,
                         index_col=0,
                         tupleize_cols=True
                         )
        return self._reshape(df)

    @staticmethod
    def _reshape(df):
        tmp = df.columns.values
        cols = []
        for idx in range(0, len(tmp)):
            cols.append(literal_eval(tmp[idx]))
        df.columns = pd.MultiIndex.from_tuples(cols)
        return df

    @staticmethod
    def _drop_duplicates(df):
        # df = df - df['epoch'] # fake column inserted in _join_dfs
        to_drop = df.filter(regex="epoch")
        df.drop(to_drop.columns.values, axis=1, inplace=True)
        return df

    @staticmethod
    def _add_multindex(dfs):
        for df in dfs:
            cols = df.df.columns.values
            for idx in range(0,len(cols)):
                cols[idx] = (df.name.split('/')[-1],) + cols[idx]
            df.df.columns = cols
        return dfs

    def _join_dfs(self, dfs):
        left_df = self._create_left_df(dfs)
        left_df = left_df.join(dfs, how='left', rsuffix='_r', lsuffix='_l', )
        return left_df

    def _create_left_df(self, dfs):
        time = set()
        for df in dfs:
            for value in np.ndenumerate(df.index.values):
                time.add(value[1])
        sorted = list(time)
        sorted.sort()
        index = pd.Index(data=sorted, name='epoch')
        return pd.DataFrame(data=sorted, index=index, columns=['epoch'])

    @staticmethod
    def _time_as_index(dfs):
        items = [df.df.set_index(df.df[df.name.split('/')[-1], 'epoch', 'epoch']) for df in dfs]
        for item in items:
            item.index.name = 'epoch'
        return items

    @staticmethod
    def _filter_dfs(dfs):
        ret = set()
        for outer in dfs:
            found = False
            sout = set(outer.df['epoch','epoch'])
            for inner in dfs:
                if inner.df.equals(outer.df):
                    continue
                sin = set(inner.df['epoch','epoch'])
                if len(sout.intersection(sin)):
                    found = True
                    break
            if found:
                ret.add(outer)

        return list(ret)





    def save_csv(self):
        """
        This function should store in a new .csv the collected global df
        Csv format should be the same of dstat save csv format
        :return:
        """
        pass