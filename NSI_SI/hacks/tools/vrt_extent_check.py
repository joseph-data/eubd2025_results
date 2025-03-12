#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Alen Mangafić
"""
import os
import rasterio

bands_directory = "/media/eouser/.../s2/vrt"

# Gather all .vrt files
vrt_files = [
    os.path.join(bands_directory, f)
    for f in os.listdir(bands_directory)
    if f.endswith(".vrt")
]

extents = []
for vrt_path in vrt_files:
    with rasterio.open(vrt_path) as src:
        extents.append((vrt_path, src.bounds))

# Check if all extents match
unique_bounds = set(bounds for _, bounds in extents)

if len(unique_bounds) == 1:
    print("All VRT files have the SAME extent:", unique_bounds.pop())
else:
    print("VRT files have DIFFERENT extents:")
    for path, bounds in extents:
        print(f"{path} → {bounds}")
