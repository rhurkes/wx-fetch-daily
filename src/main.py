"""Simple script to fetch NWS text product data for multiple days in a range"""

from datetime import datetime, timedelta, timezone
import outlook
import spcevent
import stormdata
import fshelper
import kmlhelper

STARTDATETIME = datetime(2013, 5, 18, tzinfo=timezone.utc)
ENDDATETIME = datetime(2013, 5, 18, tzinfo=timezone.utc)

def fetchdailydata(day):
    """Fetches and processes all data for a specific day"""

    path = day.strftime('data/%Y/%m/%d')
    fshelper.safedirs(path)

    # Get day 2 outlook
    #TODO
    # prevday = day - delta(days=1)

    # Get day 1 13z
    outlook.getshapefiles(day, '1300')
    day113z = outlook.process(day, '1300')
    fshelper.savedata(path, 'outlook_1300.json', day113z)

    # Get day 1 1630z outlook
    outlook.getshapefiles(day, '1630')
    day11630z = outlook.process(day, '1630')
    fshelper.savedata(path, 'outlook_1630.json', day11630z)

    # Get day 1 20z outlook
    outlook.getshapefiles(day, '2000')
    day120z = outlook.process(day, '2000')
    fshelper.savedata(path, 'outlook_2000.json', day120z)

    # Get MDs and Watches
    spcevent.processday(day)

# Fetch and process bulk data, must be done first
print('Processing bulk data...')
stormdata.process(STARTDATETIME, ENDDATETIME)

# Fetch and process individual daily data
print('Processing individual daily data...')
CURRENT = STARTDATETIME
while CURRENT <= ENDDATETIME:
    print(CURRENT)
    fetchdailydata(CURRENT)
    stormdata.checkreports(CURRENT)
    kmlhelper.buildkml(CURRENT)
    CURRENT += timedelta(days=1)
