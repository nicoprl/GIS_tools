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
            "profondeur": {
                "datatype": "float:11.2",
                "values": [45.21, 50.0, 45.0]
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
ignored_field = []

# pour chaque fichier dans le dossier courant ...
for f in os.listdir(os.getcwd()):
    # si le fichier porte l'extension d'un format vectoriel connu ...
    if os.path.splitext(f)[1].lower() in vector_formats:
        try:
            with fiona.open(f) as src:
                if len(src.meta["schema"]["properties"]) == 0:
                    print(f, "ne contient aucune information attributaire")
                geom_type = src.meta["schema"]["geometry"]
                fields = src.meta["schema"]["properties"]
                # création de l'entrée dans le dictionnaire results (nom fichier, geom type)
                results[f] = {"geom_type": geom_type, "champs": {}}
                for name, datatype in fields.items():
                    # on exclu les champs commençants par id / ID / Id ...
                    if "id" not in name[0:2].lower():
                        # pour chaque champs, écriture de son nom et de son type ...
                        results[f]["champs"][name] = {"datatype": datatype, "values": []}
                    else:
                        ignored_field.append(name)

                for key, feat in src.items():
                    for field in fields:
                        if field not in ignored_field:
                            value = feat["properties"][field]
                            # on inscrit la valeur du champs si elle n'est pas déjà enregistrée
                            if not value in results[f]["champs"][field]["values"]:
                                results[f]["champs"][field]["values"].append(value)
        except fiona.errors.DriverError as err_fiona_open:
            print("Erreur à l'ouverture de", f)
            print(err_fiona_open)
            pass

# écriture du dictionnaire results dans metadata.csv
with open("metadata.csv", encoding="utf-8", newline="", mode="w") as csv_f:
    output = csv.writer(csv_f, delimiter=",")
    output.writerow(["FICHIER", "GEOM_TYPE", "CHAMP", "TYPE", "VALEUR"])

    for file, content in results.items():
        for field, infos in content["champs"].items():
            for value in infos["values"]:
                output.writerow([file, content["geom_type"], field, infos["datatype"], value])
