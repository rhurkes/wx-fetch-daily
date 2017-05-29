import arrow

ISOFORMAT = 'YYYY-MM-DDTHH:mm:ss'

def getutc(value):
    """Parses NWS datetime strings"""
    # arrow/dateutil don't support non-unique DST shorthand, so replace those tz strings
    if value.find('EDT') > -1:
        value = value.replace('EDT', 'EST5EDT')
    elif value.find('CDT') > -1:
        value = value.replace('CDT', 'CST6CDT')
    elif value.find('MDT') > -1:
        value = value.replace('MDT', 'MST7MDT')
    elif value.find('PDT') > -1:
        value = value.replace('PDT', 'PST8PDT')
    return arrow.get(value, 'hmm A ZZZ ddd MMM DD YYYY').to('UTC')

def toisostring(dt):
    """Takes UTC datetime object and return ISO8601 string"""
    return dt.format(ISOFORMAT) + 'Z'

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
