#!/usr/bin/env python

import os
import urllib2
import urlparse
import zipfile

root_directory = os.path.join(os.environ['HOME'], '.esp32vm')
esp_idf_baseurl = 'https://github.com/espressif/esp-idf/archive/'

def download_file(url, out_file=None):
    """
    Download file from an URL to current directory.
    If out_file is provided, then it will be used as the output filename
    """

    filedata = urllib2.urlopen(url)
    datatowrite = filedata.read()

    parsed = urlparse.urlparse(url)
    output = None
    if out_file:
        output = out_file
    else:
        output = parsed.path.split('/').pop()

    with open(output, 'wb') as fopen:
        fopen.write(datatowrite)

def create_root_dir():
    """
    Initialize the version manager by creating the root directory for ESP-IDF
    """

    if not os.path.isdir(root_directory):
        os.mkdir(root_directory, 0755)

        return True

    return False

def download_idf(idf_revision, output_dir):
    """
    Download ESP-IDF with specified revision to a directory
    """

    download_url = '%s%s.zip' % (esp_idf_baseurl, idf_revision)
    zip_output_filename = '%s.zip' % idf_revision
    zip_output_path = os.path.join(output_dir, zip_output_filename)

    extracted_dir = None
    if idf_revision[0] == 'v':
        extracted_dir = 'esp-idf-%s' % idf_revision[1:]
    else:
        extracted_dir = 'esp-idf-%s' % idf_revision

    extracted_dir = os.path.join(output_dir, extracted_dir)

    if os.path.exists(zip_output_path):
        if os.path.exists(extracted_dir):
            print('ESP-IDF revision %s is already installed' %idf_revision)
            os.unlink(zip_output_path)
            return True
        else:
            zip_file = zipfile.ZipFile(zip_output_path)
            zip_file.extractall(output_dir)
            os.unlink(zip_output_path)
            return True
    else:
        if os.path.exists(extracted_dir):
            print('ESP-IDF revision %s is already installed' %idf_revision)
            return True
        else:
            download_file(download_url, zip_output_path)
            zip_file = zipfile.ZipFile(zip_output_path)
            zip_file.extractall(output_dir)
            os.unlink(zip_output_path)
            return True
    return False

def create_env(name, idf_revision):
    """
    Create ESP32 environment on home directory.
    """

    if not os.path.isdir(root_directory):
        create_root_dir()

    fullpath = os.path.join(root_directory, name)

    if os.path.isdir(fullpath):
        print('Environment %s is already exists' % name)
        return True
    else:
        os.mkdir(fullpath)

    download_idf(idf_revision, fullpath)

    return True
