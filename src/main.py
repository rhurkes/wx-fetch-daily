"""Simple script to fetch NWS text product data for multiple days in a range"""

from datetime import date, datetime, timedelta, timezone
import outlook
import stormdata
import fshelper
import kmlhelper

STARTDATETIME = datetime(2010, 6, 17, 12, tzinfo=timezone.utc)
ENDDATETIME = datetime(2010, 6, 18, 12, tzinfo=timezone.utc)

def fetchdailydata(day):
    """Fetches and processes all data for a specific day"""

    path = day.strftime('data/%Y/%m/%d')
    fshelper.safedirs(path)

    # Get day 2 outlook
    #TODO

    # Get day 1 13z
    day113z = outlook.process(day, '1300')
    fshelper.savedata(path, 'outlook_1300.json', day113z)

    # Get day 1 1630z outlook
    day11630z = outlook.process(day, '1630')
    fshelper.savedata(path, 'outlook_1630.json', day11630z)

    # Get day 1 20z outlook
    day120z = outlook.process(day, '2000')
    fshelper.savedata(path, 'outlook_2000.json', day120z)

    # Get MDs
    #TODO

    # Get Watches
    #TODO

# Fetch and process bulk data first
stormdata.process(STARTDATETIME, ENDDATETIME)

# Fetch and process individual daily data
CURRENT = STARTDATETIME
while CURRENT <= ENDDATETIME:
    fetchdailydata(CURRENT)
    kmlhelper.buildkml(CURRENT)
    CURRENT += timedelta(days=1)
