#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Alen Mangafić
"""
import h5py

h5_file = "/media/ard.h5"

with h5py.File(h5_file, "r") as h5f:
    print("Datasets in HDF5 file:")
    for dataset in h5f.keys():
        print(f"{dataset}: {h5f[dataset].shape}, {h5f[dataset].dtype}")
