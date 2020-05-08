# LEAFLET GEN

## Usages

```
usage: leafletGen.py [-h] configFile destFolder

Generate a simple leaflet webmap based on a JSON configuration file

positional arguments:
  configFile  path to config.json
  destFolder  path to destination folder

optional arguments:
  -h, --help  show this help message and exit
```

## JSON config file

### Map  
`title`: title of the map  
`outputFileName`: name of html file  
`mapWidth` : map width, in pixel (px)  
`mapHeight`: map height, in pixel (px)  
`center`: lat and lng of central point of the map  

```json
"center":{  
    "lat":45.751498,
    "lng":4.828184,
    "zoom":15
}
```

### geojsonConfig  
`name`: name of the GeoJSON layer  
`addToMap`: display layer by default. Boolean  
`geojsonFilePath`: path to GeoJSON file  
`geometry`: geometry in GeoJSON format. Not to be used if geojsonFilePath is provided  
`bindPopup`: set to true to bind a popup to each feature  
`bindPopupPropertie`: the propertie to show when the feature is clicked  
`geojsonStyle`: GeoJSON layer symbology  

```json
"geojsonStyle":{  
    "color":"red",
    "weight":4,
    "opacity":0.7,
    "fill":true,
    "fillColor":"green",
    "fillOpacity":0.2
}
```

### tileLayerConfig  
`name`: name of the tileLayer  
`addToMap`: display layer by default. Boolean  
`url`: url of the tile service  
`attribution`: attribution  

```json
{  
    "name": "OpenTopoMap",
    "addToMap":false,
    "url":"https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    "attribution":"Map data: [...]"
} 
```

### wmsConfig  
`name`: name of the WMS layer  
`addToMap`: display layer by default. Boolean  
`url`: url of the WMS service  
`layers`: layers to display  

### Full exemple
```json
{  
   "title":"Leaflet Generator - map",
   "outputFileName":"multi.html",
   "mapWidth": "500px",
   "mapHeight": "700px",
   "center":{  
      "lat":45.751498,
      "lng":4.828184,
      "zoom":15
   },
   "geojsonConfig":[
      {  
         "name": "Place Carnot",
         "addToMap":true,
         "geometry":{  
            "type":"FeatureCollection",
            "features":[  
               {  
                  "type":"Feature",
                  "properties":{  

                  },
                  "geometry":{  
                     "type":"Polygon",
                     "coordinates":[  
                        [  
                           [  
                              4.826173782348632,
                              45.75144473708562
                           ],
                           [  
                              4.828813076019287,
                              45.75074102179696
                           ],
                           [  
                              4.829306602478027,
                              45.75265750218635
                           ],
                           [  
                              4.826173782348632,
                              45.75144473708562
                           ]
                        ]
                     ]
                  }
               }
            ]
         },
         "geojsonStyle":{  
            "color":"red",
            "weight":4,
            "opacity":0.7,
            "fill":true,
            "fillColor":"green",
            "fillOpacity":0.2
         }
      },
      {
        "name": "Margeriaz",
        "addToMap":false,
        "geojsonFilePath":"margeriaz.geojson",
        "geometry": "",
        "geojsonStyle":{
          "color": "black",
          "weight": 5,
          "opacity":0.7,
          "fill":false,
          "fillColor":"green",
          "fillOpacity":0.2
        }
      }
   ],
   "tileLayerConfig":[  
      {  
         "name": "OpenTopoMap",
         "addToMap":false,
         "url":"https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
         "attribution":"[...]"
      },
      {
        "name": "OSM light",
        "addToMap":true,
        "url": "https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png",
        "attribution": "[...]"
      }
   ],
   "wmsConfig":[
      {  
         "name": "Silos à verre",
         "addToMap":false,
         "url":"https://download.data.grandlyon.com/wms/grandlyon",
         "layers":"gic_collecte.gicsiloverre"
      },
      {
         "name": "Stations Vélo'v",
         "addToMap":true,
         "url":"https://download.data.grandlyon.com/wms/grandlyon",
         "layers": "pvo_patrimoine_voirie.pvostationvelov"
      }
   ]
}
```