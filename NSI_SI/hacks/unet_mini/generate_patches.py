import numpy as np
from sklearn.model_selection import train_test_split
from grass.script import array as garray

def generate_patches(feature_layers, label_layer, patch_size, overlap, split_ratios, binary_labels=False):
    print(f"Loading features: {feature_layers}")
    features = np.stack([garray.array(layer)[:] for layer in feature_layers], axis=-1)

    try:
        labels = garray.array(label_layer)[:].astype(np.int32)
    except Exception as e:
        print(f"Error loading labels: {e}")
        return None

    if labels.size == 0:
        print("Label array is empty.")
        return None

    patches, label_patches = [], []
    for y in range(0, labels.shape[0] - patch_size, patch_size - overlap):
        for x in range(0, labels.shape[1] - patch_size, patch_size - overlap):
            patch = features[y:y + patch_size, x:x + patch_size, :]
            label_patch = labels[y:y + patch_size, x:x + patch_size]

            if binary_labels:
                label_patch = (label_patch > 0).astype(np.uint8)

            if len(np.unique(label_patch)) > 1:
                patches.append(patch)
                label_patches.append(label_patch)

    patches, label_patches = np.array(patches), np.array(label_patches)
    if len(patches) == 0:
        print("No valid patches found.")
        return None

    train_x, valid_x, train_y, valid_y = train_test_split(
        patches, label_patches, test_size=split_ratios[1], stratify=[p.flatten().mean() for p in label_patches]
    )

    return {"train": (train_x, train_y), "valid": (valid_x, valid_y), "label_name": "labels_2017"}

