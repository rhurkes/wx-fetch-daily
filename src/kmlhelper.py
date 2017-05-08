"""Super hacky way of building KML to validate centroid analysis"""

from datetime import datetime
import fshelper

#TODO styles

def buildpolygon(name, data):
    start = '<Placemark><name>' + name + '</name>'
    coordinates = '\n'
    for point in data['points']:
        coordinates += str(point[0]) + ',' + str(point[1]) + ',' + '100\n'
    polygonstart = '<Polygon><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode><outerBoundaryIs><LinearRing><coordinates>'
    polygonend = '</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>'
    centerstart = '<Placemark><name>' + name + ' Center</name>'
    centerpoint = '<Point><coordinates>' + str(data['center'][0]) + ',' + str(data['center'][1]) + ',100</coordinates></Point></Placemark>'
    return ''.join([start, polygonstart, coordinates, polygonend, centerstart, centerpoint])

def buildkml(day):
    """Builds KML for a given day"""
    base = '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>' + day.strftime('%Y-%m-%d Validation') + '</name>'
    end = '</Document></kml>'
    rootpath = day.strftime('data/%Y/%m/%d/')

    outlook1300data = fshelper.loaddata(rootpath + 'outlook_1300.json')
    outlook1630data = fshelper.loaddata(rootpath + 'outlook_1630.json')
    outlook2000data = fshelper.loaddata(rootpath + 'outlook_2000.json')

    maxkey = outlook1300data['probabilistic']['tornado']['max']
    o13 = outlook1300data['probabilistic']['tornado'][maxkey]

    maxkey = outlook1630data['probabilistic']['tornado']['max']
    o16 = outlook1630data['probabilistic']['tornado'][maxkey]

    maxkey = outlook2000data['probabilistic']['tornado']['max']
    o20 = outlook2000data['probabilistic']['tornado'][maxkey]

    outlook1300 = buildpolygon('1300z Outlook', o13)
    outlook1630 = buildpolygon('1630z Outlook', o16)
    outlook2000 = buildpolygon('2000z Outlook', o20)

    kml = ''.join([base, outlook1300, outlook1630, outlook2000, end])

    with open(rootpath + 'validation.kml', 'w') as textfile:
        textfile.write(kml)
