import json
import os
import errno

def savedata(path, filename, data):
    """Writes data to file"""
    with open(path + '/' + filename, 'w') as openedfile:
        json.dump(data, openedfile, sort_keys=True, indent=2, ensure_ascii=False)

def safedirs(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
