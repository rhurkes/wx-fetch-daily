"""Simple script to fetch NWS text product data for multiple days in a range"""

from datetime import date, datetime, timedelta
import outlook
import fshelper
import json

STARTDATE = date(2010, 6, 17)
ENDDATE = date(2010, 6, 17)

def savedata(path, filename, data):
    """Writes data to file"""
    with open(path + '/' + filename, 'w') as openedfile:
        json.dump(data, openedfile, sort_keys=True, indent=2, ensure_ascii=False)

def fetchdata(day):
    """Fetches all data for a specific day"""

    path = day.strftime('data/%Y/%m/%d')
    fshelper.safedirs(path)

    # Get day 2 outlook
    #TODO

    # Get day 1 13z
    day113z = outlook.process(day, '1300')
    savedata(path, 'outlook_1300.json', day113z)

    # Get day 1 1630z outlook
    day11630z = outlook.process(day, '1630')
    savedata(path, 'outlook_1630.json', day11630z)

    # Get day 1 20z outlook
    day120z = outlook.process(day, '2000')
    savedata(path, 'outlook_2000.json', day120z)

    # Get MDs
    #TODO

    # Get Watches
    #TODO

    # Get reports
    #TODO

CURRENT = STARTDATE
while CURRENT <= ENDDATE:
    fetchdata(CURRENT)
    CURRENT += timedelta(days=1)
