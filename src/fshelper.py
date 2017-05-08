"""Various functions to help interact with the filesystem"""

import json
import os
import errno

def loaddata(path):
    """Loads JSON file from filesystem as Python object"""
    with open(path) as jsondata:
        return json.load(jsondata)

def savedata(path, filename, data):
    """Writes data to file"""
    with open(path + '/' + filename, 'w') as openedfile:
        json.dump(data, openedfile, sort_keys=True, indent=2, ensure_ascii=False)

def safedirs(path):
    """Safely creates all directories in a path if they don't exist"""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
