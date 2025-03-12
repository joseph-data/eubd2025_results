#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Alen Mangafić
"""
import os

# Define the base directory where Sentinel-2 images are stored
base_dir = os.path.expanduser("/media/eouser/...")

# Define the years to check
years = [2017, 2018, 2019, 2020, 2021, 2022, 2023] # Adjust range if needed

# Define the band to check (you can change this if needed)
band_to_check = "B04_20m"  # Using B04_20m, but you can modify

# Function to extract tile names from a directory
def get_tiles_from_year(year):
    band_dir = os.path.join(base_dir, str(year), band_to_check)
    if not os.path.exists(band_dir):
        print(f"Warning: {band_dir} does not exist, skipping year {year}.")
        return set()

    # Extract tile names from filenames (e.g., T31UFT_20170610T103019_B04_20m_EPSG3035.tif)
    tiles = set()
    for file in os.listdir(band_dir):
        if file.endswith(".tif"):  # Check only GeoTIFFs
            tile_name = file.split("_")[0]  # Extract tile ID (e.g., T31UFT)
            tiles.add(tile_name)

    print(f"Found {len(tiles)} tiles for {year}")
    return tiles

# Get tile lists for each year
yearly_tiles = {year: get_tiles_from_year(year) for year in years}

# Find the common tiles across all years
common_tiles = set.intersection(*yearly_tiles.values())

# Output result
print(f"\nMinimal common tiles across all years ({len(common_tiles)} tiles):")
print(sorted(common_tiles))  # Sorted for readability
