import os
import h5py
import numpy as np
import time
from tensorflow.keras.callbacks import ModelCheckpoint
from train_model import train_model
from predict_patches import predict_and_export

# Configuration
h5_file_path = "ard.h5"
output_dir = "model_outputs"
checkpoint_dir = "checkpoints"
chunk_size = 256
batch_size = 8
epochs = 10

# Dataset Metadata
total_rows = #write your extent and region metadata
train_valid_row_limit = #write your extent and region metadata

# Define row splits
train_chunks = int((train_valid_row_limit // chunk_size) * 0.8)
valid_chunks = (train_valid_row_limit // chunk_size) - train_chunks
train_split = list(range(0, train_chunks))
valid_split = list(range(train_chunks, train_valid_row_limit // chunk_size))
predict_split = list(range(train_valid_row_limit // chunk_size, total_rows // chunk_size))

os.makedirs(output_dir, exist_ok=True)
os.makedirs(checkpoint_dir, exist_ok=True)

def load_data_by_chunks(h5_file_path, feature_layers, chunk_indices):
    """Load features and labels from HDF5 in chunks."""
    with h5py.File(h5_file_path, "r") as h5file:
        features, labels = [], []
        for idx in chunk_indices:
            row_start = idx * chunk_size
            row_end = min(row_start + chunk_size, h5file["labels/labels_2017"].shape[0])

            feature_chunk = np.stack([
                np.pad(
                    h5file[f"/features/{layer}"][row_start:row_end, :chunk_size],
                    ((0, chunk_size - (row_end - row_start)), (0, 0)),
                    mode="constant"
                ) for layer in feature_layers
            ], axis=-1)

            label_chunk = np.pad(
                h5file["labels/labels_2017"][row_start:row_end, :chunk_size],
                ((0, chunk_size - (row_end - row_start)), (0, 0)),
                mode="constant"
            )

            features.append(feature_chunk)
            labels.append(label_chunk)

    return np.array(features), np.array(labels)

models = [('model1', ['B04_20m.vrt', 'B11_20m.vrt', 'B12_20m.vrt'])]

for model_name, feature_layers in models:
    print(f"Processing {model_name}")
    
    train_features, train_labels = load_data_by_chunks(h5_file_path, feature_layers, train_split)
    valid_features, valid_labels = load_data_by_chunks(h5_file_path, feature_layers, valid_split)

    train_model(
        model_name=model_name,
        patches={"train": (train_features, train_labels), "valid": (valid_features, valid_labels)},
        num_classes=3,
        output_dir=output_dir,
        batch_size=batch_size,
        epochs=epochs,
        callbacks=[ModelCheckpoint(filepath=os.path.join(checkpoint_dir, f"{model_name}_best.h5"), save_best_only=True)]
    )

    predict_and_export(
        model_path=os.path.join(output_dir, f"{model_name}_best.h5"),
        h5_file_path=h5_file_path,
        feature_layers=feature_layers,
        chunk_indices=predict_split,
        output_layer=f"{model_name}_prediction",
        chunk_size=chunk_size
    )

