import jax
import jax.numpy as jnp
from typing import Tuple
from functools import partial


def _get_complex_tensor_from_tuple(x) -> jax.lax.complex:
    """
    Get a complex tensor from a tuple of two real-valued tensors.

    Parameters
    ----------
    x : jax.lax.real | list | tuple
        Input tensor, either `jax.lax.real` (real part) or tuple/list (real- and imaginary part).
        If only the real part is provided, the imaginary part is assumed 0.

    Returns
    -------
    y : jax.lax.complex
        Tensor with `dtype=jax.lax.complex`.

    Raises
    ------
    ValueError
        If shapes of real- and imaginary part to not match.
    ValueError
        If at least on of the inputs is not of type float.

    """

    if not isinstance(x, (tuple, list)) or len(x) != 2:
        real = x
        imag = jnp.zeros_like(x)
    else:
        real, imag = x
    # Check shapes.
    if real.shape != imag.shape:
        raise ValueError(
            "Input `x` should be a tuple of two tensors - real and imaginary."
            "Both the real and imaginary parts should have the same shape. "
            f"Received: x[0].shape = {real.shape}, x[1].shape = {imag.shape}"
        )
    # Ensure dtype is float.
    if not jnp.issubdtype(real.dtype, jnp.floating) or not jnp.issubdtype(
        imag.dtype, jnp.floating
    ):
        raise ValueError(
            "At least one tensor in input `x` is not of type float."
            f"Received: x={x}."
        )
    
    complex_input = jax.lax.complex(real, imag)
    return complex_input


# === FFT ===
def _fft(x: tuple, fn: callable, **kwargs) -> Tuple[jnp.ndarray, jnp.ndarray]:
    complex_input = _get_complex_tensor_from_tuple(x)
    complex_output = fn(complex_input, **kwargs)
    return jnp.real(complex_output), jnp.imag(complex_output)


# === real valued FFT ===
def _rfft(x: jnp.ndarray, fn: callable, **kwargs) -> Tuple[jnp.ndarray, jnp.ndarray]:
    complex_output = fn(x, **kwargs)
    return jnp.real(complex_output), jnp.imag(complex_output)


def _irfft(x: jnp.ndarray, fn: callable, **kwargs) -> jnp.ndarray:
    complex_input = _get_complex_tensor_from_tuple(x)
    complex_output = fn(complex_input, **kwargs)
    return jnp.real(complex_output), jnp.imag(complex_output)


# === derived functions
def fft_fn(x):
    return partial(_fft, fn=jnp.fft.fft)(x)


def fft2_fn(x):
    return partial(_fft, fn=jnp.fft.fft2)(x)


def fft3_fn(x):
    return partial(_fft, fn=jnp.fft.fftn, axes=(-3, -2, -1))(x)


def ifft_fn(x):
    return partial(_fft, fn=jnp.fft.ifft)(x)


def ifft2_fn(x):
    return partial(_fft, fn=jnp.fft.ifft2)(x)


def ifft3_fn(x):
    return partial(_fft, fn=jnp.fft.ifftn, axes=(-3, -2, -1))(x)


def rfft_fn(x):
    return partial(_rfft, fn=jnp.fft.rfft)(x)


def rfft2_fn(x):
    return partial(_rfft, fn=jnp.fft.rfft2)(x)


def rfft3_fn(x):
    return partial(_rfft, fn=jnp.fft.rfftn, axes=(-3, -2, -1))(x)


def irfft_fn(x, n=None):
    if isinstance(n, tuple):
        n, = n  # unpack tuple
    y_real, _ = partial(_irfft, fn=jnp.fft.irfft, n=n)(x)
    return y_real


def irfft2_fn(x, n=None):
    y_real, _ = partial(_irfft, fn=jnp.fft.irfft2, s=n)(x)
    return y_real


def irfft3_fn(x, n=None):
    y_real, _ = partial(_irfft, fn=jnp.fft.irfftn, s=n, axes=(-3, -2, -1))(x)
    return y_real
