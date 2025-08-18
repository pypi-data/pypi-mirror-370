# Keras Extensions
This package offers a wide range of extensions and tools for the [Keras3](https://keras.io/keras_3/) framework. Please note that this package is still in development. While all methods have a comprehensive docstring, there is no API documentation yet.

The implementation of all layers, blocks and models aligns with official Keras3 layer implementations, and subclass either `keras.layers.Layer` or `keras.models.Model`. All layers are fully serializable and can be used in `model.save()`.

# Installation
The package is hosted on [pypi.org](https://pypi.org/project/kerex/) and can be installed using pip
```
$ pip install kerex
```
which automatically installs `keras>3.0.0`. Additionally, you can use the installer with options
```
$ pip install kerex[jax]
```
which installs `jax` and `jaxlib` packages, or
```
$ pip install kerex[tensorflow]
```
which installs the `tensorflow` backend.


# Contents

## Layers
The module `kerex.layers` implements a wide variety of additional layers for Keras3.

### Fourier Neural Operator
The first class of layers are Fourier Neural Operators (FNO), cf. [Zongyi et al. (2021)](https://arxiv.org/abs/2010.08895).
The FNO layer has two parallel paths. The first path applies a spectral convolution, where the input is transformed to Fourier space, truncated to the lowest $m$ modes, multiplied by the weights, padded and then transformed back to space (or time) domain.
The second path applies a $1\times1$ convolution to learn higher order dynamics.

```
>>> from keras import ops
>>> from kerex.layers import FNO1D
>>> fno_layer = FNO1D(filters=8, modes=8)
>>> fno_layer.build(input_shape=(None, 32, 3))
>>> x = ops.ones((1, 32, 3))
>>> y = fno_layer(x)
>>> y.shape
(1, 32, 8)
```

#### Note
The Keras3 framework does not have a complex data type. Therefore, the implementation of the spectral convolution treats the real- and imaginary parts of the weights and the inputs as two separate tensors. The multiplication of the complex weights with the complex inputs 

$$wx = (w_{\text{real}} + i w_{\text{imag}})(x_{\text{real}} + i x_{\text{imag}})$$

is therefore explicitly performed as

$$y_{\text{real}} = w_{\text{real}}x_{\text{real}} - w_{\text{imag}}x_{\text{imag}}$$

and

$$y_{\text{imag}} = w_{\text{real}}x_{\text{imag}} + w_{\text{imag}}x_{\text{real}}$$

Moreover, the Tensorflow implementation requires a `custom_gradient` function as the automatic differentiation has trouble propagating throught the layer.

### Merge layer
This module implements additional merge layer, that are not implemented in Keras3 by default.

### Wrapper
This module implements wrapper, which can be used to augment any Keras3 layer with additional functionality.


## Blocks
This module implements larger blocks from layers. All blocks subclass `keras.layers.Layer` and are serializable using `model.save()`.

### Attention
...


### Autoencoder
...

### TSMixer
...



## Models

### Autoencoder
...

### Neural Operator
...

### TSMixer
...




