#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Alen Mangafić
"""
import subprocess

# Input and output file paths
label_file = "/media/eouser/.../S2GLC_Europe_2017_v1.2.tif"
clipped_label_file = "/media/eouser/f.../S2GLC_Europe_2017_clipped_20m.tif"

# Fixed extent (minX, minY, maxX, maxY)
common_extent = (3769660, 2336620, 5109780, 3489900)

# Build the gdalwarp command with:
# -te: sets the target extent
# -tr: sets the target resolution to 20 x 20 meters
# -r mode: uses mode resampling (best for categorical data)
cmd = [
    "gdalwarp",
    "-te", str(common_extent[0]), str(common_extent[1]), str(common_extent[2]), str(common_extent[3]),
    "-tr", "20", "20",
    "-r", "mode",
    "-of", "GTiff",
    label_file,
    clipped_label_file
]

print("Executing command:")
print(" ".join(cmd))
subprocess.run(cmd, check=True)
print("Clipped and resampled label saved as:", clipped_label_file)
