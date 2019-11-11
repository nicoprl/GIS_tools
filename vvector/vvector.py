#!/usr/bin/python3.6

import os
import sys

try:
    import fiona
    from shapely.geometry import shape
    import matplotlib.pyplot as plt
except ImportError as err_import:
    print(err_import)
    sys.exit(1)

# TODO:


with fiona.open(sys.argv[1]) as src:
    title_geom_type = src.meta["schema"]["geometry"]
    for key, feat in src.items():
        geom = shape(feat["geometry"])
        if geom.geom_type == "Polygon":
            x, y = geom.exterior.xy
            if len(geom.interiors) > 0:
                plt.plot(x, y, color="blue")
                for ring in geom.interiors:
                    x, y = ring.xy
                    plt.plot(x, y, color="blue")
            else:
                plt.plot(x, y)
        elif geom.geom_type == "MultiPolygon":
            for polygon in geom:
                x, y = polygon.exterior.xy
                plt.plot(x, y, color="blue")
        elif geom.geom_type == "LineString":
            x, y = geom.coords.xy
            plt.plot(x, y)
        elif geom.geom_type == "MultiLineString":
            for line in geom:
                x, y = line.coords.xy
                plt.plot(x, y, color="blue")
        elif geom.geom_type == "Point":
            x = geom.x
            y = geom.y
            plt.scatter(x, y)
        elif geom.geom_type == "MultiPoint":
            for point in geom:
                x = point.x
                y = point.y
                plt.scatter(x, y, color="blue")

plt.title(sys.argv[1] + " [" + title_geom_type + "]")
plt.show()
