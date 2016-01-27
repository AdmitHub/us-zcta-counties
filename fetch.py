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
OUT_DIR = os.path.join(os.path.dirname(__file__))

COUNTY_ZCTA = "http://www2.census.gov/geo/docs/maps-data/data/rel/zcta_county_rel_10.txt"
COUNTY_GEO = "http://www2.census.gov/geo/docs/maps-data/data/gazetteer/Gaz_counties_national.zip"

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

def main():
    zcta_reader = county_zcta_reader()
    geo_reader = county_geo_reader()

    # Counties indexed by concatenated state/county fips code
    counties = defaultdict(lambda: {
        'name': None,
        'state': None,
        'latitude': None,
        'longitude': None,
        'zip_codes': [],
    })
    # Mapping of zip codes to state and county
    zip_codes = {}
    for row in geo_reader:
        state, fips, _, county_name = row[0:4] 
        lat, lng = row[-2:]
        counties[fips]['name'] = county_name
        counties[fips]['state'] = state
        counties[fips]['latitude'] = float(lat)
        counties[fips]['longitude'] = float(lng)

    for row in zcta_reader:
        zcta, _, _, fips = row[0:4]
        counties[fips]['zip_codes'].append(zcta)
        zip_codes[zcta] = {
            'state': counties[fips]['state'],
            'county': counties[fips]['name']
        }

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    # Build a {state: {county: {zip_codes: }}} mapping.
    od = OrderedDict()
    for fips, county in sorted(counties.items(), key=lambda c: (c[1]['state'], c[1]['name'])):
        if county['state'] not in od:
            od[county['state']] = {'counties': OrderedDict()}
        state = od[county['state']]
        state['counties'][county['name']] = {
            'zip_codes': county['zip_codes']
        }
    with open(os.path.join(OUT_DIR, "state_county_zip.json"), 'w') as fh:
        json.dump(od, fh, indent=1)

    # Build a {zip: {county, state} mapping
    zsc = {'zip_state_county': []}
    for zcta, obj in sorted(zip_codes.items()):
        zsc['zip_state_county'].append([zcta, obj['state'], obj['county']])
    zsc['zip_state_county'].sort(key=lambda a: (a[1], a[2]))
    with open(os.path.join(OUT_DIR, "zip_state_county.json"), 'w') as fh:
        json.dump(zsc, fh, indent=0)

if __name__ == "__main__":
    main()
