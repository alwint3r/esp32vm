#!/usr/bin/env python

import os
import urllib2
import urlparse
import zipfile
import tarfile

root_directory = os.path.join(os.environ['HOME'], '.esp32vm')
esp_idf_baseurl = 'https://github.com/espressif/esp-idf/archive/'
toolchain_baseurl = 'https://dl.espressif.com/dl/'

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

    extracted_dir = get_idf_dir(idf_revision)

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

def get_toolchain_version(idf_revision):
    """
    Get xtensa esp32 toolchain version from esp-idf
    """

    idf_dir = get_idf_dir(idf_revision)
    if not os.path.isdir(idf_dir):
        raise Exception('ESP-IDF does not exists in %s environment!' % idf_revision)

    project_makefile = os.path.join(idf_dir, 'make/project.mk')
    if not os.path.exists(project_makefile):
        raise Exception('ESP-IDF project.mk does not exist in %s environment!' % idf_revision)

    opened_makefile = open(project_makefile, 'r')

    toolchain_version = None
    gcc_version = None

    for line in opened_makefile.readlines():
        if line.startswith('SUPPORTED_TOOLCHAIN_COMMIT_DESC'):
            splitted = line.split(':=')
            if len(splitted) < 2:
                pass
            toolchain_version = splitted[1]
            toolchain_version = toolchain_version.replace('crosstool-NG', '')
            toolchain_version = toolchain_version.replace('crosstool-ng-', '')
            toolchain_version = toolchain_version.strip()
        if line.startswith('SUPPORTED_TOOLCHAIN_GCC_VERSIONS'):
            splitted = line.split(':=')
            if len(splitted) < 2:
                pass
            gcc_version = splitted[1]
            gcc_version = gcc_version.strip()

    return (toolchain_version, gcc_version)

def download_xtensa_toolchain(idf_revision, output_dir):
    xtensa_version, gcc_version = get_toolchain_version(idf_revision)
    if not xtensa_version or not gcc_version:
        raise Exception('Failed to get toolchain version of %s' % idf_revision)
    
    toolchain_dir = 'xtensa-esp32-elf'
    output_filename = '%s-linux64-%s-%s.tar.gz' % (toolchain_dir, xtensa_version, gcc_version)
    output_path = os.path.join(output_dir, output_filename)
    extracted_dir = os.path.join(output_dir, toolchain_dir)

    if os.path.exists(output_path):
        if os.path.isdir(extracted_dir):
            print('xtensa esp32 toolchain is already installed for %s' % idf_revision)
            os.unlink(output_path)
            return True
        else:
            tar = tarfile.open(output_path, 'r:gz')
            tar.extractall(output_dir)
            tar.close()
            os.unlink(output_path)
            return True
    else:
        if os.path.isdir(extracted_dir):
            print('xtensa esp32 toolchain is already installed for %s' % idf_revision)
            return True
        else:
            toolchain_dl_url = '%s%s' % (toolchain_baseurl, output_filename)
            download_file(toolchain_dl_url, output_path)
            tar = tarfile.open(output_path, 'r:gz')
            tar.extractall(output_dir)
            tar.close()
            os.unlink(output_path)
            return True
    return False


def get_idf_dir(idf_revision):
    """
    Return path to ESP-IDF of an environment
    """

    env_dir = os.path.join(root_directory, idf_revision)
    ver = idf_revision[1:] if idf_revision[0] == 'v' else idf_revision

    return os.path.join(env_dir, 'esp-idf-%s' % ver)

def create_env(idf_revision):
    """
    Create ESP32 environment on home directory.
    """

    if not os.path.isdir(root_directory):
        create_root_dir()

    fullpath = os.path.join(root_directory, idf_revision)

    if os.path.isdir(fullpath):
        print('Environment %s is already exists' % idf_revision)
    else:
        os.mkdir(fullpath)

    download_idf(idf_revision, fullpath)
    download_xtensa_toolchain(idf_revision, fullpath)

    return True
