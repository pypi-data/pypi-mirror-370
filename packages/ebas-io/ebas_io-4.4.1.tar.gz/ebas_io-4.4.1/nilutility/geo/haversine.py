"""
$Id: haversine.py 1809 2017-10-17 10:22:58Z pe $

Geospatianls functions - Haversine formula
Spherical trigonometry

History:
V.1.0.0  2017-10-16  pe  initial version
"""

import math

UNIT_FACTORS = {
    "nm": 1,
    "km": 1.852,
    "m": 1852,
}

def haversine_dist(pos1, pos2, unit='nm'):
    """
    Haversine great circle distance between two points.
    Parameters:
        pos1, pos2   the two position, each (lat, lon)
        unit         result unit ('km', 'nm')
    Returns:
        distance
    Raises:
        ValueError  on unsupported unit
    """
    r_nm = 180*60/math.pi
    try:
        rad = r_nm * UNIT_FACTORS[unit]
    except KeyError:
        raise ValueError("unsupported unit '{}'".format(unit))
    lat1, lon1, lat2, lon2 = [math.radians(x) for x in list(pos1) + list(pos2)]
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a__ = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * \
        math.sin(dlon/2)**2
    c__ = 2 * math.asin(math.sqrt(a__))
    return c__ * rad
