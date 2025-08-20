"""Module to process convolutional neural networks."""

import numpy as np
import tensorflow as tf
from keras import Model

from . import utils


def get_conv_indx(model: Model) -> list:
    """Apply to a NN to obtain the indexes of all the convolutional layers. Be aware that the output of a conv layer includes the activation function.

    Parameters
    ----------
    model : Neural Network Model

    Returns
    -------
    idxConvLayers : list
        Indices of conv layers according to the model layers .
    """
    # Get the layers of the model
    layers = model.layers
    len_layers = len(layers)
    idx_conv_layers = []
    # Obtain only the convolutional ones
    for i in range(len_layers):
        if isinstance(layers[i], tf.keras.layers.Conv2D):
            idx_conv_layers.append(i)

    return idx_conv_layers


def reshape_data(data: np.ndarray) -> np.ndarray:
    """
    Reshapes a 4-dimensional NumPy array into a 2-dimensional array.

    The input array is expected to have the shape (b, h, w, n). The output array will have the shape (h * w * b, n), effectively flattening
    the spatial and batch dimensions into a single dimension.

    Parameters
    ----------
    data : array-like of shape (b, h, w, n)

    Returns
    -------
    Array-like of shape (h * w * b, n)
    """
    b, h, w, n = data.shape
    return data.reshape(h * w * b, n)


def partial_model(
    base_model: Model, num_conv: int | None, id_layer: int | None = None
) -> Model:
    """Apply to a NN to return the output of a certain convolutional layer.

    Parameters
    ----------
    base_model : Neural Network Model

    num_conv : int
        Convolutional layer (first=0, second=1,...).

    id_layer: int
        Index of the output layer, according to base_model.layers. It can be used instead of num_conv.

    Returns
    -------
    partial_model :Neural Network Model with output the selected layer.
    """
    if id_layer is not None:
        out_layers = [base_model.layers[id_layer].output]
    else:
        # Get the indices of the convolutional layers
        idx_conv_layers = get_conv_indx(base_model)
        # Check that the index given is right
        if num_conv > len(idx_conv_layers) - 1 and num_conv != -1:
            raise ValueError(
                "Not so many convolutional layers"
                ": %d > %d" % (num_conv, len(idx_conv_layers) - 1)
            )

        out_layers = [base_model.layers[idx_conv_layers[num_conv]].output]
    # Obtain the modified NN
    partial_model = tf.keras.Model(inputs=base_model.input, outputs=out_layers)

    return partial_model


def conv_output_data(partial_model: Model, img: np.ndarray) -> tuple:
    """Obtain the output of a convolutional layer in the required data shape for layer factor analysis. For this, a modified Neural Network is used, which returns the desired output with shape (batch_size, hpx, wpx, num_channels).

    Parameters
    ----------
    partial_model : Neural Network Model
        Modified Model.

    img : array-like of shape (batch_size, input_size, input_size, input_channels)
        Input batch of images already preprocessed for the given Model.

    Returns
    -------
    data : array-like of shape (hpx*wpx*batch_size, num_channels)
        Output of partial model reshaped.

    hpx : int
        The height of the feature map produced by the partial model.

    wpx : int
        The width of the feature map produced by the partial model.

    num_channels :  int
        Number of output channels.
    """
    # Get the output of the model
    conv_features = partial_model.predict(img)
    _, hpx, wpx, num_channels = conv_features.shape
    # Reshape it
    data = reshape_data(conv_features)

    return data, hpx, wpx, num_channels


def get_fa_input(
    batch_size: int,
    dstrain: tf.data.Dataset,
    img_size: tuple,
    partial_model: Model,
    normalize: bool = True,
    ite: int = 20,
):
    """
    Prepares input data for the Explainable Layer Factor Analysis method by processing batches of images through a partial model and optionally normalizing the data.

    Parameters
    ----------
    batch_size : int
        The batch size.

    dstrain : tf.data.Dataset
        The dataset to draw batches of images from.

    img_size : duple (int, int)
        The target size of the input images (height, width).

    partial_model : Neural Network Model
        A modified neural network model which outputs the activation maps of the desired layer, used to process the images and extract features.

    normalize : bool, defaults=True
        Whether to normalize the extracted data.

    ite : intm defaults=20
        The maximum number of iterations to attempt normalization if the standard deviation of the data contains zero values.

    Returns
    -------
    data : array-like of shape (batch_size*hpx*wpx, num_channels)
        The processed and optionally normalized feature data.

    hpx : int
        The height of the feature map produced by the partial model.

    wpx : int
        The width of the feature map produced by the partial model.

    num_channels : int
        The number of channels in the feature map.
    """
    # Obtain images batch
    images_batch, _ = utils.get_batch(batch_size, dstrain, img_size)

    # Obtain input data for FA method
    data, hpx, wpx, num_channels = conv_output_data(partial_model, images_batch)

    # Normalize input data
    it = 0
    if normalize:
        while 0 in np.std(data, axis=0) and it < ite:
            it += 1
            print("Standard deviation has a zero value.")
            images_batch, _ = utils.get_batch(batch_size, dstrain, img_size)
            data, hpx, wpx, num_channels = conv_output_data(partial_model, images_batch)
        if it == ite:
            print(
                "Standard deviation has a zero value in all iterations. It will be only normalized by the mean."
            )
            data = data - np.mean(data, axis=0)
        else:
            data = (data - np.mean(data, axis=0)) / np.std(data, axis=0)

    return data, hpx, wpx, num_channels
