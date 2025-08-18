from keras import saving
from keras import layers
from keras import Sequential
from keras import ops
from keras.src.layers.convolutional.base_conv import BaseConv
from keras.src.layers.convolutional.base_separable_conv import BaseSeparableConv
from keras.src.layers.convolutional.base_conv_transpose import BaseConvTranspose
from keras.src import activations
from ...ops import get_layer


@saving.register_keras_serializable(package="Kerex.Layers", name="ChannelAttentionModule")
class ChannelAttentionModule(layers.Layer):
    """
    Convolutional Channel Attention Module (CAM)

    Parameters
    ----------
    rank : int, optional
        Rank of the convolutions.
        Defaults to 2.
    reduction_ratio : int, optional
        Size of the bottleneck of the shared MLP in relation to the input size.
        Defaults to 8.
    activation : str, optional
        Activation function for the shared MLP.
        Defaults to `"sigmoid"`.
    data_format : str, optional {`"channels_first"`, `"channels_last"`}
        Data format of the convolutions.
        Can be either `"channels_first"` or `"channels_last"`.
        Defaults to `"channels_last"`.
    name : str, optional
        Name of the layer.
        Defaults to `"channel_attention_module"`.
    **kwargs : Additional keyword arguments for the `Layer` super-class.

    Notes
    -----
    This is not a wrapper but a CAM layer.
    May be used on it's own, but here it serves as a building block for the 
    [Convolutional Block Attention Module (CBAM)](https://arxiv.org/abs/1807.06521).
    
    More information on the CAM can be found here: https://www.digitalocean.com/community/tutorials/attention-mechanisms-in-computer-vision-cbam#channel-attention-module-cam
    
    """

    def __init__(self, rank=2, reduction_ratio=8, activation="sigmoid", data_format="channels_last", name="channel_attention_module", **kwargs):
        super().__init__(name=name, **kwargs)
        self.rank = rank
        self.reduction_ratio = reduction_ratio
        self.activation = activation
        self.data_format = data_format
        self.channel_axis = -1 if self.data_format == "channels_last" else 1

        self.avg_pooling = get_layer(f"GlobalAveragePooling{self.rank}D", data_format=self.data_format, keepdims=True)
        self.max_pooling = get_layer(f"GlobalMaxPooling{self.rank}D", data_format=self.data_format, keepdims=True)
        self.activation_fn = activations.get(self.activation)

    def build(self, input_shape):
        """
        Build method of `ChannelAttentionModule`
        
        Builds all sub-modules and sets `self.built=True`.

        Parameters
        ----------
        input_shape : tuple
            Shape of the input.

        """

        if self.built:
            return

        # define mlp
        input_shape = list(input_shape)
        num_ch = input_shape[self.channel_axis]
        self.mlp = Sequential([
            layers.Dense(units=num_ch // self.reduction_ratio, activation="relu"),
            layers.Dense(units=num_ch)
        ])

        # get input shape for mlp
        feature_axes = list(range(len(input_shape)))
        feature_axes.pop(self.channel_axis)  # remove channel axis
        feature_axes.pop(0)  # remove batch dimension

        # overwrite feature axes with 1
        for a in feature_axes:
            input_shape[a] = 1

        input_shape[self.channel_axis] = 2 * num_ch

        self.mlp.build(input_shape=tuple(input_shape))

        self.built = True

    def call(self, inputs):
        """
        Call method of `ChannelAttentionModule`

        Parameters
        ----------
        inputs : KerasTensor
            Input tensor for `ChannelAttentionModule`.

        Returns
        -------
        outputs : KerasTensor
            Refined features.

        """

        max_pool = self.max_pooling(inputs)  # shape (batch, 1, 1, ch)
        avg_pool = self.avg_pooling(inputs)  # shape (batch, 1, 1, ch)

        # concatenate
        x = ops.concatenate([max_pool, avg_pool], axis=self.channel_axis)  # shape = (batch, 1, 1, 2*ch)

        # apply mlp
        x = self.mlp(x)
        x = self.activation_fn(x)

        return x
    
    def compute_output_shape(self, input_shape: tuple) -> tuple:
        """
        Compute output shape

        Parameters
        ----------
        input_shape : tuple
            Shape of the input.

        Returns
        -------
        output_shape : tuple
            Shape of the output of `ChannelAttentionModule`.

        """

        output_shape = [1] * len(input_shape)
        output_shape[0] = input_shape[0]
        output_shape[self.channel_axis] = input_shape[self.channel_axis]

        return tuple(output_shape)

    def get_config(self):
        """
        Get config method.
        Required for serialization.

        Returns
        -------
        config : dict
            Dictionary with the configuration of `ChannelAttentionModule`

        """
        
        config: dict = super().get_config()
        config.update({
            "rank": self.rank,
            "reduction_ratio": self.reduction_ratio,
            "activation": self.activation,
            "data_format": self.data_format
        })
        return config


@saving.register_keras_serializable(package="Kerex.Layers", name="SpatialAttentionModule")
class SpatialAttentionModule(layers.Layer):
    """
    Spatial Attention Module (SAM)

    Parameters
    ----------
    rank : int, optional
        Rank of the convolutions.
        Defaults to 2.
    kernel_size : int | tuple, optional
        An integer or a tuple/list of integers indicating the kernel size of the convolutional projection layer.
        Defaults to 5.
    activation : str, optional
        Activation function for the convolutional layer.
        Defaults to `"sigmoid"`.
    data_format : str, optional {`"channels_first"`, `"channels_last"`}
        Data format of the convolutions.
        Can be either `"channels_first"` or `"channels_last"`.
        Defaults to `"channels_last"`.
    name : str, optional
        Name of the layer. Defaults to `"spatial_attention_module"`.
    **kwargs : Additional keyword arguments for the `Layer` super-class.

    Notes
    -----
    This is not a wrapper but a CAM layer.
    May be used on it's own, but here it serves as a building block for the 
    [Convolutional Block Attention Module (CBAM)](https://arxiv.org/abs/1807.06521).
    
    More information on the SAM can be found here: https://www.digitalocean.com/community/tutorials/attention-mechanisms-in-computer-vision-cbam#channel-attention-module-cam
    
    """

    def __init__(self, rank=2, kernel_size=5, activation="sigmoid", data_format="channels_last", name="spatial_attention_module", **kwargs):
        super().__init__(name=name, **kwargs)
        self.rank = rank
        self.kernel_size = kernel_size
        self.activation = activation
        self.data_format = data_format
        self.channel_axis = -1 if self.data_format == "channels_last" else 1

        self.projection = get_layer(f"Conv{self.rank}D", filters=1, kernel_size=self.kernel_size, padding="same", data_format=self.data_format)
        self.activation_fn = activations.get(self.activation)
    
    def build(self, input_shape):
        """
        Build method of `SpatialAttentionModule`
        
        Builds all sub-modules and sets `self.built=True`.

        Parameters
        ----------
        input_shape : tuple
            Shape of the input.

        """

        if self.built:
            return
        
        input_shape_projection = list(input_shape)

        input_shape_projection[self.channel_axis] = 2

        self.projection.build(input_shape=tuple(input_shape_projection))
        
        self.built = True

    def call(self, inputs):
        """
        Call method of `SpatialAttentionModule`

        Parameters
        ----------
        inputs : KerasTensor
            Input tensor for `SpatialAttentionModule`.

        Returns
        -------
        outputs : KerasTensor
            Refined features.

        """

        channel_avg = ops.average(inputs, axis=self.channel_axis)
        channel_max = ops.max(inputs, axis=self.channel_axis)
        x = ops.stack([channel_avg, channel_max], axis=self.channel_axis)  # shape (batch, h, w, 2)
        x = self.projection(x)  # shape (batch, h, w, 1)
        x = self.activation_fn(x)  # shape (batch, h, w, 1)

        return x  # shape (batch, h, w, 1)
    
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
            Shape of the output of `SpatialAttentionModule`.

        """
        
        output_shape = list(input_shape)
        output_shape[self.channel_axis] = 1
        
        return tuple(output_shape)
    
    def get_config(self):
        """
        Get config method.
        Required for serialization.

        Returns
        -------
        config : dict
            Dictionary with the configuration of `SpatialAttentionModule`

        """
        
        config: dict = super().get_config()
        config.update({
            "rank": self.rank,
            "kernel_size": self.kernel_size,
            "activation": self.activation,
            "data_format": self.data_format
        })
        return config


@saving.register_keras_serializable(package="Kerex.Layers.Wrapper", name="CBAM")
class CBAM(layers.Wrapper):
    """
    Convolutional Block Attention Module Wrapper

    Can be used to wrap any convolutional Keras layer.
    The layer refines the latent space variable / features by sequentially applying
    - channel attention from ChannelAttentionModule, followed by
    - spatial attention from SpatialAttentionModule.

    Parameters
    ----------
    layer : Layer
        Keras `layer` or `Sequential` model to be wrapped.
        If this is a `Sequential` model, all layers have to be convolutional.
    reduction_ratio : int, optional
        Size of the bottleneck in relation to the input size of the shared MLP in `ChannelAttentionModule`.
        Defaults to 8.
    kernel_size : int | tuple, optional
        An integer or a tuple/list of integers indicating the kernel size of the convolutional projection layer.
        This is parameter for the `SpatialAttentionModule`.
        Defaults to 5.
    channel_activation : str, optional
        Activation in `ChannelAttentionModule`.
        Defaults to `"sigmoid"`.
    spatial_activation : str, optional
        Activation in `SpatialAttentionModule`.
        Defaults to `"sigmoid"`.
    name : str, optional
        Name of the wrapper, that is prepended to the name of the wrapped layer.
        Defaults to `"cbam"`.
    **kwargs : Additional keyword arguments for the `Wrapper` super-class.

    Raises
    ------
    ValueError
        If `layer` is not a Convolutional layer.

    Examples
    --------
    >>> from keras import layers, ops
    >>> x = ops.ones((2, 32, 32, 3))
    >>> conv_layer = layers.Conv2D(filters=8, kernel_size=3)
    >>> cbam_conv_layer = CBAM(conv_layer)
    >>> layer_output = conv_layer(x)
    >>> cbam_output = cbam_conv_layer(x)
    >>> layer_output.shape == cbam_output.shape
    True
    >>> ops.convert_to_numpy(ops.equal(cbam_output, layer_output)).any()
    np.False_

    """

    def __init__(self, layer, reduction_ratio=8, kernel_size=5, channel_activation="sigmoid", spatial_activation="sigmoid", name="cbam", **kwargs):
        if issubclass(type(layer), Sequential):
            if not all([isinstance(type(l), (BaseConv, BaseConvTranspose, BaseSeparableConv)) for l in layer.layers]):
                raise ValueError(f"CBAM is only compatible with convolutional layers, received a Sequential model with {[l.__class__ for l in layer.layers]} layers")
        elif issubclass(type(layer), (BaseConv, BaseConvTranspose, BaseSeparableConv)):
            pass
        else:
            raise ValueError(f"CBAM is only compatible with convolutional layers, received {layer.__class__}")
        
        name = "_".join([layer.name, name])
        super().__init__(layer=layer, name=name, **kwargs)
        self.reduction_ratio = reduction_ratio
        self.kernel_size = kernel_size
        self.channel_activation = channel_activation
        self.spatial_activation = spatial_activation

        self.channel_attention = ChannelAttentionModule(
            rank=self.layer.rank,
            reduction_ratio=self.reduction_ratio,
            activation=self.channel_activation,
            data_format=self.layer.data_format
        )
        self.spatial_attention = SpatialAttentionModule(
            rank=self.layer.rank,
            kernel_size=self.kernel_size,
            activation=self.spatial_activation,
            data_format=self.layer.data_format
        )

    def build(self, input_shape):
        """
        Build method of `CBAM`
        
        Builds all sub-modules and sets `self.built=True`.

        Parameters
        ----------
        input_shape : tuple
            Shape of the input.

        """

        super().build(input_shape=input_shape)
        output_shape = self.layer.compute_output_shape(input_shape=input_shape)
        self.channel_attention.build(input_shape=output_shape)
        self.spatial_attention.build(input_shape=output_shape)

    def call(self, inputs):
        """
        Call method of `CBAM`.
        This layer applies (1) channel-wise and (2) spatial attention to refine the features.

        Parameters
        ----------
        inputs : KerasTensor
            Input tensor for `CBAM`.

        Returns
        -------
        outputs : KerasTensor
            Refined features.

        """

        x = self.layer(inputs)

        # apply attention sequentially
        x = ops.multiply(x, self.channel_attention(x))
        x = ops.multiply(x, self.spatial_attention(x))
        return x
    
    def get_config(self):
        """
        Get config method.
        Required for serialization.

        Returns
        -------
        config : dict
            Dictionary with the configuration of `CBAM`.

        """

        config: dict = super().get_config()
        config.update({
            "reduction_ratio": self.reduction_ratio,
            "kernel_size": self.kernel_size,
            "channel_activation": self.channel_activation,
            "spatial_activation": self.spatial_activation
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
            Shape of the output of `CBAM`.

        Notes
        -----
        `CBAM` does not modify the output shape.
        Hence, this layer simply calls the `compute_output_shape` method of the wrapped layer.

        """

        return self.layer.compute_output_shape(input_shape)
    