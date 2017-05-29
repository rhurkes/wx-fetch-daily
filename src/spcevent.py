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
    fshelper.safedirs(path + '/md')
    fshelper.safedirs(path + '/ww')
    url = 'http://www.spc.noaa.gov/exper/archive/leftmenu3.php?date=' + day.strftime('%Y%m%d')
    eventfile = fshelper.gettmpfile(url, day, 'spcevent.html')
    mdurls = []
    wwurls = []

    for match in re.finditer(MD_PATTERN, eventfile):
        mdurl = match.group(1).replace('../../', URL_BASE)
        mdurls.append(mdurl)
    spcmd.process(mdurls, path, day)

    for match in re.finditer(WW_PATTERN, eventfile):
        wwurl = match.group(1).replace('../../', URL_BASE)
        wwurls.append(wwurl)
    spcww.process(wwurls, path, day)
