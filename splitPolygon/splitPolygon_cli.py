#!/usr/bin/python3.6

from splitPolygon import *

"""
polygone en entrée
calcul de sa bbox
calcul de son orientation
calcul des points A et B de la droite séquante
création de la géometrie Line
création des polygones par coupe
"""

def main():
    # message d'erreur et print de la doc s'il manque des args
    if len(sys.argv) < 3:
        print('ERREUR: un ou plusieurs arguments manquants')
        doc()
        sys.exit(1)
    else:
        # geom du polygone à découper
        polygonGeom = getGeom(sys.argv[1])

        # liste vide pour stocker les polygones < surfaceMax produits
        goodPolygons = []

        # split des polygones, incrémentation de goodPolygons
        splitPolygon(polygonGeom[0], int(sys.argv[2]), goodPolygons)

        # écriture du SHP de sortie avec goodPolygons
        debug_dumpPoligons(goodPolygons)

def doc():
    print("""
    argument 1 : shp source
    argument 2 : surface maximale des polygones (en ha)

    ex : [...].py polygone.shp 20
    """)

if __name__ == '__main__':
    main()
