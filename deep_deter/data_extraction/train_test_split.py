import os
import hashlib
import shutil
from typing import List


def ensure_directories_exist(paths: List[str]):
    """ Ensure all listed directories exist, create them if they do not. """
    for path in paths:
        os.makedirs(path, exist_ok=True)


def hash_file_id(file_id: str) -> int:
    """ Return a hash value between 0 and 99 inclusive for a given file ID. """
    return int(hashlib.sha256(file_id.encode()).hexdigest(), 16) % 100


def assign_files_to_datasets(base_dir: str, percentage_train: float):
    # Directories for features and labels
    labels_dir = os.path.join(base_dir, 'processed', 'labels')
    features_dir = os.path.join(base_dir, 'processed', 'masked_feature_bands')

    # Directories for training and testing splits under model_inputs
    model_inputs_dir = os.path.join(base_dir, 'model_inputs')
    train_labels_dir = os.path.join(model_inputs_dir, 'train_labels')
    test_labels_dir = os.path.join(model_inputs_dir, 'test_labels')
    train_features_dir = os.path.join(model_inputs_dir, 'train_features')
    test_features_dir = os.path.join(model_inputs_dir, 'test_features')

    # Ensure all directories exist
    ensure_directories_exist([train_labels_dir, test_labels_dir, train_features_dir, test_features_dir])

    # Get a list of label files and feature files
    label_files = [f for f in os.listdir(labels_dir) if f.endswith('.tif')]
    feature_files = [f for f in os.listdir(features_dir) if f.endswith('_bands.tif')]

    # Ensure the IDs match
    ids = set(f.split('.')[0] for f in label_files)
    assert ids == set(f.split('_bands')[0] for f in feature_files), "Mismatch in file IDs between labels and features"

    # Copy files to their respective directories based on the hash
    for file_id in ids:
        hash_value = hash_file_id(file_id)
        is_train = hash_value < percentage_train

        # Define source and destination paths
        label_src = os.path.join(labels_dir, f"{file_id}.tif")
        feature_src = os.path.join(features_dir, f"{file_id}_bands.tif")

        if is_train:
            label_dst = os.path.join(train_labels_dir, f"{file_id}.tif")
            feature_dst = os.path.join(train_features_dir, f"{file_id}_bands.tif")
        else:
            label_dst = os.path.join(test_labels_dir, f"{file_id}.tif")
            feature_dst = os.path.join(test_features_dir, f"{file_id}_bands.tif")

        # Copy files
        shutil.move(label_src, label_dst)
        shutil.move(feature_src, feature_dst)
