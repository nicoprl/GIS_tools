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
    # afficher tous les niveaux de log de fiona/shapely
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    # gestion des arguments
    parser = argparse.ArgumentParser(
        description='Split un SHP polygone en entités avec S < surface_max'
    )
    parser.add_argument('shp', help='SHP en entrée')
    parser.add_argument('surface_max', help='surface maximale des polygones (en ha)')
    parser.add_argument('-epsg', help='EPSG de la donnée source si pas de .prj')
    parser.add_argument(
        '--forceinvalid',
        action='store_true',
        help='Procéder au découpage même si erreurs de topologie sont détectées'
    )
    args = parser.parse_args()

    # geom du polygone à découper, booleen sur la validité topo, epsg source
    polygonGeom, all_valid, source_epsg = getGeom(args.shp, args.epsg)

    # on abandonne si des géometries invalides sont trouvées
    # sauf si l'utilisateur force la découpe avec --forceinvalid
    if not all_valid and not args.forceinvalid:
        print("Une ou plusieurs erreurs de topologies trouvées. Abandon.")
        sys.exit(1)
    elif not all_valid and args.forceinvalid:
        print("Une ou plusieurs erreurs de topologies trouvées. Forçage du découpage.")

    # liste vide pour stocker les polygones < surfaceMax produits
    goodPolygons = []

    # split des polygones, incrémentation de goodPolygons
    for poly in polygonGeom:
        splitPolygon(poly, int(args.surface_max), goodPolygons)

    # écriture du SHP de sortie avec goodPolygons
    debug_dumpPoligons(goodPolygons, args.shp, source_epsg)

    print("Fin du traitement")

if __name__ == '__main__':
    main()
