#!/usr/bin/python3.6

import os
import sys
import logging
import argparse

try:
    import fiona
    from fiona.transform import transform_geom
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


def getGeom(inputfn, epsg):
    """Retourne:
       - géometrie de inputfn
       - booleen à True si toutes les geom sont valides
       - l'epsg source s'il a pu être détecté
    """
    print("Récupération des géometries")
    polygonGeoms = []
    all_valid = True
    with fiona.Env():
        with fiona.open(inputfn) as source:
            if len(source.crs) > 0:
                source_epsg = source.crs
            elif epsg is not None:
                source_epsg = {'init': 'epsg:' + epsg}
            else:
                print("Aucun fichier prj détecté et/ou aucune projection source passée avec -epsg")
                sys.exit(1)

            if source_epsg['init'] == 'epsg:4326':
                print("Le SHP d'origne doit être dans une projection en mètre")
                print("détecté:", source_epsg)
                sys.exit(1)

            items = source.items()
            for key, value in items:
                geom = shape(value["geometry"])
                if not geom.is_valid:
                    all_valid = False
                polygonGeoms.append(geom)

            return polygonGeoms, all_valid, source_epsg


def debug_dumpPoligons(polygons, inputfn, source_epsg):
    """Créé dans un nouveau dossier du même nom que le SHP d'entrée
       un nouveau SHP résultat de la découpe et autant de GeoJSON
       en EPSG:4326 que d'entitées créés
    """
    schema = {
        'geometry': 'Polygon',
        'properties': {
            'polygoneid': 'int',
        }
    }

    output_dir = './SPLITTED_' +  os.path.splitext(inputfn)[0]
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    print("Ecriture des fichiers dans", output_dir)

    i = 0
    with fiona.collection(
        output_dir + '/SPLITTED_' + inputfn, 
        'w', 'ESRI Shapefile', schema
    ) as output:
        for polygon in polygons:
            output.write({
                'properties': {
                    'polygoneid': i
                },
                'geometry': mapping(polygon)
            })
            i += 1

    i = 0
    for polygon in polygons:
        geom_transform = transform_geom(source_epsg, "EPSG:4326", mapping(polygon))
        with fiona.collection(
            output_dir + '/' + str(i) + '.geojson', 
            'w', 'GeoJSON', schema
        ) as output:
            output.write({
                'properties': {
                    'polygoneid': i
                },
                'geometry': geom_transform
            })
            i += 1

    print(i, "fichiers GeoJSON créés")


def splitPolygon(geom, maxsurface, targetListVar):
    """
    polygone en entrée
    calcul de sa bbox
    calcul de son orientation
    calcul des points A et B de la droite séquante
    création de la géometrie Line
    création des deux "boites" de part et d'autre de la bbox
    création des polygones par intersection entre chaque boite et la geom
    """
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
