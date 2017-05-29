"""Parser for SPC Watches"""

import base64
import re
import fshelper
import nwshelper
import requests

PROB_PATTERN = r'(\d{1,3})% probability'
MDREF_PATTERN = r'/md(\d{4}).html'
POLY_PATTERN = r'\d{8} \d{8} \d{8} \d{8}'

def getidfromurl(url):
    """Returns string ID from URL"""
    matches = re.findall(r'ww(\d{4}).html', url)
    return matches[0]

def parsebody(body):
    """TODO"""
    result = {'isPDS': False}
    normalizedbody = body.lower()
    if normalizedbody.find('particularly dangerous situation') > -1:
        result['isPDS'] = True
    return result

def buildww(text, wwid):
    """TODO"""
    watch = {'id': wwid}
    startpre = text.index('<pre>') + 5
    endpre = text.index('</pre>')
    body = text[startpre:endpre].strip()
    watch['raw'] = body
    lines = body.split('\n')
    subjectline = lines[3].lower()

    if subjectline.find('severe thunderstorm watch') > -1:
        watch['type'] = 'SevereThunderstorm'
    elif subjectline.find('tornado watch') > -1:
        watch['type'] = 'Tornado'
    else:
        raise Exception('UNKNOWN WATCH TYPE')

    utcdt = nwshelper.getutc(lines[5].strip())
    watch['timestamp'] = nwshelper.toisostring(utcdt)
    watch['forecasters'] = [lines[len(lines) - 1].replace('...', '').strip()]

    parsedbody = parsebody(body)
    watch['isPDS'] = parsedbody['isPDS']

    # Watch polys are assumed to always have 4 vertices
    matches = re.findall(POLY_PATTERN, text)
    points = matches[0].split(' ')
    watch['points'] = [nwshelper.parsenwspt(x) for x in points]

    # probabilities
    starttbody = text.index('<tbody>') + 7
    endtbody = text.index('</tbody>')
    tbody = text[starttbody:endtbody].strip()
    probmatches = re.findall(r'title=\'(.+)\'', tbody)
    watch['torPercent'] = int(re.findall(PROB_PATTERN, probmatches[2])[0])
    watch['sigTorPercent'] = int(re.findall(PROB_PATTERN, probmatches[3])[0])
    watch['windPercent'] = int(re.findall(PROB_PATTERN, probmatches[6])[0])
    watch['sigWindPercent'] = int(re.findall(PROB_PATTERN, probmatches[7])[0])
    watch['hail'] = int(re.findall(PROB_PATTERN, probmatches[10])[0])
    watch['sigHailPercent'] = int(re.findall(PROB_PATTERN, probmatches[11])[0])

    # related MD
    matches = re.findall(MDREF_PATTERN, text)
    if len(matches) > 0:
        watch['mdReference'] = int(matches[0])

    # Get base64 image data
    #imgurl = 'http://www.spc.noaa.gov/products/watch/' + str(utcdt.year) + '/ww' + wwid + '_radar_init.gif'
    #response = requests.get(imgurl)
    #if response.status_code == requests.codes.ok:
    #    watch['imageData'] = base64.b64encode(response.content)
    return watch

def process(wwurls, path):
    """TODO"""
    for url in wwurls:
        response = requests.get(url)
        wwid = getidfromurl(url)
        ww = buildww(response.text, wwid)
        fshelper.savedata(path + '/ww', wwid + '.json', ww)
