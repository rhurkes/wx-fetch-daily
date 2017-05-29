"""Downloads and processes Storm Data"""

from datetime import datetime, timedelta
import shutil
import csv
import os
import fipshelper
import fshelper
import pytz
import requests

URL = 'http://www.spc.noaa.gov/wcm/data/Actual_tornadoes.csv'
UTCZONE = pytz.timezone('US/Central')
TORCSV_PATH = 'tmp/tornado.csv'

def buildreport(line, utcdate, eventkey):
    report = {}
    report['timestamp'] = utcdate.strftime('%Y-%m-%dT%H:%M:%SZ')
    report['eventDate'] = eventkey
    report['state'] = fipshelper.getstatefromfips(line[8])
    report['fscale'] = int(line[10])
    report['injuries'] = int(line[11])
    report['fatalities'] = int(line[12])
    report['loss'] = float(line[13])
    report['cropLoss'] = float(line[14])
    report['startLat'] = float(line[15])
    report['startLon'] = float(line[16])
    report['endLat'] = float(line[17])
    report['endLon'] = float(line[18])
    report['lengthMiles'] = float(line[19])
    report['widthYards'] = int(line[20])
    return report

def parseasutc(line):
    """ TODO """
    # A timezone value of 3 means CST. Skip ones with unknown timezones: 0, 6, 9.
    if line[6] == '3':
        newdate = datetime.strptime(line[4] + line[5], '%Y-%m-%d%H:%M:%S')
        awaredatetime = UTCZONE.localize(newdate)
        return awaredatetime.astimezone(pytz.utc)

def downloadcsv():
    """Downloads SPC Storm Data for tornadoes if it doesn't exist"""
    fshelper.safedirs('tmp')
    response = requests.get(URL, stream=True)
    with open(TORCSV_PATH, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

def checkreports(day):
    path = day.strftime('data/%Y/%m/%d/')
    if not os.path.exists(path + 'reports.json'):
        fshelper.savedata(path, 'reports.json', {'tornadoes': []})

def savefiles(reportdays):
    """Saves JSON files"""
    for day in reportdays:
        currentdt = datetime.strptime(day, '%Y-%m-%d')
        path = currentdt.strftime('data/%Y/%m/%d')
        fshelper.safedirs(path)
        fshelper.savedata(path, 'reports.json', reportdays[day])

def process(startdate, enddate):
    """Processes SPC Storm Data for tornadoes.
    Empty files for non-event days are created elsewhere"""

    if not os.path.exists(TORCSV_PATH):
        downloadcsv()
    reportdays = {}
    reader = csv.reader(open(TORCSV_PATH, 'r'), delimiter=',')
    paddedenddate = enddate + timedelta(days=1, hours=12)

    for line in reader:
        utcdt = parseasutc(line)

        if utcdt is None or utcdt < startdate:
            continue
        elif utcdt > paddedenddate:
            break

        if int(utcdt.strftime('%H')) < 12:
            eventdt = utcdt - timedelta(days=1)
            eventkey = eventdt.strftime('%Y-%m-%d')
        else:
            eventkey = utcdt.strftime('%Y-%m-%d')

        if eventkey not in reportdays:
            reportdays[eventkey] = {'tornadoes': []}

        report = buildreport(line, utcdt, eventkey)
        reportdays[eventkey]['tornadoes'].append(report)
    savefiles(reportdays)
