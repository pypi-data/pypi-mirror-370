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
    scan_adc_delay_plot(args.files)


def scan_adc_delay_plot(files):
    for fp in files:
        n = numpy.loadtxt(fp, delimiter=',')
        pyplot.plot(n[:, 2], n[:, 0], label=os.path.basename(fp))
    pyplot.legend()
    pyplot.show()


if __name__ == '__main__':
    run()




