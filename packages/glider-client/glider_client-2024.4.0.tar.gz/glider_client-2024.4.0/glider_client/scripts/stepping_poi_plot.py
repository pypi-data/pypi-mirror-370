# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

import os.path
from argparse import ArgumentParser

from matplotlib import pyplot
import numpy


def run():
    parser = ArgumentParser()
    parser.add_argument('files', nargs='+', type=str,
                        help='csv files containing the stepping POI')

    args = parser.parse_args()
    for fp in args.files:
        if not os.path.exists(fp):
            parser.error('file {} does not exist'.format(fp))
    stepping_poi_plot(args.files)

def stepping_poi_plot(files):
    for fp in files:
        n = numpy.loadtxt(fp, delimiter=',', usecols=[0, 1, 2, 3, 6])
        wn = n[:, 0]
        analog1 = n[:, 1]/n[:, 3]
        analog2 = n[:, 2]/n[:, 3]
        pyplot.plot(wn, analog1, label=os.path.basename(fp))
        pyplot.plot(wn, analog2 , label=os.path.basename(fp))
        has_errors = [bool(x) for x in n[:, 4]]
        if [x for x in has_errors if x]:
            pyplot.plot(wn[has_errors], analog1[has_errors], 'rx')
            pyplot.plot(wn[has_errors], analog2[has_errors], 'rx')


    pyplot.legend()
    pyplot.show()


if __name__ == '__main__':
    run()




