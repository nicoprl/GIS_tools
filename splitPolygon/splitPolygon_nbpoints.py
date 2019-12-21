#!/usr/bin/python3.6

import sys

import fiona
from shapely.geometry import shape, mapping, MultiPolygon, box
from shapely.ops import unary_union
from shapely.wkt import loads

def main():
    geom = get_geom(sys.argv[1])
    xmin, ymin, xmax, ymax = geom.bounds
    print(nbpoint_count(geom))
    print(box(xmin, ymin, xmax, ymax))

    polys = []
    split_polygon(geom, "nb_points", 180000, polys)
    with open("output.csv", "w") as dest:
        i = 0
        for poly in polys:
            dest.write(str(i) + ";" + str(poly) + "\n")
            i += 1

def get_geom(inputfn):
    with fiona.open(inputfn) as src:
        # feat = next(iter(src))
        # return shape(feat["geometry"])

        polys = []
        for key, feat in src.items():
            polys.append(shape(feat["geometry"]))

        return unary_union(polys)
def nbpoint_count(geom):
    """
       comptage du nombre de points dans le multipolygone
       warning si [150000;180001], arrêt si > 180000
    """
    coordinates = mapping(geom)["coordinates"]
    points_count = 0
    for polygon in coordinates:
            for part in polygon:
                points_count += len(part)

    return points_count

def split_polygon(geom, critere, criterevalue, target):
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

    box1_intersect = geom.intersection(box1)
    box2_intersect = geom.intersection(box2)

    # print(box1)
    # print(box2)
    # print(line)
    # print(box1_intersect)
    # print(box2_intersect)
    # sys.exit(0)   


    if box1_intersect.geom_type != "MultiPolygon":
        polygons.append(MultiPolygon([box1_intersect]))
    else:
        polygons.append(box1_intersect)

    if box2_intersect.geom_type != "MultiPolygon":
        polygons.append(MultiPolygon([box2_intersect]))
    else:
        polygons.append(box2_intersect)

    # print(polygons[0])
    # print(polygons[1])

    if critere == "nb_points":
        for p in polygons:
            if nbpoint_count(p) > criterevalue:
                # print("polygon has", nbpoint_count(p), "points, > at", criterevalue, p)
                split_polygon(p, "nb_points", criterevalue, target)
            else:
                target.append(p)

if __name__ == '__main__':
    main()