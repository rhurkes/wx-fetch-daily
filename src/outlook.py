import re
import requests

OUTLOOK_BASE = 'http://www.spc.noaa.gov/products/outlook/archive/'
OUTLOOK_PATTERN = r'\.{3} (.+) \.{3}\n\n([\d|\s|.|A-Z]+)*&&'
OUTLOOK_PTS_PATTERN = r'(\S+)\s{3}((\d+\s+)+)'

def process(day, time):
    """Downloads, parses, and return JSON data"""
    year = day.strftime('%Y')
    spcdate = year + day.strftime('%m%d')
    url = OUTLOOK_BASE + year + '/KWNSPTSDY1_' + spcdate + time + '.txt'
    response = requests.get(url)
    return parse(response.text, url)

def parsenwspt(text):
    """Parses a line of NWS points representing a polygon"""
    lat = int(text[0:4]) / 100
    lon = int(text[4:])
    if lon < 1000:
        lon += 10000
    return (lon / -100, lat)

def getpolycenter(poly):
    """Gets center of a polygon"""
    polylength = len(poly)

    return (
        round(sum(x for x, y in poly) / polylength, 2),
        round(sum(y for x, y in poly) / polylength, 2)
    )

def parseoutlookpts(text):
    """parses a line into points"""
    groupdict = {}
    for match in re.finditer(OUTLOOK_PTS_PATTERN, text):
        section = match.group(1)
        pts = match.group(2)
        groupdict[section] = {'points': []}
        for innermatch in re.finditer(r'\d+', pts):
            if innermatch.group(0) != '99999999':
                parsedpts = parsenwspt(innermatch.group(0))
                groupdict[section]['points'].append(parsedpts)
        groupdict[section]['center'] = getpolycenter(groupdict[section]['points'])
    return groupdict

def parse(text, url):
    """parses an outlook"""
    lines = text.split('\n')
    parsedoutlook = {'probabilistic': {}, 'categorical': {}}
    parsedoutlook['originURL'] = url
    parsedoutlook['description'] = lines[1]
    parsedoutlook['issuer'] = lines[2]
    parsedoutlook['timestamp'] = lines[3]
    for match in re.finditer(OUTLOOK_PATTERN, text):
        group = match.group(1)
        ptsdata = match.group(2)
        if group == 'TORNADO':
            parsedoutlook['probabilistic']['tornado'] = parseoutlookpts(ptsdata)
        elif group == 'HAIL':
            parsedoutlook['probabilistic']['hail'] = parseoutlookpts(ptsdata)
        elif group == 'WIND':
            parsedoutlook['probabilistic']['wind'] = parseoutlookpts(ptsdata)
        elif group == 'CATEGORICAL':
            parsedoutlook['categorical'] = parseoutlookpts(ptsdata)
    return parsedoutlook
