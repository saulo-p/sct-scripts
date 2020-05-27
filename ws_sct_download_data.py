#!/usr/bin/env python
##############################################################################
#
# Download data using http.
#
# ----------------------------------------------------------------------------
# Copyright (c) 2015 Polytechnique Montreal <www.neuro.polymtl.ca>
# Author: Julien Cohen-Adad
#
# About the license: see the file LICENSE.TXT
###############################################################################

from __future__ import absolute_import

import os
import sys

from ws_download_data import install_data

import pickle

def main(data_name, dest_folder, unzip=True):
    with open('/home/saulo/Work/exmakhina/poly/workspace/tmp/urls.pickle', 'rb') as fin:
        dict_url = pickle.load(fin)

    url = dict_url[data_name]
    install_data(url, dest_folder, unzip)

    return 0


if __name__ == "__main__":
    data_name = sys.argv[1]
    dest_folder = sys.argv[2]

    if sys.argv[3] == 'z':
        res=main(data_name, dest_folder, False)
    else:
        res=main(data_name, dest_folder)

    raise SystemExit(res)
