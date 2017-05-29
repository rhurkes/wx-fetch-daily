"""Various functions to help interact with the filesystem"""

import json
import os
import errno
import shutil
import requests

def loaddata(path):
    """Loads JSON file from filesystem as Python object"""
    with open(path) as jsondata:
        return json.load(jsondata)

def gettmpfile(url, day, filename):
    """Downloads and caches a file to the tmp dir if necessary"""
    path = day.strftime('tmp/%Y/%m/%d/')
    safedirs(path)
    if not os.path.exists(path + filename):
        response = requests.get(url)
        with open(path + filename, 'wb') as out_file:
            out_file.write(response.content)
        return response.text
    else:
        with open(path + filename, 'r') as in_file:
            return in_file.read()

def savedata(path, filename, data):
    """Writes data to file"""
    with open(path + '/' + filename, 'w') as out_file:
        out_file.write(json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False))

def safedirs(path):
    """Safely creates all directories in a path if they don't exist"""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
