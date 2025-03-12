#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Alen Mangafić
"""
import os
import glob
import subprocess

# Base directory where Sentinel-2 data is stored
base_dir = "/media/eouser/..."
years = range(2017, 2023)
bands = ["B04_20m", "B11_20m", "B12_20m"]

# Extent of our choice
common_extent = (3769660, 2336620, 5109780, 3489900)

# Directory to store fixed VRTs
vrt_output_dir = os.path.join(base_dir, "vrt")
os.makedirs(vrt_output_dir, exist_ok=True)

for band in bands:
    all_rasters = []
    for year in years:
        band_dir = os.path.join(base_dir, str(year), band)
        if os.path.exists(band_dir):
            all_rasters.extend(glob.glob(os.path.join(band_dir, "*.tif")))
    
    if not all_rasters:
        print(f"No rasters found for band {band}, skipping.")
        continue

    vrt_path = os.path.join(vrt_output_dir, f"{band}.vrt")
    cmd = [
        "gdalbuildvrt",
        "-resolution", "user",
        "-tr", "20", "20",
        "-te",
        str(common_extent[0]),
        str(common_extent[1]),
        str(common_extent[2]),
        str(common_extent[3]),
        "-overwrite",
        vrt_path
    ] + all_rasters

    print("Running command:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Created VRT: {vrt_path}")
