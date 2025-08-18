import tensorflow as tf
from typing import Tuple
from functools import partial


def _get_complex_tensor_from_tuple(x):
    """
    Get a complex tensor from a tuple of two real-valued tensors.

    Parameters
    ----------
    x : tf.Tensor | list | tuple
        Input tensor, either `tf.Tensor` (real part) or tuple/list (real- and imaginary part).
        If only the real part is provided, the imaginary part is assumed 0.

    Returns
    -------
    y : tf.Tensor
        Tensor with `dtype=tf.complex`.

    Raises
    ------
    ValueError
        If shapes of real- and imaginary part to not match.

    """

    if not isinstance(x, (tuple, list)) or len(x) != 2:
        real = x
        imag = tf.zeros_like(x)
    else:
        real, imag = x
    # Check shapes.
    if real.shape != imag.shape:
        raise ValueError(
            "Input `x` should be a tuple of two tensors - real and imaginary."
            "Both the real and imaginary parts should have the same shape. "
            f"Received: x[0].shape = {real.shape}, x[1].shape = {imag.shape}"
        )

    complex_input = tf.complex(real=real, imag=imag)
    return complex_input


# === FFT ===
def _fft(x: tuple, fn: callable) -> Tuple[tf.Tensor, tf.Tensor]:
    complex_input = _get_complex_tensor_from_tuple(x)
    complex_output = fn(complex_input)
    return tf.math.real(complex_output), tf.math.imag(complex_output)


# === real valued FFT ===
def _rfft(x: tf.Tensor, fn: callable) -> Tuple[tf.Tensor, tf.Tensor]:
    complex_output = fn(x)
    return tf.math.real(complex_output), tf.math.imag(complex_output)


def _irfft(x: tf.Tensor, fn: callable, n: tuple = None) -> tf.Tensor:
    complex_input = _get_complex_tensor_from_tuple(x)
    complex_output = fn(complex_input, fft_length=n)
    return tf.math.real(complex_output), tf.math.imag(complex_output)

# === derived functions
def fft_fn(x):
    return partial(_fft, fn=tf.signal.fft)(x)


def fft2_fn(x):
    return partial(_fft, fn=tf.signal.fft2d)(x)


def fft3_fn(x):
    return partial(_fft, fn=tf.signal.fft3d)(x)


def ifft_fn(x):
    return partial(_fft, fn=tf.signal.ifft)(x)


def ifft2_fn(x):
    return partial(_fft, fn=tf.signal.ifft2d)(x)


def ifft3_fn(x):
    return partial(_fft, fn=tf.signal.ifft3d)(x)


def rfft_fn(x):
    return partial(_rfft, fn=tf.signal.rfft)(x)


def rfft2_fn(x):
    return partial(_rfft, fn=tf.signal.rfft2d)(x)


def rfft3_fn(x):
    return partial(_rfft, fn=tf.signal.rfft3d)(x)


def irfft_fn(x, n=None):
    y_real, _ = partial(_irfft, fn=tf.signal.irfft, n=n)(x)
    return y_real


def irfft2_fn(x, n=None):
    y_real, _ = partial(_irfft, fn=tf.signal.irfft2d, n=n)(x)
    return y_real


def irfft3_fn(x, n=None):
    y_real, _ = partial(_irfft, fn=tf.signal.irfft3d, n=n)(x)
    return y_real
