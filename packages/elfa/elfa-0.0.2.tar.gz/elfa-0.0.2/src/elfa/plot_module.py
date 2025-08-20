"""Plot module"""

import os
import sys
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from .constants import IMG_SIZE
from .utils import resize_map

matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["font.family"] = "STIXGeneral"


def plot_gallery(
    images: np.ndarray,
    images_shape: tuple[int],
    n_col: int = 1,
    n_row: int = 1,
    cmap: Any = plt.cm.gray,
    figsize: tuple | None = None,
    path: str | os.PathLike = "",
):
    """
    Plots different images as a grid (in subplots).

    Parameters
    -------
    images : array-like of shape (nº pixels, nº images)
        Batch of images to be plotted.

    images_shape : duple (int, int)
        Tuple specifying the shape (height, width) of each individual image.

    n_col : int, default=1
        Number of columns in the grid.

    n_row : int, default=1
        Number of rows in the grid.

    cmap : matplotlib colormap, default=plt.cm.gray
        Colormap to be used for displaying the images.

    figsize : duple (int, int), default=None
        Shape of the entire figure. If None, it defaults to (2*n_cols, 2*n_row).

    path : str or path-like, default=""
        Saving path.

    Returns
    -------
    matplotlib.figure.Figure
        The matplotlib figure object containing the plotted gallery.
    """
    if figsize == None:
        figsize = (2 * n_col, 2 * n_row)
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(n_row, n_col, hspace=0, wspace=0)
    axs = gs.subplots(sharex=True, sharey=True)
    n = 0
    _, b = images.shape
    N = n_col * n_row
    images_copy = images
    if N == 1:
        image = images_copy.reshape(images_shape)
        axs.imshow(image, cmap=cmap)
    else:
        for ax in axs.flat:
            if n < b:
                image = images_copy[:, n].reshape(images_shape)
                ax.imshow(image, cmap=cmap)
            n = n + 1

    fig.subplots_adjust(wspace=0, hspace=0)

    plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[])
    if path:
        fig.savefig(path, dpi=500, bbox_inches="tight")
    plt.show()


def plot_matrix(
    matrix: np.ndarray,
    figsize: tuple | None = None,
    cmap: Any = "RdBu_r",
    path: str | os.PathLike = "",
):
    """
    Plots a matrix as a grid with colors in each cell corresponding to the value of that coefficient in the matrix.

    Parameters
    -------
    matrix : array-like
        Matrix to be plotted.

    figsize : duple (int,int)
        Shape of the entire figure. If None, it defaults to matrix shape.

    cmap : matplotlib colormap, default="RdBu_r"
        Colormap to be used for displaying the matrix.

    path : str or path-like, default=""
        Saving path.

    Returns
    ------
    matplotlib.figure.Figure
        The matplotlib figure object containing the plotted matrix.
    """
    if figsize == None:
        figsize = matrix.shape
    maxValue = np.abs(matrix).max()
    plt.figure(figsize=figsize)
    plt.imshow(matrix, cmap=cmap, vmax=maxValue, vmin=-maxValue)
    if matrix.shape[0] < matrix.shape[1]:
        plt.colorbar(location="bottom", aspect=40, pad=0.01)
    else:
        plt.colorbar(location="left", aspect=40, pad=0.01)

    if path:
        plt.savefig(path, dpi=500, bbox_inches="tight")

    plt.show()


def images_montage(images: np.ndarray, path: str | os.PathLike = ""):
    """
    Montage of images.

    Parameters
    -------
    images : array-like
        Images to be plotted as an array of shape (height, width, channels, num_images).

    path : str or path-like, default=""
        Saving path.

    Returns
    -------
    matplotlib.figure.Figure
        The matplotlib figure object containing the plotted images.
    """
    d = images.shape[3]
    n_row = round(np.sqrt(d))
    fig = plt.figure()
    gs = fig.add_gridspec(n_row, n_row, hspace=0, wspace=0)
    axs = gs.subplots(sharex=True, sharey=True)
    n = 0
    for ax in axs.flat:
        if n < d:
            ax.imshow(images[:, :, :, n], interpolation="bilinear")
        n = n + 1
    if path:
        plt.savefig(path, dpi=500, bbox_inches="tight")

    plt.show()


def similar_to_factor(
    WT: np.ndarray,
    n_factor: int,
    output: np.ndarray,
    latent_factors: np.ndarray,
    num_img: int,
    img_size: tuple,
    max_value: float = 0.8,
    path: str | os.PathLike = "",
):
    """
    Displays a given latent factor and the most similar channels (i.e., observed variables).
    In order to obtain "similar_to_channel" you only need to provide WT as WT.transpose(), n_factor as the number of the selected channel, output as latent_factors, and latent_factors as output.

    Parameters
    -------
    WT : array-like of shape (n_component, n_features)
        Factor loading matrix.

    n_factor : int
        Selected latent factor.

    output : array-like of shape (n_samples, n_features)
        Data (observed variables).

    latent_factors : array-like of shape (n_samples, n_components)
        Latent factors obtained from the data.

    num_img : int
        Selected image from the batch.

    img_size : duple (int,int)
        Size of the data samples (i.e., height and width of the activation map).

    max_value : float, default=0.8
        The features (channels) whose correlation with the selected latent factor is greater than max_value are selected.

    path : str or pth-like, default=""
        Saving path.

    Returns
    -------
    matplotlib.figure.Figure
        The matplotlib figure object containing the plotted factors and channels.
    """
    Wrow = abs(WT[n_factor, :])
    h = img_size[0]
    w = img_size[1]
    num_pixels = h * w
    data = output[num_pixels * num_img : num_pixels * (num_img + 1), Wrow > max_value]
    factor = latent_factors[num_pixels * num_img : num_pixels * (num_img + 1), n_factor]

    num_channels = data.shape[1]
    if num_channels == 1:
        sys.exit("Just one match in", np.where(Wrow > max_value)[0][0])
    ncol = np.minimum(np.floor(num_channels / 2).astype("int"), 4)
    ncol = ncol + 2

    rel = w / h
    fig = plt.figure(figsize=(ncol * rel, 2), constrained_layout=False)
    gs = fig.add_gridspec(2, ncol, wspace=0, hspace=0)

    ax0 = fig.add_subplot(gs[:, :2])
    factor = factor.reshape(img_size, order="F")
    ax0.imshow(factor, cmap=plt.cm.gray)
    ax0.set_xticks([])
    ax0.set_yticks([])

    row = 0
    col = 2
    m = (ncol - 2) * 2
    for i in range(m):
        col = col + row
        row = i % 2
        ax = fig.add_subplot(gs[row, col])
        data0 = data[:, i].reshape(img_size, order="F")
        ax.imshow(data0, cmap=plt.cm.gray)
        ax.set_xticks([])
        ax.set_yticks([])

    if path:
        fig.savefig(path, dpi=500, bbox_inches="tight")
    plt.show()


def plot_attributions(
    num_images: int,
    images: list,
    attribution_maps: dict,
    img_size: tuple = IMG_SIZE,
    mode: str | None = None,
    cmap: Any = "jet",
    path: str | os.PathLike = "",
):
    """
    Displays the attribution maps associated to given images.

    Parameters
    -------
    num_images : int
        Number of images.

    images : list
        List of images to show.

    attribution_maps : dict
        Dictionary of the different types of attribution maps computed for all the images given. The keys of the dictionary are the names of the attribution methods, and the values are the corresponding attribution maps, with shape (num_images, height, width).

    img_size : tuple, default=IMG_SIZE
        Size of the images (height, width) to be displayed. If None, the original size of the images is used.

    mode : str, default=None
        Display mode, which could be superposition or mask. If None, the heatmap alone is displayed.

    cmap : matplotlib colormap, default=plt.cm.jet
        Colormap to be used for displaying the images.

    path : str or path-like, default=""
        Saving path.

    Returns
    -------
    matplotlib.figure.Figure
        The matplotlib figure object containing the plotted heatmaps.
    """
    keys = list(attribution_maps.keys())
    ncols = len(keys) + 1
    fig, axes = plt.subplots(
        nrows=num_images, ncols=ncols, figsize=(ncols + 1, num_images + 0.5)
    )
    for i in range(num_images):
        img = np.uint8(images[i])
        axes[i, 0].imshow(img)
        axes[i, 0].axis("off")
        for j in range(ncols - 1):
            h_img = attribution_maps[keys[j]][i]
            if mode == "mask":
                h_img = resize_map(h_img, size=img_size)
                h_img = (h_img - np.min(h_img)) / (np.max(h_img) - np.min(h_img))
                heatmap = np.uint8(255 * h_img)
                img_feature = (
                    img * (heatmap[:, :, None].astype(np.float64) / np.amax(heatmap))
                ).astype(np.uint8)
                axes[i, j + 1].imshow(
                    img_feature, alpha=1, interpolation="gaussian", cmap=plt.cm.jet
                )
            elif mode == "superposition":
                h_img = resize_map(h_img, size=img_size)
                h_img = (h_img - np.min(h_img)) / (np.max(h_img) - np.min(h_img))
                heatmap = np.uint8(255 * h_img)

                axes[i, j + 1].imshow(img)
                axes[i, j + 1].imshow(heatmap, alpha=0.5, cmap=cmap)
            else:
                axes[i, j + 1].imshow(h_img, cmap=cmap)
            if i == 0:
                axes[i, j + 1].title.set_text(keys[j])
            axes[i, j + 1].axis("off")
    plt.tight_layout()
    if path:
        fig.savefig(path, dpi=500, bbox_inches="tight")
    plt.show()
