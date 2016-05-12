#!/usr/bin/env python
# -*- coding: utf-8 -*

import os

import pandas as pd
import matplotlib.pyplot as plt

DIR = "/home/andrea/TESI/PYTHON/shee-project/shee/dstat"
def main():
    """
    The tool must provide following functions:
    when run, like shee, il tool parsa tutti i file .csv della directory corrente, crea una directory out e salva i
    grafici all'interno della stessa cartella
    :return:
    """

    # qualcosa tipo if not newdir
    dir ="/home/andrea/TESI/PYTHON/shee-project/shee/dstat/"

    # per ogni file .csv all'interno di questa cartella apro i file .csv
    for fn in os.listdir(dir):
        # d'ora in avanti il path deve essere assoluto
        fn = os.path.join(dir, fn)
        if os.path.isfile(fn):
            try:
                df = pd.read_csv(
                    filepath_or_buffer=fn,
                    sep=",",
                    skip_blank_lines=True,
                    header=[2,3],
                )
            except Exception as e:
                print "Not possible to open .csv  caused by %s" % e.message

            # convert unix timestamp to datetime param
            df['epoch', 'epoch'] = pd.to_datetime(df['epoch', 'epoch'], unit='s')

            # convert first outer column level due to read_csv bug
            df = fix_columns(df)

            plt.plot(df['epoch', 'epoch'], df['total cpu usage'])
            plt.show()


            break



        else:
            print "%s Not is a file" % fn


def fix_columns(df, level = 0, to_replace = 'Unnamed'):
    """
    Fix column method: replace columns unnamed values; needed for multi-indexing plotting

    :param df:
    :param level:
    :param to_replace:
    :return:
    """
    cols = df.columns.values
    replace_value = ""
    new_cols = {}

    for col in cols:
        if to_replace in col[level]:
            new_cols[col[level]] = replace_value
        else:
            replace_value = col[level]

    df.rename(columns=new_cols, inplace=True)

    return df




