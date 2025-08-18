

from math import radians, degrees, sin, cos, atan2, sqrt

def sq2ll(sq):
    sq = sq.upper()
    lat = 10* (ord(sq[1])-ord('A'))
    lon = 20* (ord(sq[0])-ord('A'))
    if(len(sq)>2):
        lat += int(sq[3]) + 0.5
        lon += 2*int(sq[2]) + 1
    else:
        lat += 5
        lon += 10
    return lat, lon
    
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c)

def bearing_deg(lat1, lon1, lat2, lon2):
    y = sin(radians(lon2 - lon1)) * cos(radians(lat2))
    x = cos(radians(lat1))*sin(radians(lat2)) - sin(radians(lat1))*cos(radians(lat2))*cos(radians(lon2 - lon1))
    b = atan2(y, x)
    return round((degrees(b) + 360) % 360)

def sq_km_deg(sq, home_square):
    import re
    if(re.search("[A-R][A-R][0-9][0-9]",sq) and sq != "RR73"):
        lat1, lon1 = sq2ll(home_square)
        lat2, lon2 = sq2ll(sq)
        km = haversine_distance(lat1, lon1, lat2, lon2)
        deg = bearing_deg(lat1, lon1, lat2, lon2)
        return km, deg
    else:
        return False






