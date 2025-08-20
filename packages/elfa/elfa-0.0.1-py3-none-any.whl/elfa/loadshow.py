"""Module to download, show and work with images"""

import os

import IPython.display as display
import numpy as np
import PIL.Image
import tensorflow as tf
import tensorflow_datasets as tfds


def load(image_path: str | os.PathLike, size: int) -> np.ndarray:
    """Open and image, resize it and return as as a NumPy array.

    Parameters
    -------
    image_path : str or path-like

    size : int

    Returns
    -------
    Image of shape (size, size).
    """
    image = PIL.Image.open(image_path)
    img = image.resize((size, size))
    return np.array(img)


def deprocess(img: np.ndarray) -> tf.Tensor:
    """Normalize an image whose values are between -1 and 1

    Parameters
    -------
    img : array-like
        Image with values between -1 and 1.

    Returns
    -------
    Image array-like with values between 0 and 255.
    """
    img = 255 * (img + 1.0) / 2.0
    return tf.cast(img, tf.uint8)


def show(img, gray: bool = False):
    """Display and image (only IPython)."""
    if gray:
        img = PIL.Image.fromarray(np.array(img, dtype="uint8")).convert("L")
    else:
        img = PIL.Image.fromarray(np.array(img, dtype="uint8"))

    display.display(img)
