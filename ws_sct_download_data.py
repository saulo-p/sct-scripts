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

def main(key_name, dest_folder, url_dict_dir, unzip=True):
    with open(os.path.join(url_dict_dir,'urls.pickle'), 'rb') as fin:
        dict_url = pickle.load(fin)

    url = dict_url[key_name]
    install_data(url, dest_folder, unzip)

    return 0


if __name__ == "__main__":
    args = iter(sys.argv[1:])

    # mandatory arguments
    try:
        key_name = next(args)
        dest_folder = next(args)
        url_dict_dir = next(args)
    except StopIteration:
        print ("Not enough arguments")
        exit(1)

    try:
        #optional arguments
        output_zip = next(args)
    except StopIteration:
        res=main(key_name, dest_folder, url_dict_dir)
    else:
        if output_zip == 'z':
            res=main(key_name, dest_folder, url_dict_dir, False)
        else:
            res=main(key_name, dest_folder, url_dict_dir)

    raise SystemExit(res)
