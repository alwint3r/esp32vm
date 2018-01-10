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


def create_env(name, idf_revision):
    """
    Create ESP32 environment on home directory.
    """

    if not os.path.isdir(root_directory):
        create_root_dir()

    fullpath = os.path.join(root_directory, name)
    output_filename = '%s.zip' % idf_revision
    download_url = '%s%s.zip' % (esp_idf_baseurl, idf_revision)

    if os.path.isdir(fullpath):
        print('Environment %s is already exists' % name)
    else:
        os.mkdir(fullpath)
    out_path = os.path.join(fullpath, output_filename)

    if not os.path.exists(out_path):
        download_file(download_url, out_path)

    if idf_revision[0] == 'v':
        extracted_dir = 'esp-idf-%s' % idf_revision[1:]
    else:
        extracted_dir = 'esp-idf-%s' % idf_revision
    
    extracted_dir = os.path.join(fullpath, extracted_dir)

    if (os.path.exists(out_path) and not os.path.isdir(extracted_dir)) or (not os.path.exists(out_path) and not os.path.isdir(extracted_dir)):
        zip_file = zipfile.ZipFile(out_path)
        zip_file.extractall(fullpath)

        if not os.path.isdir(extracted_dir):
            print('Failed to extract ESP-IDF archive')
            return False
        else:
            os.unlink(out_path)

    elif (os.path.exists(out_path) and os.path.isdir(extracted_dir)) or (not os.path.exists(out_path) and os.path.isdir(extracted_dir)):
        print('ESP-IDF is already installed on %s environment!' % name)
        return True

    return True
