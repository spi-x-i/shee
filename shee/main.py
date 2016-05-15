#!/usr/bin/env python
# -*- coding: utf-8 -*

import os

import numpy as np

import pandas as pd
import matplotlib as mp
import matplotlib.pyplot as plt
import time

from DStatFrame import DStatCpu
from DStatFrame import DStatMemory
from DStatFrame import DStatNetwork

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
            start_time = time.time()
            print "executing : " + fullname
            if 1 == 0:
                ######################################
                #################CPU##################
                ds = DStatCpu(fullname, "cpu")

                dn = fullname.split('.')[0]
                if not os.path.exists(dn):
                    os.makedirs(dn)

                cpudir = dn + "/cpu"
                if not os.path.exists(cpudir):
                    os.makedirs(cpudir)

                ds.plot_together()
                ds.subplot_all(True)
                ds.plot_stacked(columns=['usr', 'sys', 'idl'])

                # TODO: fare qualcosa di meglio qua è doveroso, un while true dove finchè ci sono cpu da leggere si leggono
                num_cpu = 15
                for n in np.arange(1,(num_cpu + 1)):
                    ndir = cpudir + "/cpu" + str(n)
                    if not os.path.exists(ndir):
                        os.makedirs(ndir)

                    ds = DStatCpu(fullname, "cpu", cpu=n)
                    ds.plot_together()
                    ds.subplot_all(True)
                    ds.plot_stacked(columns=['usr', 'sys', 'idl'])
                ####################################
                ####################################
            else:
                ##########################################
                #################NETWORK##################
                ds = DStatNetwork(fullname, "network")

                dn = fullname.split('.')[0]
                if not os.path.exists(dn):
                    os.makedirs(dn)

                netdir = dn + "/network"
                if not os.path.exists(netdir):
                    os.makedirs(netdir)

                ds.plot_together()
                ds.subplot_all()
                ds.plot_stacked(columns=['send','recv'])

                # TODO: fare qualcosa di meglio qua è doveroso, un while true dove finchè ci sono cpu da leggere si leggono
                num_eth = 1
                for n in np.arange(0,(num_eth)):

                    ndir = netdir + "/eth" + str(n)
                    if not os.path.exists(ndir):
                        os.makedirs(ndir)

                    ds = DStatNetwork(fullname, "network", eth=n)

                    ds.plot_together()
                    ds.subplot_all()
                    ds.plot_stacked(columns=['send','recv'])
                ##########################################
                ##########################################

                ##########################################
                ##################### MEMORY #############

                ds = DStatMemory(fullname, "memory")

                dn = fullname.split('.')[0]
                if not os.path.exists(dn):
                    os.makedirs(dn)

                memdir = dn + "/memory"
                if not os.path.exists(memdir):
                    os.makedirs(memdir)

                ds.plot_together()
                ds.subplot_all()
                ds.plot_stacked(columns=['used','buff','cach','free'], plot=False)
                # qui non c'è l'esigenza di inserire una ricorsione sui vari device, il contatore è unico

                ##########################################
                ############ COMPAIRASON #################





            print fn + " analysis completed.(Execution time: %s secs" % (time.time() - start_time) + ")"

        else:
            print "%s is not a file" % fn




