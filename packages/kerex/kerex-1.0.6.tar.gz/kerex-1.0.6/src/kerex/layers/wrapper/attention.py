from keras import layers
from keras import saving
from keras import ops
from functools import partial
from typing import Tuple
from ...blocks.attention import GlobalSelfAttention


@saving.register_keras_serializable(package="Kerex.Layers.Wrapper", name="SpatialAttention")
class SpatialAttention(layers.Wrapper):
    """
    Applies spatial multi-head attention on the wrapped layer.
    
    Parameters
    ----------
    layer : Layer
        Keras 'layer' to be wrapped
    num_heads : int, optional
        Number of attention heads. Defaults to 4.
    key_dim : int, optional
        Size of key dimension of multi-head attention. Defaults to 64.
    value_dim : int, optional
        Size of value dimension of multi-head attention. Defaults to 64.
    dropout : float, optional
        Dropout propability. Defaults to 0.
    name : str
        Name of the wrapper.
        Is prepended to the name of the wrapped layer.
        Defaults to `"spatial_attention"`.
    **kwargs : Additional keyword arguments for the `Wrapper` super-class.

    Raises
    ------
    ValueError
        If wrapped `layer` is `LSTM` with argument `return_sequences=False`.

    Notes
    -----
    This layer does not add too many weights to the model,
    but is very expensive to run.

    The implementation follows https://arxiv.org/abs/2307.09072

    """

    def __init__(self, layer, num_heads=4, key_dim=64, value_dim=64, dropout=0, name="spatial_attention", **kwargs):
        if issubclass(type(layer), layers.LSTM):
            if not layer.return_sequences:
                raise ValueError(f"LSTM layer has to be initialized with 'return_sequences=True' in order to work with this wrapper!")
        
        name = "_".join([layer.name, name])
        super().__init__(layer=layer, name=name, **kwargs)
        self.num_heads = num_heads
        self.key_dim = key_dim
        self.value_dim = value_dim
        self.dropout = dropout
        try:
            self.data_format = self.layer.data_format
        except AttributeError:
            self.data_format = "channels_last"  # this is valid for dense layer for example! TODO: check if it really is ;-D

        self.channel_axis = -1 if self.data_format == "channels_last" else 1

        self.self_attention = GlobalSelfAttention(
            num_heads=num_heads,
            key_dim=key_dim,
            value_dim=value_dim,
            dropout=dropout
        )

    def get_transpose(self, feature_axes: list, input_shape: tuple) -> Tuple[list]:
        # we have to transpose to 'channels_last' for attention! Target transpose axes = [0, *feature_axes, 1]
        # N: sequence length from features
        # d_model: number of channels
        if self.data_format == "channels_first":
            # construct transpose axes from feature axes. For attention, we need data format [b, N, d_model] where N is the sequence length
            transpose_axes = [0, *feature_axes, 1]  # for example [0, 2, 1]
            inverse_transpose_axes = [0, len(input_shape) - 1, *[fa - 1 for fa in feature_axes]]  # ...has to be [0, 2, 1]
        else:
            transpose_axes = list(range(len(input_shape)))
            inverse_transpose_axes = transpose_axes.copy()

        return transpose_axes, inverse_transpose_axes
    
    def get_reshape(self, feature_axes: list, output_shape: tuple) -> Tuple[int]:
        # now we have to reshape in case len(feature_axis) < 1
        batch_size = output_shape[0]
        feature_shape = [output_shape[a] for a in feature_axes]

        sequence_length = int(ops.prod(feature_shape))
        num_channel = output_shape[self.channel_axis]

        newshape = (batch_size, sequence_length, num_channel)
        inverse_newshape = (batch_size, *feature_shape, num_channel)
        
        return newshape, inverse_newshape

    def build(self, input_shape: tuple):
        """
        Build method of `SpatialAttention`.

        Builds all sub-modules and sets `self.built=True`.

        Parameters
        ----------
        input_shape : tuple
            Shape of the input data.

        """

        super().build(input_shape=input_shape)
        output_shape = self.layer.compute_output_shape(input_shape)
        
        # extract feature axes from input shape
        feature_axes = list(range(len(input_shape)))
        feature_axes.pop(self.channel_axis)  # remove channel dimension, e.g. [1] when channels last or self.channel_axis = -1
        feature_axes.pop(0)  # remove batch dimension  # e.g. [1, 2]

        # get transpose operation
        transpose_axes, inverse_transpose_axes = self.get_transpose(feature_axes=feature_axes, input_shape=input_shape)

        self.transpose = partial(ops.transpose, axes=transpose_axes)
        self.inverse_transpose = partial(ops.transpose, axes=inverse_transpose_axes)

        # get reshape operation
        newshape, inverse_newshape = self.get_reshape(feature_axes=feature_axes, output_shape=output_shape)

        # both newshape and inverse_newshape have (None) as first dimension. For the transpose operation, we change that to (-1)
        self.reshape = partial(ops.reshape, newshape=(-1, *newshape[1:]))
        self.inverse_reshape = partial(ops.reshape, newshape=(-1, *inverse_newshape[1:]))

        # finally, build attention layer
        self.self_attention.build(query_shape=newshape, value_shape=newshape)

    def call(self, inputs):
        """
        Call method of `SpatialAttention`

        Parameters
        ----------
        inputs : KerasTensor
            Input tensor for the wrapped Keras `layer` or `Model`.

        Returns
        -------
        outputs : KerasTensor
            Output tensor of the wrapped Keras `layer` or `Model`.

        """

        x = self.layer(inputs)

        # apply attention to input
        attention_inputs = self.transpose(x)
        attention_inputs = self.reshape(x)
        attention_outputs = self.self_attention(attention_inputs)

        # inverse transform
        attention_outputs = self.inverse_reshape(attention_outputs)
        attention_outputs = self.inverse_transpose(attention_outputs)
        return x + attention_outputs

    def get_config(self):
        """
        Get config method.
        Required for serialization.

        Returns
        -------
        config : dict
            Dictionary with the configuration of `SpatialAttention`.

        """
        
        config: dict = super().get_config()
        config.update({
            "num_heads": self.num_heads,
            "key_dim": self.key_dim,
            "value_dim": self.value_dim,
            "dropout": self.dropout
        })
        return config

    def compute_output_shape(self, input_shape):
        """
        Compute output shape

        Parameters
        ----------
        input_shape : tuple
            Shape of the input.

        Returns
        -------
        output_shape : tuple
            Shape of the output of `SpatialAttention`.

        """

        return self.layer.compute_output_shape(input_shape)
    

@saving.register_keras_serializable(package="Kerex.Layers.Wrapper", name="ChannelAttention")
class ChannelAttention(SpatialAttention):
    """
    Applies channel-wise multi-head attention on the wrapped layer.
    
    Parameters
    ----------
    layer : Layer
        Layer to be wrapped
    num_heads : int, optional
        Number of attention heads. Defaults to 4.
    key_dim : int, optional
        Size of key dimension of multi-head attention. Defaults to 64.
    value_dim : int, optional
        Size of value dimension of multi-head attention. Defaults to 64.
    dropout : float, optional
        Dropout propability. Defaults to 0.
    name : str
        Name of the wrapper.
        Is prepended to the name of the wrapped layer.
        Defaults to `"channel_attention"`.
    **kwargs : Additional keyword arguments for the `Wrapper` super-class.

    Raises
    ------
    ValueError
        If wrapped `layer` is `LSTM` with argument `return_sequences=False`.

    Notes
    -----
    This layer adds a lot of weights to the model,
    but is still more lightweight at runtime than the `SpatialAttention` wrapper.

    The implementation follows https://arxiv.org/pdf/2112.13047

    """

    def __init__(self, layer, num_heads=4, key_dim=64, value_dim=64, dropout=0, name="channel_attention", **kwargs):
        super().__init__(
            layer=layer,
            num_heads=num_heads,
            key_dim=key_dim,
            value_dim=value_dim,
            dropout=dropout,
            name=name,
            **kwargs
        )

    def get_transpose(self, feature_axes: list, input_shape: Tuple) -> Tuple[list]:
        # we have to transpose to 'channels_first' for attention! Target transpose axes = [0, 1, *feature_axes]
        if self.data_format == "channels_last":
            # construct transpose axes from feature axes. For attention, we need data format [b, N, d_model] where N is the sequence length
            # N: number of channels
            # d_model: sequence length from features
            transpose_axes = [0, len(input_shape) - 1, *feature_axes]
            inverse_transpose_axes = [0, *[fa + 1 for fa in feature_axes], 1]
        else:
            transpose_axes = list(range(len(input_shape)))
            inverse_transpose_axes = transpose_axes.copy()

        return transpose_axes, inverse_transpose_axes
    
    def get_reshape(self, feature_axes: list, output_shape: tuple) -> Tuple[int]:
        # now we have to reshape in case len(feature_axis) < 1
        batch_size = output_shape[0]
        feature_shape = [output_shape[a] for a in feature_axes]
        num_channels = int(ops.prod(feature_shape))
        sequence_length = output_shape[self.channel_axis]

        newshape = (batch_size, sequence_length, num_channels)
        newshape_inverse = (batch_size, sequence_length, *feature_shape)

        return newshape, newshape_inverse
