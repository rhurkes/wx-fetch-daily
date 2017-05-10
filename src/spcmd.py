# http://www.spc.noaa.gov/exper/archive/event.php?date=20100617
# get list of MDs
# get list of watches
# for each MD:
#   ID, Image as base64 data, timestamp, forecaster, polygon, valid, raw text, wfos


possibleval = 'CONCERNING...SEVERE POTENTIAL...WATCH POSSIBLE'
tornadolikelyval = 'CONCERNING...SEVERE POTENTIAL...TORNADO WATCH LIKELY'
unlikelyval = 'CONCERNING...SEVERE POTENTIAL...WATCH UNLIKELY'
neededval = 'CONCERNING...SEVERE POTENTIAL...WATCH NEEDED SOON'
likelyval = 'CONCERNING...SEVERE POTENTIAL...WATCH LIKELY'

#CONCERNING...SEVERE THUNDERSTORM WATCH 332...

#CONCERNING...TORNADO WATCH 333...
#CONCERNING...TORNADO WATCH 334...335...338...
#CONCERNING...FREEZING RAIN 
#CONCERNING...WINTER MIXED PRECIPITATION 

import base64
from enum import Enum
import re
import nwshelper
import pytz
import requests

BODY_PATTERN = r'<pre>([\s|\S]+)<\/pre>'
FORECASTER_PATTERN = r'\.\.(.+)\.\. \d\d'
PROBABILITY_PATTERN = r'PROBABILITY OF WATCH ISSUANCE\.{3}(\d+) PERCENT'
WFO_PATTERN = r'ATTN...WFO...(\w{3}...+)'
POINTS_PATTERN = r'[^\d+]+(\d{8})'
MD_BASE_URL = 'http://www.spc.noaa.gov/products/md/'

class MDType(Enum):
    WatchUnlikely = 1
    WatchPossible = 2
    WatchLikely = 3
    TornadoWatchLikely = 4
    WatchNeeded = 5
    WatchReference = 6
    Other = 7

def getmdtype(body):
    """TODO"""
    if body.find(possibleval) > -1:
        return MDType.WatchPossible
    elif body.find(unlikelyval) > -1:
        return MDType.WatchUnlikely
    elif body.find(likelyval) > -1:
        return MDType.WatchLikely
    elif body.find(tornadolikelyval) > -1:
        return MDType.TornadoWatchLikely
    elif body.find(neededval) > -1:
        return MDType.WatchNeeded
    else:
        return MDType.Other
    #TODO references


def buildmd(text):
    """Builds MD object from original HTML"""
    md = {}

    startpre = text.index('<pre>') + 5
    endpre = text.index('</pre>')
    body = text[startpre:endpre]
    lines = body.split('\n')
    mdid = lines[2].strip().replace('MESOSCALE DISCUSSION ', '')
    md['id'] = int(mdid)
    utcdt = nwshelper.getutc(lines[4].strip())
    md['timestamp'] = nwshelper.toisostring(utcdt)
    url = MD_BASE_URL + str(utcdt.year) + '/mcd' + mdid + '.gif'
    md['forecasters'] = re.findall(FORECASTER_PATTERN, body)[0].split('/')
    probability = re.findall(PROBABILITY_PATTERN, body)
    if len(probability) > 0:
        md['probability'] = int(probability[0])
    md['type'] = getmdtype(body).name
    md['wfos'] = list(filter(None, re.findall(WFO_PATTERN, body)[0].split('...')))
    attnposition = body.find('ATTN...WFO')
    points = re.findall(POINTS_PATTERN, body)
    #md['raw'] = body.strip()

    # valid start
    # valid end
    # polygon
    # center
    # watch probability
    # raw text
    
    print(md)

    # Get base64 image data
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        md['imagedata'] = base64.b64encode(response.content)

def process(mdurls):
    """TODO"""
    for url in mdurls:
        response = requests.get(url)
        buildmd(response.text)

process(['http://www.spc.noaa.gov/products/md/2010/md0983.html'])
