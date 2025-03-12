#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Alen Mangafić
"""
import os
import h5py
import rasterio
import numpy as np
from rasterio.windows import Window

# Paths
bands_directory = "/path/to/s2/vrt"
label_file = "/path/to/classification/S2GLC_Europe_2017_clipped_20m.tif"
output_h5 = "/path/to/wherever/ard.h5"

compression_type = "gzip"
tile_size = 256  

def window_generator(width, height, tile_size):
    """Yield rasterio Windows for chunked reading."""
    for row_off in range(0, height, tile_size):
        for col_off in range(0, width, tile_size):
            win_width = min(tile_size, width - col_off)
            win_height = min(tile_size, height - row_off)
            yield Window(col_off, row_off, win_width, win_height), (row_off, col_off, win_height, win_width)

# Get VRT files
vrt_files = sorted(f for f in os.listdir(bands_directory) if f.endswith(".vrt"))
if not vrt_files:
    raise Exception("No VRT files found.")

with h5py.File(output_h5, "w") as h5f:
    for file_name in vrt_files:
        file_path = os.path.join(bands_directory, file_name)
        parts = file_name.split('_')
        dataset_name = f"{parts[1]}_{parts[0]}" if len(parts) >= 3 else os.path.splitext(file_name)[0]

        with rasterio.open(file_path) as src:
            height, width = src.height, src.width
            dset = h5f.create_dataset(
                dataset_name, shape=(height, width), dtype="float32",
                chunks=(tile_size, tile_size), compression=compression_type
            )

            for win, (row_off, col_off, win_height, win_width) in window_generator(width, height, tile_size):
                data_block = src.read(1, window=win).astype(np.float32)
                data_block[data_block == 0] = np.nan
                dset[row_off:row_off+win_height, col_off:col_off+win_width] = data_block

    with rasterio.open(label_file) as src:
        height, width = src.height, src.width
        dset_label = h5f.create_dataset(
            "labels_2017", shape=(height, width), dtype="uint8",
            chunks=(tile_size, tile_size), compression=compression_type
        )

        for win, (row_off, col_off, win_height, win_width) in window_generator(width, height, tile_size):
            dset_label[row_off:row_off+win_height, col_off:col_off+win_width] = src.read(1, window=win).astype(np.uint8)
