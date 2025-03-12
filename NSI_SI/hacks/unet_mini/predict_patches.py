import os
import sys
import numpy as np
import h5py
from pathlib import Path
from tensorflow.keras.models import load_model
import subprocess

# GRASS GIS Configuration
os.environ["GISBASE"] = "/usr/local/grass84"
os.environ["PATH"] = f"/usr/local/grass84/bin:/usr/local/grass84/scripts:{os.environ['PATH']}"
os.environ["LD_LIBRARY_PATH"] = f"/usr/local/grass84/lib:{os.environ.get('LD_LIBRARY_PATH', '')}"
os.environ["PYTHONPATH"] = f"/usr/local/grass84/etc/python:{os.environ.get('PYTHONPATH', '')}"

sys.path.append(subprocess.check_output(["grass", "--config", "python_path"], text=True).strip())

import grass.script as gs
import grass.jupyter as gj
import grass.script.array as garray

# GRASS GIS Database Configuration
gisdbase = Path("/path/to/grass_baza/")
session = gj.init(Path(gisdbase, "some_project"))
os.environ['GRASS_OVERWRITE'] = '0'  # Overwriting not permitted, by default is 1, so do as you dare

def predict_and_export(model_path, h5_file_path, feature_layers, chunk_indices, output_layer, chunk_size):
    print(f"Loading model from {model_path}")
    model = load_model(model_path)

    with h5py.File(h5_file_path, "r") as h5file:
        n_rows, n_cols = h5file[f"/features/{feature_layers[0]}"].shape

    predictions = np.zeros((n_rows, n_cols), dtype=np.uint8)

    print(f"Processing {len(chunk_indices)} chunks...")
    for chunk_idx in chunk_indices:
        row_start = chunk_idx * chunk_size
        row_end = min(row_start + chunk_size, n_rows)

        chunk_features = []
        with h5py.File(h5_file_path, "r") as h5file:
            for col_start in range(0, n_cols, chunk_size):
                col_end = min(col_start + chunk_size, n_cols)

                tile = []
                for layer in feature_layers:
                    layer_data = h5file[f"/features/{layer}"][row_start:row_end, col_start:col_end]
                    if layer_data.shape != (chunk_size, chunk_size):
                        layer_data = np.pad(
                            layer_data,
                            ((0, chunk_size - layer_data.shape[0]), (0, chunk_size - layer_data.shape[1])),
                            mode="constant",
                        )
                    tile.append(layer_data)
                chunk_features.append(np.stack(tile, axis=-1))

        X_test = np.array(chunk_features)

        print(f"Predicting chunk {chunk_idx + 1}/{len(chunk_indices)}...")
        predictions_chunk = model.predict(X_test)

        if predictions_chunk.shape[-1] > 1:
            predictions_chunk = np.argmax(predictions_chunk, axis=-1)
        else:
            predictions_chunk = (predictions_chunk > 0.5).astype(np.uint8)

        for i, col_start in enumerate(range(0, n_cols, chunk_size)):
            col_end = min(col_start + chunk_size, n_cols)
            predictions[row_start:row_end, col_start:col_end] = predictions_chunk[i, :row_end - row_start, :col_end - col_start]

    print(f"Finished predictions. Writing to GRASS GIS layer: {output_layer}")
    write_raster_grass(predictions, output_layer)

def write_raster_grass(array, output_name):
    out_raster = garray.array()
    out_raster[...] = array
    out_raster.write(output_name, overwrite=True)
    print(f"Raster written to GRASS GIS as: {output_name}")

