from functools import partial
from tensorflow.python.framework import ops
from tensorflow.python.ops import random_ops
from tensorflow.python.ops.image_ops_impl import _AssertAtLeast3DImage
import tensorflow as tf


""" RANDOM NOISE WITH SNR DATA AUGMENTATION """
def _get_signal_power(image: tf.Tensor, axis: int | tuple) -> tf.Tensor:
    return tf.reduce_sum(abs(image**2), axis=axis, keepdims=True)


def _get_noise(image: tf.Tensor, snr: int | float, axis: int | tuple) -> tf.Tensor:
    noise_power = _get_signal_power(image=image, axis=axis) / (10**(snr / 10))
    noise = tf.random.normal(tf.shape(image))

    return noise / tf.sqrt(_get_signal_power(noise, axis=axis)) * tf.sqrt(noise_power)


def _random_noise(image: tf.Tensor, random_func: callable, scope_name: str):
    with ops.name_scope(None, scope_name, [image]) as scope:
        image = ops.convert_to_tensor(image, name='image')
        image = _AssertAtLeast3DImage(image)
        shape = image.get_shape()

        if shape.ndims == 3:
            # we have unbatched data (t, x, y) without channels.
            # use the same SNR for all data
            axis = (1, 2)
            snr = random_func(shape=[1, ])
        
        elif (shape.ndims == 4) or (shape.ndims == 5):
            # we have batched data (b, t, x, y) with or without channels.
            # get an individual SNR for each sample
            axis=(2, 3)
            snr = random_func(shape=[shape[0], ])
        else:
            raise ValueError(f"Image shape must be either 3 (unbatched) or 4 (batched) dimensions.")
        
        noise = _get_noise(image=image, snr=snr, axis=axis)
        return image + noise


def random_noise(image, snr, seed=None):
    """
    Apply additive white Gaussian noise (AWGN) with SNR randomly sampled from `snr`.
    Can be savely used within `tf.data.Dataset.map()`.

    Parameters
    ----------
    image : tf.Tensor
        image or 2-D tensor to rotate
    snr : int | tuple | list
        (min_snr, max_snr) SNR value in dB for random noise. A single value results in `snr=(1, snr)`.
    seed : int
        Random seed, defaults to `None`.

    Returns
    -------
    image : tf.Tensor
        `image` with AWGN with SNR randomly sampled from (`min_snr`, `max_snr`).

    Raises
    ------
    ValueError
        If more than 2 values for `snr` are provided.
    ValueError
        If unsupported type for `snr` is provided.

    """

    if snr is None:
        return image
    
    if isinstance(snr, (int, float)):
        # we do not want a minimum value of SNR=0, since it will be ONLY noise!
        # best is to provide 2 values...
        minval = min(1, snr)
        maxval = max(1, snr)
    elif isinstance(snr, (list, tuple)):
        if len(snr) > 2:
            raise ValueError(f"Too many values for SNR, received snr={snr}, expected 2 values.")
        if len(snr) == 2:
            minval = min(snr)
            maxval = max(snr)
        else:
            minval = min(1, *snr)
            maxval = max(1, *snr)
    else:
        raise ValueError(f"Unsupported type for snr {type(snr)}.")
    
    random_func = partial(random_ops.random_uniform, minval=minval, maxval=maxval, seed=seed)
    return _random_noise(image=image, random_func=random_func, scope_name="random_noise")