# Javascript to get values from:
# https://en.wikipedia.org/wiki/Federal_Information_Processing_Standard_state_code
#var values = [];
#document.getElementById('meow').querySelectorAll('tr').forEach(x => {
#  const cells = x.querySelectorAll('td');
#  const st = cells[1].innerText;
#  if (st) { values.push([parseInt(cells[2].innerText), st]); }
#});

import json

JSONVALUES = '[[1,"AL"],[2,"AK"],[60,"AS"],[4,"AZ"],[5,"AR"],[6,"CA"],[8,"CO"],[9,"CT"],[10,"DE"],[11,"DC"],[12,"FL"],[64,"FM"],[13,"GA"],[66,"GU"],[15,"HI"],[16,"ID"],[17,"IL"],[18,"IN"],[19,"IA"],[20,"KS"],[21,"KY"],[22,"LA"],[23,"ME"],[68,"MH"],[24,"MD"],[25,"MA"],[26,"MI"],[27,"MN"],[28,"MS"],[29,"MO"],[30,"MT"],[31,"NE"],[32,"NV"],[33,"NH"],[34,"NJ"],[35,"NM"],[36,"NY"],[37,"NC"],[38,"ND"],[69,"MP"],[39,"OH"],[40,"OK"],[41,"OR"],[70,"PW"],[42,"PA"],[72,"PR"],[44,"RI"],[45,"SC"],[46,"SD"],[47,"TN"],[48,"TX"],[74,"UM"],[49,"UT"],[50,"VT"],[51,"VA"],[78,"VI"],[53,"WA"],[54,"WV"],[55,"WI"],[56,"WY"]]'
VALUES = json.loads(JSONVALUES)

def getstatefromfips(fips):
    """ Returns two letter state code """
    normalizedfips = int(fips)
    for value in VALUES:
        if value[0] == normalizedfips:
            return value[1]
    return None
