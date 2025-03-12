#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Alen Mangafić
"""
import requests
import pickle
import rasterio
import concurrent.futures
import time
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.crs import CRS

# STAC API and processing parameters
BASE_URL = "https://stac.dataspace.copernicus.eu/v1/search"
bands = ['B12_20m', 'B11_20m', 'B04_20m']
output_crs = CRS.from_epsg(3035)
years = range(2023, 2024)
processed_tiles_path = "/path/to/processed_tiles.pkl"

# Load processed tiles
if os.path.exists(processed_tiles_path):
    with open(processed_tiles_path, 'rb') as f:
        processed_tiles = pickle.load(f)
else:
    processed_tiles = set()

for year in years:
    pickle_path = f"/path/to/{year}_query.pkl"
    all_features = []

    # Load previous queries
    if os.path.exists(pickle_path):
        print(f"Loading saved features for {year}")
        with open(pickle_path, 'rb') as f:
            all_features = pickle.load(f)

    # Query STAC if no saved data
    if not all_features:
        print(f"Fetching new data for {year}...")
        query = {
            "collections": ["sentinel-2-l2a"],
            "datetime": f"{year}-05-01T00:00:00Z/{year}-06-01T23:59:59Z",
            "limit": 1000,
            "query": {"eo:cloud_cover": {"gte": 0, "lt": 6}},
            "intersects": {
                "type": "Polygon",
                "coordinates": [[
                    [3.46, 44.90], [18.68, 44.90], [18.68, 53.71],
                    [3.46, 53.71], [3.46, 44.90]
                ]]
            }
        }

        next_url = BASE_URL
        while next_url:
            try:
                response = requests.post(next_url, json=query) if next_url == BASE_URL else requests.get(next_url)
                response.raise_for_status()
                data = response.json()
                all_features.extend(data.get("features", []))
                next_url = next((link["href"] for link in data.get("links", []) if link.get("rel") == "next"), None)
            except requests.HTTPError as e:
                print(f"Request failed: {e}")
                break

        with open(pickle_path, 'wb') as f:
            pickle.dump(all_features, f)
        print(f"Saved features for {year}")

    if not all_features:
        print(f"No data for {year}, skipping...")
        continue

    # Select the largest scene per tile
    scenes = {}
    for feature in all_features:
        assets = feature.get("assets", {})
        tile_id = feature.get("id", "").split('_')[-2]
        total_size = sum(assets[band].get('file:size', 0) for band in bands if band in assets)
        if tile_id and (tile_id not in scenes or scenes[tile_id]['size'] < total_size):
            scenes[tile_id] = {'assets': assets, 'size': total_size}

    if not scenes:
        print(f"No valid scenes for {year}, skipping.")
        continue

    def process_band(band, href, year, tile_id):
        start_time = time.time()

        if (year, tile_id, band) in processed_tiles:
            print(f"Skipping {year}, {tile_id}, {band}")
            return

        filename = href.split('/')[-1].replace('.jp2', '_EPSG3035.tif')
        output_dir = f"/path/to/{year}/{band}"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/{filename}"

        if os.path.exists(output_path):
            print(f"File {output_path} exists, skipping.")
            return

        with rasterio.open(f'/vsis3/{href[5:]}') as src:
            transform, width, height = calculate_default_transform(
                src.crs, output_crs, src.width, src.height, *src.bounds
            )

            kwargs = src.meta.copy()
            kwargs.update({
                'crs': output_crs, 'transform': transform,
                'width': width, 'height': height,
                'driver': 'GTiff', 'compress': 'LZW'
            })

            with rasterio.open(output_path, 'w', **kwargs) as dst:
                reproject(
                    source=rasterio.band(src, 1),
                    destination=rasterio.band(dst, 1),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=output_crs,
                    resampling=Resampling.nearest
                )

        print(f"Processed {year}, {tile_id}, {band} in {time.time() - start_time:.2f}s")
        processed_tiles.add((year, tile_id, band))
        with open(processed_tiles_path, 'wb') as f:
            pickle.dump(processed_tiles, f)

    # Process in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [
            executor.submit(process_band, band, assets[band]["href"], year, tile_id)
            for tile_id, scene_data in scenes.items()
            for band in bands if band in scene_data["assets"] and scene_data["assets"][band]["href"].startswith("s3://")
        ]
        concurrent.futures.wait(futures)
