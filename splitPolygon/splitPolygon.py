#!/usr/bin/python3.6

import sys

try:
    import fiona
except ImportError:
    print('ImportError fiona')
    sys.exit(1)

try:
    from shapely import *
    from shapely.wkt import loads, dumps
    from shapely.geometry import box, Polygon, MultiPolygon, shape, mapping
    from shapely.ops import linemerge, unary_union, polygonize
except ImportError:
    print('ImportError shapely')
    sys.exit(1)

"""
polygone en entrée
calcul de sa bbox
calcul de son orientation
calcul des points A et B de la droite séquante
création de la géometrie Line
création des polygones par coupe
"""

def getGeom(inputfn):
    polygonGeoms = []
    with fiona.Env():
        with fiona.open(inputfn) as source:
            items = source.items()
            for key, value in items:
                geom = shape(value["geometry"])
                polygonGeoms.append(geom)

            return polygonGeoms

def debug_dumpPoligons(polygons):
    schema = {
        'geometry': 'Polygon',
        'properties': {
            'polygoneid': 'int',
        }
    }

    i = 0
    with fiona.collection('dump_polygons.shp', 'w', 'ESRI Shapefile', schema) as output:
        for polygon in polygons:
            output.write({
                'properties': {
                    'polygoneid': i
                },
                'geometry': mapping(polygon)
            })
            i += 1

def splitPolygon(geom, maxsurface, targetListVar):
    # bbox
    xmin, ymin, xmax, ymax = geom.bounds

    # construction de la droite sécante
    if (xmax - xmin) > (ymax - ymin):
        A_x = (xmin + xmax) / 2
        A_y = ymax
        B_x = (xmin + xmax) / 2
        B_y = ymin

        line = loads('LINESTRING ({0} {1}, {2} {3})'.format(A_x, A_y, B_x, B_y))

         # box's
        box1 = loads('POLYGON (({0} {1},{2} {3},{4} {5},{6} {7},{0} {1}))'.format(
            xmin, ymin, xmin, ymax, A_x, A_y, B_x, B_y, xmin, ymin
        ))
        box2 = loads('POLYGON (({0} {1},{2} {3},{4} {5},{6} {7},{0} {1}))'.format(
            A_x, A_y, xmax, ymax, xmax, ymin, B_x, B_y, A_x, A_y
        ))
    elif (xmax - xmin) < (ymax - ymin):
        A_x = xmin
        A_y = (ymin + ymax) / 2
        B_x = xmax
        B_y = (ymin + ymax) / 2

        line = loads('LINESTRING ({0} {1}, {2} {3})'.format(A_x, A_y, B_x, B_y))

        box1 = loads('POLYGON (({0} {1},{2} {3},{4} {5},{6} {7},{0} {1}))'.format(
            xmin, ymin, A_x, A_y, B_x, B_y, xmax, ymin, xmin, ymin
        ))
        box2 = loads('POLYGON (({0} {1},{2} {3},{4} {5},{6} {7},{0} {1}))'.format(
            A_x, A_y, xmin, ymax, xmax, ymax, B_x, B_y, A_x, A_y
        ))

    # géometries splitées
    polygons = []
    polygons.append(geom.intersection(box1))
    polygons.append(geom.intersection(box2))

    # répétition de l'opération pour tous les polygones produits
    for polygon in polygons:
        if (polygon.area / 10000) > maxsurface:
            splitPolygon(polygon, maxsurface, targetListVar)
        else:
            targetListVar.append(polygon)
