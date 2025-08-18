import inspect
from keras import ops
from keras import layers
from keras import saving
from keras import KerasTensor
from keras.src import backend
import string
from math import pi
import re


def fftfreq(n, d=1, rad=False):
    """
    Return the Discrete Fourier Transform sample frequencies.

    The returned float array `f` contains the frequency bin centers in cycles
    per unit of the sample spacing (with zero at the start).  For instance, if
    the sample spacing is in seconds, then the frequency unit is cycles/second.

    Given a window length `n` and a sample spacing `d`::

      f = [0, 1, ...,   n/2-1,     -n/2, ..., -1] / (d*n)   if n is even
      f = [0, 1, ..., (n-1)/2, -(n-1)/2, ..., -1] / (d*n)   if n is odd

    Parameters
    ----------
    n : int
        Window length.
    d : scalar, optional
        Sample spacing (inverse of the sampling rate). Defaults to `1`.
    rad : bool, optional
        If this is set, the angular frequency `omega=2*pi*f` is returned.
        Defaults to `False`.

    Returns
    -------
    f : KerasTensor
        Tensor of length `n` containing the sample frequencies.

    Examples
    --------
    >>> from keras import ops
    >>> from ssp.keras.ops import fft, fftfreq
    >>> signal = ops.array([-2, 8, 6, 4, 1, 0, 3, 5], dtype=float)
    >>> fourier = fft(signal)
    >>> n = ops.size(signal)
    >>> timestep = 0.1
    >>> freq = fftfreq(n, d=timestep)
    >>> freq
    array([ 0.  ,  1.25,  2.5 , ..., -3.75, -2.5 , -1.25])

    """

    fs = 1.0 / d
    df = fs / ops.cast(n, float)
    fft_freqs = ops.arange(-ops.cast(n // 2, float) * df, ops.cast(n // 2, float) * df, df)

    if rad:
        fft_freqs *= (2 * pi)

    return ops.roll(fft_freqs, shift=n // 2)


def squeeze_or_expand_to_same_rank(x1, x2, axis=-1, expand_rank_1: bool = True) -> tuple:
    """
    Squeeze/expand along `axis` if ranks differ from expected by exactly 1.

    Parameters
    ----------
    x1 : KerasTensor
        first input tensor
    x2 : KerasTensor
        second input tensor
    axis : int, optional
        axis to squeeze or expand along. Defaults to `-1`.
    expand_rank_1: bool, optional
        Defaults to `True`

    Returns
    -------
    x1, x2 : (KerasTensor, KerasTensor)
        Tuple of `(x1, x2)` with the same shape

    """

    x1_rank = len(x1.shape)
    x2_rank = len(x2.shape)
    if x1_rank == x2_rank:
        return x1, x2
    if x1_rank == x2_rank + 1:
        if x1.shape[axis] == 1:
            if x2_rank == 1 and expand_rank_1:
                x2 = ops.expand_dims(x2, axis=axis)
            else:
                x1 = ops.squeeze(x1, axis=axis)
    if x2_rank == x1_rank + 1:
        if x2.shape[axis] == 1:
            if x1_rank == 1 and expand_rank_1:
                x1 = ops.expand_dims(x1, axis=axis)
            else:
                x2 = ops.squeeze(x2, axis=axis)
    return x1, x2


def large_negative_number(dtype):
    """
    Return a Large negative number based on dtype.

    Parameters
    ----------
    dtype : str
        dtype of large negative number to return
    
    Returns
    -------
    c : float
        Large negative number with dtype `dtype` (-1e9 for `dtype="float32"`, -3e4 for `dtype=float16"`).
    
    """
    
    if backend.standardize_dtype(dtype) == "float16":
        return -3e4
    return -1e9


def index_to_einsum_variable(i):
    """Coverts an index to a einsum variable name.

    We simply map indices to lowercase characters, e.g. 0 -> 'a', 1 -> 'b'.

    """

    return string.ascii_lowercase[i]


def unwrap(phase, axis=-1, period=2*pi):
    """
    Unwrap by taking the complement of large deltas with respect to the period.
    Inspired by https://numpy.org/doc/stable/reference/generated/numpy.unwrap.html

    Parameters
    ----------
    phase : KerasTensor
        Input array.
    axis : int, optional
        Axis along which unwrap will operater.
        Defaults to the last axis.
    period : float, optional
        Size of the range over which the input wraps. By default, it is
        `2*pi`.

    Returns
    -------
    out : KerasTensor
        Output array.

    Examples
    --------
    >>> from keras import ops
    >>> from math import pi
    >>> phase = ops.linspace(0, pi, 5) + ops.array([0.0, 0.0, 0.0, pi, pi])
    >>> ops.convert_to_numpy(phase)
    array([0.       , 0.7853982, 1.5707964, 5.4977875, 6.2831855], dtype=float32)
    >>> ops.convert_to_numpy(unwrap(phase))
    array([ 0.      , 0.7853982, 1.5707964, -0.785398, 0.       ], dtype=float32)

    """

    nd = ops.ndim(phase)

    # get phase difference and correction
    phase_diff = ops.diff(phase, axis=axis)
    jumps = ops.cast(phase_diff < -period / 2, dtype="int8") - ops.cast(phase_diff > period / 2, dtype="int8")
    correction = ops.cumsum(ops.cast(jumps, dtype="float32") * period, axis=axis)

    # pad to original size
    pad_width = [(0, 0)] * nd
    pad_width[axis] = (1, 0)

    correction = ops.pad(correction, pad_width=tuple(pad_width))
    return phase + correction


def capitalize_first_char(s):
    """
    Capitalize first character of string and leave the rest.
    

    Parameters
    ----------
    s : str
        A string to process.

    Returns
    -------
    s : str
        A modified string where the initial character is capitalized and the rest remains original.

    Notes
    -----
    Beneficial to import layers, e.g., "Conv2D".capitalize() results in "Conv2d", which is no valid layer!
    Source: https://stackoverflow.com/questions/12410242/python-capitalize-first-letter-only
    
    """

    return re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), s, 1)


@saving.register_keras_serializable(package="KerasAddon.Helper", name="get_layer")
def get_layer(identifier, module="keras.layers", registered_name=None, **layer_kwargs):
    """
    Get a layer from an identifier

    Parameters
    ----------
    identifier : dict | str | Layer
        The identifier for a layer to return.
    module : str, optional
        The module to load the layer from.
        When loading official Keras layer, this should be `"keras.layers"`.
        When using a custom package, this should be the path to this package, e.g., `"keras_addon.layers"`.
        Defauts to `"keras.layers"`.
    registered_name : str, optional
        Only necessary if loading inofficial keras layers. Defaults to `None`.

    Returns
    -------
    layer : Layer
        An instance of a keras.Layer class from the identifier.

    """

    if identifier is None:
        return None
    if isinstance(identifier, dict):
        obj = layers.deserialize(identifier)
    elif isinstance(identifier, str):
        config = {
            "module": module,
            "class_name": str(capitalize_first_char(identifier)),  # layer names are all capital!
            "config": {
                "name": None,
                "trainable": True,
                "dtype": {
                    "module": "keras",
                    "class_name": "DTypePolicy",
                    "config": {"name": "float32"},
                    "registered_name": None
                },
                **layer_kwargs
            },
            "registered_name": registered_name
        }
        obj = layers.deserialize(config)
    else:
        obj = identifier

    if callable(obj):
        if inspect.isclass(obj):
            obj = obj()
        return obj
    else:
        raise ValueError(
            f"Could not interpret layer identifier: {identifier}"
        )


class _IterableVars:
    """
    This class just provides basic functionality for convolutional blocks

    **Use for inheritance only!**

    This class provides a function to set the class variables as iterables based on the the first keyword argument.

    """

    def set_vars(self, **kwargs):
        """
        Wrap all `**kwargs` to list and set as class attribute

        The first keyword argument has a special role here, as it determines the depth of the network.
        All other parameters (if given as a list or tuple initially) have to comply with the length of this keyword argument.

        Parameters
        ----------
        **kwargs : Keyword arguments.

        Raises
        ------
        ValueError
            If an argument is a list/tuple and contains other dtypes than `int`, `float`, `str`, `bool` or `tuple`.
        ValueError
            If an argument is a list/tuple and contains tuples that do not match `self.rank`.
            This error is only raised when a model has a class attribute `self.rank`.
        ValueError
            If an argument does not match the length of the reference key.
        
        """

        if not kwargs:
            return

        # get the reference key, which has to be the first keyword
        ref_key = list(kwargs.keys())[0]  # e.g., `filters`

        # now iterate over kwargs
        for k, arg in kwargs.items():
            if isinstance(arg, (list, tuple)):
                if len(arg) == 1:
                    # unpack list/tuple of length 1
                    arg, = arg

            if isinstance(arg, (int, float, str, bool, tuple)) or (arg is None):
                if hasattr(self, ref_key):
                    # wrap singular argument (that is not `filters` in list)
                    arg = [arg] * len(getattr(self, ref_key))
                else:
                    # wrap `ref_key` argument in list if it is not a tuple (iterable) already
                    if not isinstance(arg, tuple):
                        arg = [arg]
            
            # wrap arguments that come as nested list (happens after deserialization!) to a list of tuples
            arg = [tuple(f) if isinstance(f, list) else f for f in arg]

            if not all(isinstance(f, (int, float, str, bool, tuple)) or (f is None) for f in arg):
                raise ValueError(f"Received bad `{k}` argument ({arg}). Expected all entries of `{k}` to be either `int`, `str`, `bool`, or `tuple`.")
            
            if hasattr(self, ref_key):
                if hasattr(self, "rank"):
                    if not all(len(f) == self.rank for f in arg if isinstance(f, tuple)):
                        raise ValueError(f"Rank of provided `{ref_key}` does not match rank of the block or model, expected `{k}` of rank {self.rank}.")
            
            try:
                if not len(arg) == len(getattr(self, ref_key)):
                    raise ValueError(f"Too many arguments for `{k}`, expected {len(getattr(self, ref_key))}, received {len(arg)}.")
            except AttributeError:
                # `ref_key` was not set yet, no comparison possible
                pass
            
            # set `v` as class attribute `k`
            setattr(self, k, arg)
