import csv
from collections.abc import Iterable
from typing import Any

import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds

from .constants import IMG_SIZE


def write_data(
    data: Iterable[Any], file_name: str, mode: str = "w", delimiter: str = ","
):
    """Write data in a csv file with name file_name."""
    with open(file_name, mode=mode, newline="") as file:
        writer = csv.writer(file, delimiter=delimiter)
        writer.writerow(data)


def get_batch(batch_size: int, dataset: tf.data.Dataset, img_size: tuple) -> tuple:
    """
    Batch of images of shape (batch_size, H, W, num_channels).

    Parameters
    -------
    batch_size : int

    dataset : tf.data.Dataset

    img_size : tuple (H,W)
      Shape in order to resize images if necessary.

    Returns
    -------
    images_batch : array-like
      Batch of images.

    images_list : list[np.ndarray]
      List of images.
    """
    images_list = []
    for images, labels in dataset.take(batch_size):
        images = tf.image.resize(images, img_size)
        images_list.append(images.numpy())

    images_batch = np.stack(images_list, 0)

    return images_batch, images_list


def get_batch_labels(
    batch_size: int, dataset: tf.data.Dataset, img_size: tuple
) -> tuple:
    """
    Batch of images of shape (batch_size, H, W, num_channels).

    Parameters
    -------
    batch_size : int

    dataset : tf.data.Dataset

    img_size : tuple (H,W)
      Shape in order to resize images if necessary.

    Returns
    -------
    images_batch : array-like
      Batch of images.

    images_list : list[np.ndarray]
      List of images.

    labels_list : list[int]
      List of labels.
    """
    images_list = []
    labels_list = []
    for images, labels in dataset.take(batch_size):
        images = tf.image.resize(images, img_size)
        images_list.append(images.numpy())
        labels_list.append(labels)

    images_batch = np.stack(images_list, 0)

    return images_batch, images_list, labels_list


def resize_map(map: np.ndarray, size: tuple = IMG_SIZE) -> tf.Tensor:
    return tf.image.resize(map[:, :, tf.newaxis], (size[0], size[1]))[:, :, 0]


def set_batch(images, labels, batch_size: int) -> tuple:
    """Batch of random images taken from a list, and their corresponding labels."""
    idx_batch = np.random.choice(len(images), batch_size, replace=False).astype(int)
    x_batch_list = [images[i] for i in idx_batch]
    x_batch = np.array(x_batch_list)
    y_batch = np.array([labels[i] for i in idx_batch])
    return x_batch_list, x_batch, y_batch, idx_batch


def import_tf_dataset(
    data_name: str, set_name: str, shuffle: bool = True, buffer_size: int = 10_000
):
    """
    Import a tensorflow dataset.
    Take care of the buffer_size when shuffeling.

    Parameters
    -------
    data_name : str
        Name of the dataset to import.

    set_name : str
        Name of the subset of the dataset to import (e.g., 'test', 'train', 'validation').

    shuffle : bool, default=True
        Whether to perform a new shuffle before each extraction of a subset of the dataset.

    buffer_size : int, default=10_000
        Buffer size for shuffling the dataset.

    Returns
    -------
    dataset : tf.data.Dataset
    """
    dataset_builder = tfds.builder(data_name)
    dataset_builder.download_and_prepare()
    datasets = dataset_builder.as_dataset(as_supervised=True)
    dataset: tf.data.Dataset = datasets[set_name]
    if shuffle:
        dataset = dataset.shuffle(buffer_size, reshuffle_each_iteration=True)
    return dataset
