#!/usr/bin/env python

import os
import urllib2
import urlparse

root_directory = os.path.join(os.environ['HOME'], '.esp32vm')

def download_file(url):
    filedata = urllib2.urlopen(url)
    datatowrite = filedata.read()

    parsed = urlparse.urlparse(url)
    output = parsed.path.split('/').pop()

    with open(output, 'wb') as f:
        f.write(datatowrite)