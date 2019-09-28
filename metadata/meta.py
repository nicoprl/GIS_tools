#!/usr/bin/python3

import os
import sys
import csv

try:
    import fiona
except ImportError as err_import:
    print("Error importing fiona")
    print(err_import)
    sys.exit(1)

"""
Boucle sur les fichiers vectoriels présents dans le dossier courant
Ecrit metadata.csv avec les valeurs distinct de chaque champs
CSV : 
  - Champs: FICHIER, GEOM_TYPE, CHAMP, TYPE, VALEUR
  - Encodage : UTF-8
  - Séparateur: virgule

Structure du dictionnaire produit (exemple):
r = {
    "test.shp": {
        "champs": {
            "IDNUM": {
                "datatype": "int:18",
                "values": [0, 1, 2, 3, 4]
            },
            "position": {
                "datatype": "str:254",
                "values": ['aerien', 'souterrain']
            }
        },
        "geom_type": "LineString"
    }
}
"""

vector_formats = [".shp", ".gpkg", ".geojson", ".tab", ".kml", ".gml", ".dxf"]
results = {}

for f in os.listdir(os.getcwd()):
    if os.path.splitext(f)[1].lower() in vector_formats:
        try:
            with fiona.open(f) as src:
                if len(src.meta["schema"]["properties"]) == 0:
                    print(f, "ne contient aucune information attributaire")
                geom_type = src.meta["schema"]["geometry"]
                fields = src.meta["schema"]["properties"]
                results[f] = {"geom_type": geom_type, "champs": {}}
                for name, datatype in fields.items():
                    results[f]["champs"][name] = {"datatype": datatype, "values": []}

                for key, feat in src.items():
                    for field in fields:
                        value = feat["properties"][field]
                        if not value in results[f]["champs"][field]["values"]:
                            results[f]["champs"][field]["values"].append(value)
        except fiona.errors.DriverError as err_fiona_open:
            print(err_fiona_open)
            pass

with open("metadata.csv", encoding="utf-8", newline="", mode="w") as csv_f:
    output = csv.writer(csv_f, delimiter=",")
    output.writerow(["FICHIER", "GEOM_TYPE", "CHAMP", "TYPE", "VALEUR"])

    for file, content in results.items():
        for field, infos in content["champs"].items():
            for value in infos["values"]:
                output.writerow([file, content["geom_type"], field, infos["datatype"], value])
