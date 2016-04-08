#!/usr/bin/env python

# from agate import csv
from fastkml.kml import KML
import geojson

def main():
    with open('fusion-cables-201603171133.kml') as f:
        kml = KML()
        kml.from_string(f.read())

    document = tuple(kml.features())[0]

    cable_lookup = {}
    cable_features = []

    for feature in document.features():
        props = {}

        for el in feature.extended_data.elements:
            if el.name in ['cable_id', 'rfs']:
                props[el.name] = el.value

        try:
            props['rfs_year'] = clean_rfs(props['rfs'])
        except ValueError:
            print('Cable missing year: %s' % feature.name)
            continue

        del props['rfs']

        cable_lookup[props['cable_id']] = props['rfs_year']
        del props['cable_id']

        # LineString
        if feature.geometry.geom_type == 'LineString':
            coords = tuple(c[:2] for c in feature.geometry.coords)
            geom = geojson.LineString(coords)
        # MultiLineString
        else:
            coords = tuple(tuple(c[:2] for c in geom.coords) for geom in feature.geometry.geoms)
            geom = geojson.MultiLineString(coords)

        cable = geojson.Feature(geometry=geom, properties=props, id=feature.name)

        cable_features.append(cable)

    with open('fusion-landing-points-201603171133.kml') as f:
        kml = KML()
        kml.from_string(f.read())

    document = tuple(kml.features())[0]

    cities = {}

    for feature in document.features():
        props = {}

        for el in feature.extended_data.elements:
            if el.name in ['city_id', 'cable_id']:
                props[el.name] = el.value

        try:
            props['year'] = cable_lookup[props['cable_id']]
        except KeyError:
            print('Missing cable id: %s' % props['cable_id'])
            continue

        del props['cable_id']

        if not props['year']:
            continue

        city_id = props['city_id']
        del props['city_id']

        if city_id in cities:
            if props['year'] < cities[city_id]['props']['year']:
                cities[city_id]['props'] = props
        else:
            coords = feature.geometry.coords[0]
            geom = geojson.Point(coords)

            cities[city_id] = {
                'props': props,
                'geom': geom
            }

    landing_features = []

    for city in cities.values():
        landing = geojson.Feature(geometry=city['geom'], properties=city['props'])

        landing_features.append(landing)

    output = {
        'cables': geojson.FeatureCollection(cable_features),
        'landings': geojson.FeatureCollection(landing_features)
    }

    with open('src/data/cables.json', 'w') as f:
        geojson.dump(output, f)

def clean_rfs(rfs):
    return int(rfs[-4:])

if __name__ == '__main__':
    main()
