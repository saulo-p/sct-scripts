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

import pickle
import os
import sys
import shutil
import distutils.dir_util
import logging
import cgi
import tempfile
import urllib.parse
import tarfile
import zipfile
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry
from tqdm import tqdm
import datetime

logger = logging.getLogger(__name__)

def tmp_create(basename=None):
    """Create temporary folder and return its path
    """
    prefix = "sct-%s-" % datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f")
    if basename:
        prefix += "%s-" % basename
    tmpdir = tempfile.mkdtemp(prefix=prefix)
    logger.info("Creating temporary folder (%s)" % tmpdir)
    return tmpdir

def download_data(urls):
    """Download the binaries from a URL and return the destination filename
    Retry downloading if either server or connection errors occur on a SSL
    connection
    urls: list of several urls (mirror servers) or single url (string)
    """

    # make sure urls becomes a list, in case user inputs a str
    if isinstance(urls, str):
        urls = [urls]

    # loop through URLs
    exceptions = []
    for url in urls:
        try:
            logger.info('Trying URL: %s' % url)
            retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 503, 504])
            session = requests.Session()
            session.mount('https://', HTTPAdapter(max_retries=retry))
            response = session.get(url, stream=True)
            response.raise_for_status()

            filename = os.path.basename(urllib.parse.urlparse(url).path)
            if "Content-Disposition" in response.headers:
                _, content = cgi.parse_header(response.headers['Content-Disposition'])
                filename = content["filename"]

            # protect against directory traversal
            filename = os.path.basename(filename)
            if not filename:
                # this handles cases where you're loading something like an index page
                # instead of a specific file. e.g. https://osf.io/ugscu/?action=view.
                raise ValueError("Unable to determine target filename for URL: %s" % (url,))

            tmp_path = os.path.join(tempfile.mkdtemp(), filename)

            logger.info('Downloading: %s' % filename)

            with open(tmp_path, 'wb') as tmp_file:
                total = int(response.headers.get('content-length', 1))
                tqdm_bar = tqdm(total=total, unit='B', unit_scale=True, desc="Status", ascii=False, position=0)

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                        dl_chunk = len(chunk)
                        tqdm_bar.update(dl_chunk)

                tqdm_bar.close()
            return tmp_path

        except Exception as e:
            logger.warning("Link download error, trying next mirror (error was: %s)" % e)
            exceptions.append(e)
    else:
        raise Exception('Download error', exceptions)

def unzip(compressed, dest_folder):
    """
    Extract compressed file to the dest_folder. Can handle .zip, .tar.gz.
    """
    logger.info('Unzip data to: %s' % dest_folder)

    formats = {'.zip': zipfile.ZipFile,
               '.tar.gz': tarfile.open,
               '.tgz': tarfile.open}
    for format, open in formats.items():
        if compressed.lower().endswith(format):
            break
    else:
        raise TypeError('ERROR: The file %s is of wrong format' % (compressed,))

    try:
        open(compressed).extractall(dest_folder)
    except:
        print('ERROR: ZIP package corrupted. Please try downloading again.')
        raise


def install_data(url, dest_folder, do_unzip=True):
    """
    Download data from a URL and install in the appropriate folder. Deals with multiple mirrors, retry download,
    check if data already exist.
    :param url: string or list or strings. URL or list of URLs (if mirrors).
    :param dest_folder:
    :return:
    """

    # Download data
    tmp_file = download_data(url)

    if not do_unzip:
        shutil.copyfile(tmp_file, os.path.join(dest_folder,os.path.basename(tmp_file)))
        return

    # unzip
    dest_tmp_folder = tmp_create()
    unzip(tmp_file, dest_tmp_folder)
    extracted_files_paths = []
    # Get the name of the extracted files and directories
    extracted_files = os.listdir(dest_tmp_folder)
    for extracted_file in extracted_files:
        extracted_files_paths.append(os.path.join(os.path.abspath(dest_tmp_folder), extracted_file))

    # Check if files and folder already exists
    logger.info("Destination folder: {}".format(dest_folder))
    logger.info("Checking if folder already exists...")
    for data_extracted_name in extracted_files:
        fullpath_dest = os.path.join(dest_folder, data_extracted_name)
        if os.path.isdir(fullpath_dest):
            logger.warning("Folder {} already exists. Removing it...".format(data_extracted_name))
            shutil.rmtree(fullpath_dest)

    # Destination path
    # for source_path in extracted_files_paths:
        # Copy the content of source to destination (and create destination folder)
    distutils.dir_util.copy_tree(dest_tmp_folder, dest_folder)

    logger.info("Removing temporary folders...")
    try:
        shutil.rmtree(os.path.split(tmp_file)[0])
        shutil.rmtree(dest_tmp_folder)
    except Exception as error:
        logger.error("Cannot remove temp folder: " + repr(error))



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
