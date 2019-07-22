#!/usr/bin/python3

import sys
import os
import json

import fiona
from shapely.wkt import dumps, loads
from shapely.geometry import mapping

print(json.dumps(mapping(loads(sys.argv[1]))))

try:
	if sys.argv[2] == "-f":
		if 'POINT' in sys.argv[1]:
		    geom_type = 'Point'
		elif 'LINESTRING' in sys.argv[1]:
		    geom_type = 'LineString'
		elif 'POLYGON' in sys.argv[1]:
		    geom_type = 'Polygon'
		else:
		    print(sys.argv[1], "is not a recognised geometry type")
		    sys.exit(1)

		schema = {
		    'geometry': geom_type,
		    'properties': {'id': 'int'}
		}

		with fiona.open(
		    os.getcwd() + "/output.geojson", "w",
		    driver='GeoJSON', schema=schema,
		    crs="EPSG:4326", encoding="UTF-8"
		) as output:
		    output.write({
		        "properties": {"id": 0},
		        "geometry": mapping(loads(sys.argv[1]))
		    })

		with open(os.getcwd() + "/output.geojson", "r") as r_geojson:
		    print(r_geojson.read())
except IndexError:
	pass
