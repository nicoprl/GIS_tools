#!/usr/bin/python3.5

import os
import json
import sys
import argparse
import traceback
from string import Template

def main():
    try:
        description='Generate a simple leaflet webmap based on a JSON configuration file'
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('configFile', metavar='configFile', help='path to config.json')
        parser.add_argument('destFolder', metavar='destFolder', help='path to destination folder')
        args = parser.parse_args()

        config = json.load(open(os.getcwd() + '/' + args.configFile))
        baseMaps = {"None": "emptyMap"}
        overlayMaps = {}

        tileLayerBlock_html = tileLayerBlock(config, baseMaps)
        wmsBlock_html = wmsBlock(config, overlayMaps)
        geojsonBlock_html = geojsonBlock(config, overlayMaps)
        
        overlayMapsBlock_html = overlayMapsBlock(overlayMaps)
        baseMapsBlock_html = baseMapsBlock(baseMaps)

        mapGenerate(
            config, 
            baseMapsBlock_html, 
            overlayMapsBlock_html, 
            tileLayerBlock_html, 
            wmsBlock_html, 
            geojsonBlock_html, 
            os.getcwd() + '/' + args.destFolder
        )

        print(config["outputFileName"], 'generated in', args.destFolder)
    except Exception as e:
        print(e)
        print(traceback.print_exc())

def baseMapsBlock(baseMaps):
    content = ''
    for name, var in baseMaps.items():
        content += '"{0}": {1},'.format(name, var)

    baseMapsBlockContent = """
    var baseMaps = {
            %s
    };
    """ % content
    return baseMapsBlockContent

def overlayMapsBlock(overlayMaps):
    content = ''
    for name, var in overlayMaps.items():
        content += '"{0}": {1},'.format(name, var)

    overlayMapsBlockContent = """
    var overlayMaps = {
        %s
    };
    """ % content
    return overlayMapsBlockContent

def tileLayerBlock(config, baseMaps):
    if "tileLayerConfig" in config.keys():
        tileLayerBlock = ''
        i = 0
        for tileLayer in config["tileLayerConfig"]:  
            tileLayerBlockContent ="""
            var baseMap_$i = L.tileLayer('$url', {
                attribution: '$attribution'
            })"""
            tileLayerTemplate = Template(tileLayerBlockContent)
            tileLayerBlockCompleted = tileLayerTemplate.substitute(
                i = i,
                url = tileLayer["url"],
                attribution = tileLayer["attribution"]
            )
            if tileLayer["addToMap"]:
                tileLayerBlockCompleted = tileLayerBlockCompleted + '.addTo(map);'
            tileLayerBlock += tileLayerBlockCompleted
            baseMaps[tileLayer["name"]] = "baseMap_" + str(i)
            i += 1
    else:
        tileLayerBlock = ''

    return tileLayerBlock

def wmsBlock(config, overlayMaps):
    if "wmsConfig" in config.keys():
        wmsBlock = ''
        i = 0
        for wms in config["wmsConfig"]:
            wmsBlockContent = """
            var wmsLayer_$i = L.tileLayer.wms('$url', {
                layers: '$layers',
                format: 'image/png',
                transparent: true,
            })"""
            wmsBlockTemplate = Template(wmsBlockContent)
            wmsBlockCompleted = wmsBlockTemplate.substitute(
                i = i,
                url = wms["url"],
                layers = wms["layers"]
            )
            if wms["addToMap"]:
                wmsBlockCompleted = wmsBlockCompleted + '.addTo(map);'
            wmsBlock += wmsBlockCompleted
            overlayMaps[wms["name"]] = 'wmsLayer_' + str(i)
            i += 1
    else:
        wmsBlock = ''

    return wmsBlock

def geojsonBlock(config, overlayMaps):
    if "geojsonConfig" in config.keys():
        geojsonBlock = ''
        i = 0
        for geojson in config["geojsonConfig"]:
            if "geojsonFilePath" in geojson.keys():
                with open(geojson["geojsonFilePath"]) as geojsonFile:
                    geometry = geojsonFile.read()
            else:
                geometry = geojson["geometry"]

            geojsonBlockContent = """
            // GeoJSON - Style
            var reseauStyle_$i = {
                color: '$color',
                weight: $weight,
                opacity: $opacity,
                fill: $fill,
                fillColor: '$fillColor',
                fillOpacity: $fillOpacity
            }

            // GeoJSON - data
            var geometry_$i = $geometry
            var vectorData_$i = L.geoJson(geometry_$i, {
                style: reseauStyle_$i
            })"""
            geojsonBlockTemplate = Template(geojsonBlockContent)
            geojsonBlockCompleted = geojsonBlockTemplate.substitute(
                i = i,
                color = geojson["geojsonStyle"]["color"],
                weight = geojson["geojsonStyle"]["weight"],
                opacity = geojson["geojsonStyle"]["opacity"],
                fill = str(geojson["geojsonStyle"]["fill"]).lower(),
                fillColor = geojson["geojsonStyle"]["fillColor"],
                fillOpacity = geojson["geojsonStyle"]["fillOpacity"],
                geometry = geometry
            )
            if geojson["addToMap"]:
                geojsonBlockCompleted = geojsonBlockCompleted + '.addTo(map);'
            geojsonBlock += geojsonBlockCompleted
            overlayMaps[geojson["name"]] = 'vectorData_' + str(i)
            i += 1
    else:
        geojsonBlock = ''

    return geojsonBlock

def mapGenerate(config, baseMapBlock, overlayMapsBlock, tileLayerBlock, wmsBlock, geojsonBlock, destFolder):
    mapContent = """
    <!DOCtype html>
    <html>
    <head>
    	<title>$title</title>
        <meta charset="utf-8" />
		<link rel="stylesheet" href="https://unpkg.com/leaflet@latest/dist/leaflet.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css" />

        <script src="https://unpkg.com/leaflet@latest/dist/leaflet-src.js"></script>
        <script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>
        <style>
        #map {
            height:$mapHeight;
            width:$mapWidth;
            border: 1px solid black;
        }
        
        .leaflet-container {
            background: #FFFFFF;
            outline: 0;
        }
        </style>
    </head>

    <body>

    <div id="map"></div>

    <!-- get lat, lng et zoom from URL -->
    <script>
      function getUrlVars() {
          var vars = {};
          var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
          vars[key] = value;
          });
          return vars;
      }

      var lat = getUrlVars()["lat"];
      var lng = getUrlVars()["lng"];
      var zoom = getUrlVars()["z"];
    </script>

    <script>
    // Centrage (lat,lng et z de l'URL ou valeurs par défaut)
    var map = L.map('map', {
        center: [$lat, $lng],
        zoom: $zoom
    });

    // tileLayer (basemap)
    $tileLayerBlock

    // GeoJSON
    $geojsonBlock

    // WMS
    $wmsBlock

    // empty basemap
    var emptyMap = L.tileLayer('',{maxZoom: 35});

    // controls - baseMap
    $baseMapBlock

    // controls - overlayMaps
    $overlayMapsBlock

    var options = {
        collapsed : false
    }

    L.control.layers(baseMaps, overlayMaps, options).addTo(map);

    // Geocoder
    L.Control.geocoder().addTo(map);

    // scalebar
    L.control.scale({"imperial": false}).addTo(map);

    </script>

    </body>
    </html>
    """
    mapTemplate = Template(mapContent)
    mapHTML = mapTemplate.substitute(
        mapWidth = config["mapWidth"],
        mapHeight = config["mapHeight"],
        title = config["title"],
        lat = config["center"]["lat"],
        lng = config["center"]["lng"],
        zoom = config["center"]["zoom"],
        baseMapBlock = baseMapBlock,
        overlayMapsBlock = overlayMapsBlock,
        tileLayerBlock = tileLayerBlock,
        wmsBlock = wmsBlock,
        geojsonBlock = geojsonBlock
    )

    with open(config["outputFileName"], 'w') as outputMap:
        outputMap.write(mapHTML)

if __name__ == '__main__':
    main()