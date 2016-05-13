#!/usr/bin/env python
# -*- coding: utf-8 -*

import os

import pandas as pd
import matplotlib as mp
import matplotlib.pyplot as plt

from DStatFrame import DStatCpu

DIR = "/home/andrea/TESI/PYTHON/shee-project/shee/examples"

def main():
    """
    The tool must provide following functions:
    when run, like shee, il tool parsa tutti i file .csv della directory corrente, crea una directory out e salva i
    grafici all'interno della stessa cartella
    :return:
    """

    # qualcosa tipo if not newdir
    dir = DIR

    # per ogni file .csv all'interno di questa cartella apro i file .csv
    for fn in os.listdir(dir):
        # d'ora in avanti il path deve essere assoluto
        fullname = os.path.join(dir, fn)
        print fullname
        if os.path.isfile(fullname) and fn.startswith('dstat'):
            ds = DStatCpu(fullname)

            dn = fullname.split('.')[0]
            if not os.path.exists(dn):
                os.makedirs(dn)

            # metodo che plotta tutti i grafici uno per uno
            # ds.plot_all()
            # metodo che plotta tutto in un solo grafico
            ds.plot_together()
            # metodo che subplotta tutto in un solo grafico
            ds.subplot_all()

            ds.plot_stacked(columns=['usr', 'sys', 'idl'])
        else:
            print "%s Not is a file" % fn




