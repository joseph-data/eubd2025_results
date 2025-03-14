import json
import numpy as np
from pathlib import Path
import datetime
import getpass

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import geopandas as gpd
import json
from ipyleaflet import Map, GeoJSON, basemaps

from sentinelhub import (
    SHConfig,
    Geometry,
    DataCollection,
    MimeType,
    SentinelHubDownloadClient,
    SentinelHubRequest,
    bbox_to_dimensions,
)

# Create data directory
data_dir = Path("mystorage/data")
data_dir.mkdir(exist_ok=True)

# Norway fjord simplified
norway_bbox = (4.5, 60.0, 7.5, 61.5)
center_lon = (norway_bbox[0] + norway_bbox[2]) / 2
center_lat = (norway_bbox[1] + norway_bbox[3]) / 2
width = (norway_bbox[2] - norway_bbox[0]) * 0.6
height = (norway_bbox[3] - norway_bbox[1]) * 0.7

# Create fjord shape
fjord_coords = [
    [center_lon - width/2, center_lat - height/2],
    [center_lon - width/4, center_lat - height/4],
    [center_lon, center_lat - height/8],
    [center_lon + width/4, center_lat - height/4],
    [center_lon + width/2, center_lat - height/2],
    [center_lon + width/3, center_lat],
    [center_lon + width/4, center_lat + height/3],
    [center_lon, center_lat + height/2],
    [center_lon - width/4, center_lat + height/3],
    [center_lon - width/3, center_lat],
    [center_lon - width/2, center_lat - height/2]
]

# Create smaller fjords around the main one
small_fjords = []
for i in range(3):
    # Adjust position and size
    shift_lon = np.random.uniform(-0.3, 0.3)
    shift_lat = np.random.uniform(-0.2, 0.2)
    size_factor = np.random.uniform(0.2, 0.4)
    
    # Create smaller fjord
    small_fjord_coords = []
    for x, y in fjord_coords:
        new_x = center_lon + (x - center_lon) * size_factor + shift_lon
        new_y = center_lat + (y - center_lat) * size_factor + shift_lat
        small_fjord_coords.append([new_x, new_y])
    
    small_fjords.append({
        "type": "Feature",
        "properties": {
            "name": f"Small Fjord {i+1}",
            "description": f"Smaller fjord in Norway",
            "water": "fjord",
            "size": "small"
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [small_fjord_coords]
        }
    })

fjord_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Sognefjord",
                "description": "Example fjord in Norway",
                "water": "fjord",
                "size": "large"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [fjord_coords]
            }
        }
    ] + small_fjords
}

# Finland lake simplified
finland_bbox = (24.5, 61.0, 29.5, 63.0)
center_lon = (finland_bbox[0] + finland_bbox[2]) / 2
center_lat = (finland_bbox[1] + finland_bbox[3]) / 2
width = (finland_bbox[2] - finland_bbox[0]) * 0.5
height = (finland_bbox[3] - finland_bbox[1]) * 0.5

# Generate lake shape
theta = np.linspace(0, 2*np.pi, 30)
lake_coords = [[center_lon + width/2 * np.cos(t), center_lat + height/2 * np.sin(t)] for t in theta]

# Create smaller lakes
small_lakes = []
for i in range(5):
    # Adjust position and size
    new_center_lon = np.random.uniform(finland_bbox[0], finland_bbox[2])
    new_center_lat = np.random.uniform(finland_bbox[1], finland_bbox[3])
    new_width = np.random.uniform(0.1, 0.3) * width
    new_height = np.random.uniform(0.1, 0.3) * height
    
    # Generate lake shape
    lake_theta = np.linspace(0, 2*np.pi, 20)
    small_lake_coords = [[new_center_lon + new_width * np.cos(t), new_center_lat + new_height * np.sin(t)] for t in lake_theta]
    
    small_lakes.append({
        "type": "Feature",
        "properties": {
            "name": f"Small Lake {i+1}",
            "description": f"Smaller lake in Finland",
            "water": "lake",
            "size": "small"
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [small_lake_coords]
        }
    })

lake_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Saimaa",
                "description": "Example lake in Finland",
                "water": "lake",
                "size": "large"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [lake_coords]
            }
        }
    ] + small_lakes
}

# Save the GeoJSON files
with open(data_dir / "norway_fjord.geojson", 'w') as f:
    json.dump(fjord_geojson, f)

with open(data_dir / "finland_lake.geojson", 'w') as f:
    json.dump(lake_geojson, f)

print("Created GeoJSON files:")
print(f"1. Norway Fjord: {data_dir / 'norway_fjord.geojson'}")
print(f"2. Finland Lake: {data_dir / 'finland_lake.geojson'}")
