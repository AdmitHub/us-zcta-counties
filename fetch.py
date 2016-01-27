#!/usr/bin/env python3
"""
Fetch county and state relationships from census.gov and format them as json.
"""

import os
import csv
import json
from math import sin, cos, atan2, sqrt, pi
from collections import defaultdict, OrderedDict
from urllib import request
from io import StringIO
from zipfile import ZipFile

BUILD = os.path.join(os.path.dirname(__file__), "build")
OUT = os.path.join(os.path.dirname(__file__), "out")

COUNTY_ZCTA = "http://www2.census.gov/geo/docs/maps-data/data/rel/zcta_county_rel_10.txt"
COUNTY_GEO = "http://www2.census.gov/geo/docs/maps-data/data/gazetteer/Gaz_counties_national.zip"
ZIP_CODES = "http://federalgovernmentzipcodes.us/free-zipcode-database-Primary.csv"

RADIUS_OF_EARTH = 3961 # miles

def _retrieve(url):
    name = url.split("/")[-1]
    if not os.path.exists(BUILD):
        os.makedirs(BUILD)
    path = os.path.join(BUILD, name)
    if not os.path.exists(path):
        with request.urlopen(url) as fh:
            if url.endswith('zip'):
                content = fh.read()
                with open(path, 'wb') as fh:
                    fh.write(content)
            else:
                content = fh.read().decode(fh.headers.get_content_charset() or 'latin-1')
                with open(path, 'w') as fh:
                    fh.write(content)
    return path

def county_zcta_reader():
    path = _retrieve(COUNTY_ZCTA)
    with open(path, encoding='utf-8') as fh:
        reader = csv.reader(StringIO(fh.read()))
        iterator = iter(reader)
        next(iterator)
        return iterator

def county_geo_reader():
    path = _retrieve(COUNTY_GEO)
    with ZipFile(path) as zipfh:
        names = zipfh.namelist()
        with zipfh.open(names[0]) as fh:
            reader = csv.reader(
                StringIO(fh.read().decode('latin-1')),
                delimiter='\t'
            )
            iterator = iter(reader)
            next(iterator)
            return iterator

def zip_code_reader():
    path = _retrieve(ZIP_CODES)
    with open(path, encoding='utf-8') as fh:
        reader = csv.reader(StringIO(fh.read()))
        iterator = iter(reader)
        next(iterator)
        return iterator

def deg_to_rad(deg):
    return pi * deg / 180.

def lat_lng_dist(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = [deg_to_rad(n) for n in (lat1, lon1, lat2, lon2)]
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2)**2) + cos(lat1) * cos(lat2) * (sin(dlon/2)**2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return RADIUS_OF_EARTH * c

def main():
    zcta_reader = county_zcta_reader()
    zip_reader = zip_code_reader()
    geo_reader = county_geo_reader()

    # Counties indexed by concatenated state/county fips code
    counties = defaultdict(lambda: {
        'name': None,
        'state': None,
        'latitude': None,
        'longitude': None,
        'zip_codes': [],
    })
    # Mapping of zip codes to concatenated state/county fips code
    zip_codes = {}

    # Skip the header
    for row in geo_reader:
        state, fips, _, county_name = row[0:4] 
        lat, lng = row[-2:]
        counties[fips]['name'] = county_name
        counties[fips]['latitude'] = float(lat)
        counties[fips]['longitude'] = float(lng)

    for row in zcta_reader:
        zcta, _, _, fips = row[0:4]
        zip_codes[zcta] = fips
        counties[fips]['zip_codes'].append(zcta)

    dist_audit = {}

    bad = {}
    for row in zip_reader:
        zipcode, _, _, _, _, lat, lng = row[0:7]
        if zipcode not in zip_codes:
            try:
                lat = float(lat)
                lng = float(lng)
            except ValueError:
                bad[zipcode] = row
                continue
            min_dist = 0
            argmin = None
            for fips, county in counties.items():
                dist = lat_lng_dist(
                    float(lat), float(lng),
                    county['latitude'], county['longitude']
                )
                if argmin is None or dist < min_dist:
                    argmin = fips
                    min_dist = dist
            dist_audit[zipcode] = (dist, row)
            counties[argmin]['zip_codes'].append(zipcode)

    if not os.path.exists(OUT):
        os.makedirs(OUT)

    with open(os.path.join(OUT, "bad.json"), 'w') as fh:
        json.dump(bad, fh)

    with open(os.path.join(OUT, "dist_audit.json"), 'w') as fh:
        json.dump(dist_audit, fh)

    od = OrderedDict()
    for fips, county in sorted(counties.items(), key=lambda c: c[1]['name']):
        od[county['name']] = {}
        od[county['name']].update(county)
        del od[county['name']]['name']
    with open(os.path.join(OUT, "counties.json"), 'w') as fh:
        json.dump(od, fh, indent=1)

if __name__ == "__main__":
    main()
