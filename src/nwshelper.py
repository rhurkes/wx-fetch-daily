import arrow

ISOFORMAT = 'YYYY-MM-DDTHH:mm:ss'

def getutc(value):
    """Parses NWS datetime strings"""
    return arrow.get(value, 'HHmm A ZZZ ddd MMM DD YYYY').to('UTC')

def toisostring(dt):
    """Takes UTC datetime object and return ISO8601 string"""
    return dt.format(ISOFORMAT) + 'Z'
