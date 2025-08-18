try:
    import keras
except ImportError as e:
    raise ImportError(
        "The keras package is not installed. It can be installed using 'pip install keras'."
    ) from e

from packaging import version

MIN_KERAS_VERSION = "3.10.0"

if version.parse(keras.__version__) >= version.parse(MIN_KERAS_VERSION):
    from keras.src.layers.convolutional.base_conv import BaseConv
    from keras.src.layers.convolutional.base_conv_transpose import BaseConvTranspose
    from keras.src.layers.convolutional.base_separable_conv import BaseSeparableConv
    from keras.src.layers.convolutional.conv1d import Conv1D
    from keras.src.layers.convolutional.conv1d_transpose import Conv1DTranspose
    from keras.src.layers.convolutional.conv2d import Conv2D
    from keras.src.layers.convolutional.conv2d_transpose import Conv2DTranspose
    from keras.src.layers.convolutional.conv3d import Conv3D
    from keras.src.layers.convolutional.conv3d_transpose import Conv3DTranspose

else:
    """ 
    Keras versions <3.10.0 had faulty serialization code for Convolutional layers,
    which throw an error once the activation function was defined as a layer, e.g.,
    `activation=layers.ReLU(negative_slope=0.1)`, 
    c.f. https://github.com/keras-team/keras/issues/21088.

    The following implementations fix that problem for Keras<3.10.0

    """
    
    from .base_conv import MyBaseConv as BaseConv
    from .base_conv import MyBaseConvTranspose as BaseConvTranspose
    from .base_conv import MyBaseSeparableConv as BaseSeparableConv
    from .conv1d import Conv1D, Conv1DTranspose
    from .conv2d import Conv2D, Conv2DTranspose
    from .conv3d import Conv3D, Conv3DTranspose
