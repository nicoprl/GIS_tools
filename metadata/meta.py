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

doc = """
meta.py [-h, --help] [-all]

-h, --help: display documentation and exit
-all: fields beginning with ID/id/Id/iD are ignored unless the -all flag is specified

Write metadata.csv with distinct value of each field, 
for each vector file in the current working directory

CSV : 
  - Fields: FILE, GEOM_TYPE, CHAMP, TYPE, VALEUR
  - Encoding : UTF-8
  - Delimiter: comma

results dictionnary (exemple):
    results = {
        "test.shp": {
            "fields": {
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

def main():
    if (len(sys.argv) > 1) and (sys.argv[1] in ("-h", "--help")):
        print(doc)
        sys.exit(0)

    results = {}
    ignored_fields = []
    for f in os.listdir(os.getcwd()):
        if is_valid_vector_file(f):
            print(f, "...")
            try:
                with fiona.open(f) as src:
                    has_attribute(f, src)
                    geom_type = get_geom_type(src)
                    fields = get_fields(src)
                    results_create_file_entry(f, results, geom_type)
                    if (len(sys.argv) > 1) and (sys.argv[1] == "-all"):
                        results_write_fields(f, results, fields, ignored_fields, filter_field=False)
                    else:
                        results_write_fields(f, results, fields, ignored_fields, filter_field=True)
                    results_write_distinct_values(f, results, src, fields, ignored_fields)
                    write_metadata_file(results)
            except fiona.errors.DriverError as err_fiona_open:
                print("[ERROR] Failed to open", f)
                print(err_fiona_open)
                pass

def is_valid_vector_file(f:str) -> bool:
    """Check if f file is a supported vector format"""
    vector_formats = [
        ".shp", ".gpkg", ".geojson", 
        ".tab", ".kml", ".gml", ".dxf"
    ]
    if os.path.splitext(f)[1].lower() in vector_formats:
        return True
    else:
        return False

def has_attribute(f, src) -> bool:
    """Check if source contains attributes"""
    if len(src.meta["schema"]["properties"]) == 0:
        print("[INFO]", f, "does not contain any attributes")
        return False
    else:
        return True

def get_geom_type(src):
    """Return geom_type from source"""
    return src.meta["schema"]["geometry"]

def get_fields(src):
    """Return fields from source"""
    return src.meta["schema"]["properties"]

def results_create_file_entry(f, results, geom_type):
    """Write an entry in results dict: file_name: {geom_type, fields}"""
    results[f] = {"geom_type": geom_type, "fields": {}}

def results_write_fields(f, results, fields, ignored_fields, filter_field=True):
    """Write name and datatype for each field in results dict"""
    for name, datatype in fields.items():
        if filter_field:
            # excluding fields beginning with id / ID / Id ...
            if "id" not in name[0:2].lower():
                # writing name and datatype for each field in results dict
                results[f]["fields"][name] = {"datatype": datatype, "values": []}
            else:
                print("[INFO] field", name, "of file", f, "added to ignored_fields")
                ignored_fields.append(name)
        else:
            results[f]["fields"][name] = {"datatype": datatype, "values": []}

def results_write_distinct_values(f, results, src, fields, ignored_fields):
    """Write distinct values in results dict"""
    for key, feat in src.items():
        for field in fields:
            if field not in ignored_fields:
                value = feat["properties"][field]
                # writing field value in values list if it doesn't exists
                if not value in results[f]["fields"][field]["values"]:
                    results[f]["fields"][field]["values"].append(value)

def write_metadata_file(results):
    """Write results dict to metadata.csv"""
    with open("metadata.csv", encoding="utf-8", newline="", mode="w") as csv_f:
        output = csv.writer(csv_f, delimiter=",")
        output.writerow(["FILE", "GEOM_TYPE", "CHAMP", "TYPE", "VALEUR"])

        for file, content in results.items():
            for field, infos in content["fields"].items():
                for value in infos["values"]:
                    output.writerow([
                        file, 
                        content["geom_type"], 
                        field, 
                        infos["datatype"], 
                        value
                    ])

if __name__ == "__main__":
    main()