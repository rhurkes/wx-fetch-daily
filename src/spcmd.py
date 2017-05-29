"""Parser for SPC Mesoscale Discussions"""

import base64
from enum import Enum
import re
import fshelper
import nwshelper
import pytz
import requests

possibleval = 'CONCERNING...SEVERE POTENTIAL...WATCH POSSIBLE'
tornadolikelyval = 'CONCERNING...SEVERE POTENTIAL...TORNADO WATCH LIKELY'
unlikelyval = 'CONCERNING...SEVERE POTENTIAL...WATCH UNLIKELY'
neededval = 'CONCERNING...SEVERE POTENTIAL...WATCH NEEDED SOON'
likelyval = 'CONCERNING...SEVERE POTENTIAL...WATCH LIKELY'

BODY_PATTERN = r'<pre>([\s|\S]+)<\/pre>'
FORECASTER_PATTERN = r'\.\.(.+)\.\. \d\d'
PROBABILITY_PATTERN = r'(?i)PROBABILITY OF WATCH ISSUANCE\.{3}(\d+) PERCENT'
WFO_PATTERN = r'ATTN...WFO...(\w{3}...+)'
POINTS_PATTERN = r'[^\d+]+(\d{8})'
WATCHCONCERNING_PATTERN = r'(?i)CONCERNING\.{3}.+WATCH[\S|\s]+?VALID'
WATCHREF_PATTERN = r'ww(\d{4}).html'
WATCHPROB_PATTERN = r'(?i)PROBABILITY OF WATCH ISSUANCE...(\d{1,3}) PERCENT'
MD_BASE_URL = 'http://www.spc.noaa.gov/products/md/'

class MDType(Enum):
    WatchUnlikely = 1
    WatchPossible = 2
    WatchLikely = 3
    TornadoWatchLikely = 4
    WatchNeeded = 5
    WatchReference = 6
    Other = 7

def parseconcerningtext(body):
    """TODO"""
    result = {'type': MDType.Other.name, 'refs': []}
    concerningmatch = re.findall(WATCHCONCERNING_PATTERN, body)
    if len(concerningmatch) is 1:
        result['type'] = getmdtype(concerningmatch[0])
        watchrefs = re.findall(WATCHREF_PATTERN, concerningmatch[0])
        if len(watchrefs) > 0:
            result['type'] = MDType.WatchReference.name
            result['refs'] = [int(x) for x in watchrefs]
    return result


def getmdtype(text):
    """TODO"""
    if text.find(possibleval) > -1:
        return MDType.WatchPossible.name
    elif text.find(unlikelyval) > -1:
        return MDType.WatchUnlikely.name
    elif text.find(likelyval) > -1:
        return MDType.WatchLikely.name
    elif text.find(tornadolikelyval) > -1:
        return MDType.TornadoWatchLikely.name
    elif text.find(neededval) > -1:
        return MDType.WatchNeeded.name
    else:
        return MDType.Other.name

def buildmd(text):
    """Builds MD object from original HTML"""
    md = {}
    startpre = text.index('<pre>') + 5
    endpre = text.index('</pre>')
    body = text[startpre:endpre]
    lines = body.split('\n')
    mdid = lines[2].strip().replace('MESOSCALE DISCUSSION ', '')
    md['id'] = mdid
    utcdt = nwshelper.getutc(lines[4].strip())
    md['timestamp'] = nwshelper.toisostring(utcdt)
    url = MD_BASE_URL + str(utcdt.year) + '/mcd' + mdid + '.gif'
    md['forecasters'] = re.findall(FORECASTER_PATTERN, body)[0].split('/')
    probability = re.findall(PROBABILITY_PATTERN, body)
    if len(probability) > 0:
        md['probability'] = int(probability[0])
    md['wfos'] = list(filter(None, re.findall(WFO_PATTERN, body)[0].split('...')))
    points = re.findall(POINTS_PATTERN, body)
    mdpoints = []
    for pointstring in points:
        mdpoints.append(nwshelper.parsenwspt(pointstring))
    md['points'] = mdpoints
    md['center'] = nwshelper.getpolycenter(mdpoints)
    parsedconcering = parseconcerningtext(body)
    md['type'] = parsedconcering['type']
    md['referencedWatches'] = parsedconcering['refs']
    match = re.findall(WATCHPROB_PATTERN, text)
    if len(match) > 0:
        md['watchProbability'] = int(match[0])
    else:
        md['watchProbability'] = None
    md['raw'] = body.strip()

    # Get base64 image data
    response = requests.get(url)
    #if response.status_code == requests.codes.ok:
        #md['imageData'] = base64.b64encode(response.content)
    return md

def process(mdurls, path):
    """TODO"""
    for url in mdurls:
        response = requests.get(url)
        md = buildmd(response.text)
        fshelper.savedata(path + '/md', md['id'] + '.json', md)
