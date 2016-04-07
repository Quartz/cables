#!/usr/bin/env python

# from agate import csv
from fastkml.kml import KML
import geojson

FIELDNAMES = [
    # 'id',
    # 'name',
    # 'length',
    'rfs',
    'rfs_year',
    # 'owners',
    # 'url',
]

def main():
    with open('fusion-cables-201603171133.kml') as f:
        kml = KML()
        kml.from_string(f.read())

    document = tuple(kml.features())[0]

    features = []

    for feature in document.features():
        print(feature.name)

        props = {}

        for el in feature.extended_data.elements:
            if el.name in FIELDNAMES:
                props[el.name] = el.value

        props['rfs_year'] = clean_rfs(props['rfs'])
        del props['rfs']

        # LineString
        if feature.geometry.geom_type == 'LineString':
            coords = tuple(c[:2] for c in feature.geometry.coords)
            geom = geojson.LineString(coords)
        # MultiLineString
        else:
            coords = tuple(tuple(c[:2] for c in geom.coords) for geom in feature.geometry.geoms)
            geom = geojson.MultiLineString(coords)

        feature = geojson.Feature(geometry=geom, properties=props, id=feature.name)

        features.append(feature)

    with open('src/data/cables.json', 'w') as f:
        geojson.dump(geojson.FeatureCollection(features), f)

def clean_rfs(rfs):
    try:
        return int(rfs[-4:])
    except ValueError:
        return None

if __name__ == '__main__':
    main()
