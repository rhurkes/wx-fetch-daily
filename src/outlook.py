from datetime import timedelta
import os
import re
import requests
import fshelper
import nwshelper
import zipfile
import geopandas as gp
from datetime import datetime

# TODO calculate highest risk and highest prob for each risk type

OUTLOOK_BASE = 'http://www.spc.noaa.gov/products/outlook/archive/'
OUTLOOK_PATTERN = r'\.{3} (.+) \.{3}\n\n([\d|\s|.|A-Z]+)*&&'
OUTLOOK_PTS_PATTERN = r'(\S+)\s+((\d+\s+)+)'

def process(day, time):
    """Downloads, parses, and return JSON data"""
    year = day.strftime('%Y')
    spcdate = year + day.strftime('%m%d')
    filename = '/KWNSPTSDY1_' + spcdate + time + '.txt'
    url = OUTLOOK_BASE + year + filename
    outlookfile = fshelper.gettmpfile(url, day, filename, True)
    return parse(outlookfile, url, spcdate, time)

def processday2(prevday, day, time):
    """Downloads, parses, and returns JSON data for a Day 2 outlook"""
    year = prevday.strftime('%Y')
    spcdate = year + prevday.strftime('%m%d')
    filename = '/KWNSPTSDY2_' + spcdate + time + '.txt'
    url = OUTLOOK_BASE + year + filename
    outlookfile = fshelper.gettmpfile(url, day, filename, True)
    return parse(outlookfile, url, spcdate, time)

def getcentroids(outlook):
    """TODO"""
    producttime = outlook['producttime']
    day = datetime.strptime(outlook['spcdate'], '%Y%m%d')
    path = day.strftime('tmp/%Y/%m/%d/shapefiles')
    for wxtype in ('tornado', 'wind', 'hail'):
        if wxtype == 'tornado':
            shp_suffix = '_torn.shp'
        if wxtype == 'wind':
            shp_suffix = '_wind.shp'
        if wxtype == 'hail':
            shp_suffix = '_hail.shp'
        if wxtype == 'categorical':
            shp_suffix = '_cat.shp'
        shapefile_path = path + '/day1otlk_' + outlook['spcdate'] + '_' + producttime + shp_suffix
        if os.path.exists(shapefile_path):
            shapefile = gp.read_file(shapefile_path)
            for prob in ('0.60', '0.45', '0.30', '0.15', '0.10', '0.05', '0.02', 'SIGN'):
                if prob in outlook['probabilistic'][wxtype]:
                    if not prob == 'SIGN':
                        intprob = int(prob[-2:])
                    data = shapefile[shapefile['DN'] == intprob].to_crs(epsg=4326) # WGS 84
                    if len(data) > 0:
                        # TODO this currently only stores the last if there's multiple area polygons
                        for index, row in data.iterrows():
                            outlook['probabilistic'][wxtype][prob]['centroid'] = row['geometry'].centroid.coords[0]
            del shapefile

    shapefile_path = path + '/day1otlk_' + outlook['spcdate'] + '_' + producttime + '_cat.shp'
    if os.path.exists(shapefile_path):
        shapefile = gp.read_file(shapefile_path)
        cat_map = {
            'TSTM':2,
            'MGNL':3,
            'SLGT':4,
            'ENH':5,
            'MDT':6,
            'HIGH':8
        }
        for cat in cat_map:
            data = shapefile[shapefile['DN'] == cat_map[cat]].to_crs(epsg=4326)
            if len(data) > 0:
                # TODO this currently only stores the last if there's multiple risk areas with same category
                for index, row in data.iterrows():
                    if cat in outlook['categorical']:
                        outlook['categorical'][cat]['centroid'] = row['geometry'].centroid.coords[0]

        del shapefile
    return outlook

def sethighestrisk(outlook):
    """Gets and sets the highest risk for various sections of the outlook"""
    #TODO what happens when there are multiple polys with the same risk... can't use that as a key then
    for wxtype in ('tornado', 'wind', 'hail'):
        outlook['probabilistic'][wxtype]['max'] = None

        if '0.60' in outlook['probabilistic'][wxtype]:
            outlook['probabilistic'][wxtype]['max'] = '0.60'
        elif '0.45' in outlook['probabilistic'][wxtype]:
            outlook['probabilistic'][wxtype]['max'] = '0.45'
        elif '0.30' in outlook['probabilistic'][wxtype]:
            outlook['probabilistic'][wxtype]['max'] = '0.30'
        elif '0.15' in outlook['probabilistic'][wxtype]:
            outlook['probabilistic'][wxtype]['max'] = '0.15'
        elif '0.10' in outlook['probabilistic'][wxtype]:
            outlook['probabilistic'][wxtype]['max'] = '0.10'
        elif '0.05' in outlook['probabilistic'][wxtype]:
            outlook['probabilistic'][wxtype]['max'] = '0.05'
        elif '0.02' in outlook['probabilistic'][wxtype]:
            outlook['probabilistic'][wxtype]['max'] = '0.02'

    if 'HIGH' in outlook['categorical']:
        outlook['categorical']['max'] = 'HIGH'
    elif 'MDT' in outlook['categorical']:
        outlook['categorical']['max'] = 'MDT'
    elif 'ENH' in outlook['categorical']:
        outlook['categorical']['max'] = 'ENH'
    elif 'SLGT' in outlook['categorical']:
        outlook['categorical']['max'] = 'SLGT'
    elif 'MGNL' in outlook['categorical']:
        outlook['categorical']['max'] = 'MGNL'
    elif 'TSTM' in outlook['categorical']:
        outlook['categorical']['max'] = 'TSTM'
    #TODO No max found? test max for each of these?
    return outlook

def parseoutlookpts(text):
    """parses a line into points"""
    groupdict = {}
    for match in re.finditer(OUTLOOK_PTS_PATTERN, text):
        section = match.group(1)
        pts = match.group(2)
        groupdict[section] = {'points': []}
        for innermatch in re.finditer(r'\d+', pts):
            if innermatch.group(0) != '99999999':
                parsedpts = nwshelper.parsenwspt(innermatch.group(0))
                groupdict[section]['points'].append(parsedpts)
        groupdict[section]['center'] = nwshelper.getpolycenter(groupdict[section]['points'])
    return groupdict

def parse(text, url, spcdate, time):
    """parses an outlook"""
    lines = text.split('\n')
    parsedoutlook = {'probabilistic': {'tornado': {}, 'hail': {}, 'wind': {}}, 'categorical': {}}
    parsedoutlook['originURL'] = url
    parsedoutlook['description'] = lines[1]
    parsedoutlook['issuer'] = lines[2]
    parsedoutlook['timestamp'] = lines[3]
    parsedoutlook['spcdate'] = spcdate
    parsedoutlook['producttime'] = time

    for match in re.finditer(OUTLOOK_PATTERN, text):
        group = match.group(1)
        ptsdata = match.group(2)
        if ptsdata is not None:
            if group == 'TORNADO':
                parsedoutlook['probabilistic']['tornado'] = parseoutlookpts(ptsdata)
            elif group == 'HAIL':
                parsedoutlook['probabilistic']['hail'] = parseoutlookpts(ptsdata)
            elif group == 'WIND':
                parsedoutlook['probabilistic']['wind'] = parseoutlookpts(ptsdata)
            elif group == 'CATEGORICAL':
                parsedoutlook['categorical'] = parseoutlookpts(ptsdata)

    parsedoutlook = sethighestrisk(parsedoutlook)
    parsedoutlook = getcentroids(parsedoutlook)
    return parsedoutlook

def getshapefiles(day, time, isday2):
    """TODO"""
    # http://www.spc.noaa.gov/products/outlook/archive/2017/day2otlk_20170526_1700-shp.zip
    targetday = day if isday2 is False else day - timedelta(days=1)
    otlkday = 'day2otlk' if isday2 is True else 'day1otlk'
    path = day.strftime('tmp/%Y/%m/%d/')
    year = targetday.strftime('%Y')
    spcdate = year + targetday.strftime('%m%d')
    filename = '{}_{}_{}-shp.zip'.format(otlkday, spcdate, time)
    url = '{}/{}/{}'.format(OUTLOOK_BASE, year, filename)
    fshelper.gettmpfile(url, day, filename, False)
    fshelper.safedirs(path + '/shapefiles')
    tmpzip = zipfile.ZipFile(path + filename)
    tmpzip.extractall(path + '/shapefiles')
