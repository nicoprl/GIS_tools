#!/usr/bin/python3.6

import sys

try:
    import requests
except ImportError as err_import:
    print("Erreur à l'import de requests")
    print(err_import)
    sys.exit(1)

def main():
    print(prj2epsg(sys.argv[1]))

def prj2epsg(prjfile):
    try:
        with open(prjfile, mode="r", encoding="utf-8") as prj:
            r = requests.get(
                "http://prj2epsg.org/search.json", 
                params={"mode": "wkt", "terms": prj.read()}
            )
            if r.status_code == 200:
                resp = r.json()
                if resp["exact"]:
                    epsg = resp["codes"][0]["code"]
                    return epsg
                else:
                    print("prj2epsg() pas de match exact")
                    return None
            else:
                print("prj2epsg() ERREUR : status_code", r.status_code)
                return None
    except Exception as e:
        print("prj2epsg() ERREUR: ", e)
        return None

if __name__ == "__main__":
    main()