"""Fetches event HTML for a single day, and fires off MD/Watch requests"""

import fshelper
import re
import spcmd
import spcww
import requests

MD_PATTERN = r'href=\'(.+md\d{4}.html)\''
WW_PATTERN = r'href=\'(.+ww\d{4}.html)\''
URL_BASE = 'http://www.spc.noaa.gov/'

def processday(day):
    """TODO"""

    path = day.strftime('data/%Y/%m/%d')
    fshelper.safedirs(path)
    fshelper.safedirs(path + '/md')
    fshelper.safedirs(path + '/ww')
    url = 'http://www.spc.noaa.gov/exper/archive/leftmenu3.php?date=' + day.strftime('%Y%m%d')
    response = requests.get(url)
    mdurls = []
    wwurls = []

    for match in re.finditer(MD_PATTERN, response.text):
        mdurl = match.group(1).replace('../../', URL_BASE)
        mdurls.append(mdurl)
    spcmd.process(mdurls, path)

    for match in re.finditer(WW_PATTERN, response.text):
        wwurl = match.group(1).replace('../../', URL_BASE)
        wwurls.append(wwurl)
    spcww.process(wwurls, path)
