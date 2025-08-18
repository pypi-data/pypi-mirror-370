from .base_encoder import BaseEncoder
from keras import saving


@saving.register_keras_serializable(package="KerasAddon.Blocks.Autoencoder", name="Encoder1D")
class Encoder1D(BaseEncoder):
    """
    1-D convolutional encoder block

    Parameters
    ----------
    filters : int | list | tuple
        Number of filters for the convolutional forward sub-model.
    kernel_size : int | list | tuple, optional
        Kernel size for the convolutional forward sub-model.
        Defaults to 5.
    strides : int | list | tuple, optional
        Strides for the convolutional forward sub-model.
        Defaults to 1.
    padding : str, optional {`"same"`, `"causal"`}
        Padding that is applied to maintain deterministic data shapes.
        Defaults to `"same"`.
    data_format : str, optional {`"channels_first"`, `"channels_last"`}
        Data format for the convolution operations.
        Defaults to `"channels_last"`.
    dilation_rate : int | list | tuple, optional
        Dilation rate for the convolutional forward sub-model.
        Defaults to 1.
    groups : int | list | tuple, optional
        Number of groups rate for the convolutional forward sub-model.
        Defaults to 1.
    downsampling_filters : int, optional
        Number of filters for the downsampling operation.
        If `None`, this parameter is set to the last entry of `filters`.
        Defaults to `None`.
    downsampling_groups : int, optional
        Number of groups for the downsampling operation.
        If `None`, this parameter is set to the last entry of `filters`.
        Defaults to `None`.
    activation : str | keras.activations.Activation | keras.layers.Layer, optional
        Activation for the convolutional forward sub-model.
        Can be either a `str`, a `keras.activations.Activation`, or a `keras.layers.Layer`.
        Defaults to `"relu"`.
    use_skip_connection : bool, optional
        Whether to use skip connections.
        Defaults to `False`.
    use_bias : bool, optional
        Whether to use bias.
        Defaults to `True`.
    kernel_initializer : str | keras.initializers.Initializer, optional
        Kernel initializer.
        Defaults to `"he_normal"`.
    bias_initializer : str | keras.initializers.Initializer, optional
        Bias initializer.
        Defaults to `"zeros"`.
    kernel_regularizer : str | keras.regularizers.Regularizer, optional
        Kernel regularizer.
        Defaults to `None`.
    bias_regularizer : str | keras.regularizers.Regularizer, optional
        Bias regularizer.
        Defaults to `None`.
    kernel_constraint : str | keras.constraints.Constraint, optional
        Kernel constraint.
        Defaults to `None`.
    bias_constraint : str | keras.constraints.Constraint, optional
        Bias constraint.
        Defaults to `None`.
    name : str, optional
        Name of the layer.
        If `None`, `name` is automatically inherited from the class name `"Encoder1D"`.
        Defaults to `None`.
    **kwargs : Additional keyword arguments for the `keras.layers.Layer` super-class.

    """

    def __init__(
            self, 
            filters, 
            kernel_size=5, 
            strides=1, 
            padding="same",
            data_format="channels_last", 
            dilation_rate=1, 
            groups=1, 
            use_skip_connection = False, 
            activation="relu", 
            use_bias=True, 
            kernel_initializer="he_normal", 
            bias_initializer="zeros", 
            kernel_regularizer=None, 
            bias_regularizer=None, 
            kernel_constraint=None, 
            bias_constraint=None, 
            name=None, 
            **kwargs
        ):
        assert padding in ["same", "causal"], f"Allowed padding types for `Encoder1D` are `'same'` and `'causal'`, received {padding}."
        super().__init__(
            rank=1, 
            filters=filters, 
            kernel_size=kernel_size, 
            strides=strides, 
            padding=padding,
            data_format=data_format, 
            dilation_rate=dilation_rate, 
            groups=groups, 
            use_skip_connection=use_skip_connection, 
            activation=activation, 
            use_bias=use_bias, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer, 
            bias_regularizer=bias_regularizer, 
            kernel_constraint=kernel_constraint, 
            bias_constraint=bias_constraint, 
            name=name, 
            **kwargs
        )
    

@saving.register_keras_serializable(package="KerasAddon.Blocks.Autoencoder", name="Encoder2D")
class Encoder2D(BaseEncoder):
    """
    2-D convolutional encoder block

    Parameters
    ----------
    filters : int | list | tuple
        Number of filters for the convolutional forward sub-model.
    kernel_size : int | list | tuple, optional
        Kernel size for the convolutional forward sub-model.
        Defaults to 5.
    strides : int | list | tuple, optional
        Strides for the convolutional forward sub-model.
        Defaults to 1.
    data_format : str, optional {`"channels_first"`, `"channels_last"`}
        Data format for the convolution operations.
        Defaults to `"channels_last"`.
    dilation_rate : int | list | tuple, optional
        Dilation rate for the convolutional forward sub-model.
        Defaults to 1.
    groups : int | list | tuple, optional
        Number of groups rate for the convolutional forward sub-model.
        Defaults to 1.
    downsampling_filters : int, optional
        Number of filters for the downsampling operation.
        If `None`, this parameter is set to the last entry of `filters`.
        Defaults to `None`.
    downsampling_groups : int, optional
        Number of groups for the downsampling operation.
        If `None`, this parameter is set to the last entry of `filters`.
        Defaults to `None`.
    activation : str | keras.activations.Activation | keras.layers.Layer, optional
        Activation for the convolutional forward sub-model.
        Can be either a `str`, a `keras.activations.Activation`, or a `keras.layers.Layer`.
        Defaults to `"relu"`.
    use_skip_connection : bool, optional
        Whether to use skip connections.
        Defaults to `False`.
    use_bias : bool, optional
        Whether to use bias.
        Defaults to `True`.
    kernel_initializer : str | keras.initializers.Initializer, optional
        Kernel initializer.
        Defaults to `"he_normal"`.
    bias_initializer : str | keras.initializers.Initializer, optional
        Bias initializer.
        Defaults to `"zeros"`.
    kernel_regularizer : str | keras.regularizers.Regularizer, optional
        Kernel regularizer.
        Defaults to `None`.
    bias_regularizer : str | keras.regularizers.Regularizer, optional
        Bias regularizer.
        Defaults to `None`.
    kernel_constraint : str | keras.constraints.Constraint, optional
        Kernel constraint.
        Defaults to `None`.
    bias_constraint : str | keras.constraints.Constraint, optional
        Bias constraint.
        Defaults to `None`.
    name : str, optional
        Name of the layer.
        If `None`, `name` is automatically inherited from the class name `"Encoder2D"`.
        Defaults to `None`.
    **kwargs : Additional keyword arguments for the `keras.layers.Layer` super-class.

    """

    def __init__(
            self, 
            filters, 
            kernel_size=5, 
            strides=1, 
            data_format="channels_last", 
            dilation_rate=1, 
            groups=1, 
            use_skip_connection = False, 
            activation="relu", 
            use_bias=True, 
            kernel_initializer="he_normal", 
            bias_initializer="zeros", 
            kernel_regularizer=None, 
            bias_regularizer=None, 
            kernel_constraint=None, 
            bias_constraint=None, 
            name=None, 
            **kwargs
        ):
        super().__init__(
            rank=2, 
            filters=filters, 
            kernel_size=kernel_size, 
            strides=strides, 
            data_format=data_format, 
            dilation_rate=dilation_rate, 
            groups=groups, 
            use_skip_connection=use_skip_connection, 
            activation=activation, 
            use_bias=use_bias, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer, 
            bias_regularizer=bias_regularizer, 
            kernel_constraint=kernel_constraint, 
            bias_constraint=bias_constraint, 
            name=name, 
            **kwargs
        )


@saving.register_keras_serializable(package="KerasAddon.Blocks.Autoencoder", name="Encoder3D")
class Encoder3D(BaseEncoder):
    """
    3-D convolutional encoder block

    Parameters
    ----------
    filters : int | list | tuple
        Number of filters for the convolutional forward sub-model.
    kernel_size : int | list | tuple, optional
        Kernel size for the convolutional forward sub-model.
        Defaults to 5.
    strides : int | list | tuple, optional
        Strides for the convolutional forward sub-model.
        Defaults to 1.
    data_format : str, optional {`"channels_first"`, `"channels_last"`}
        Data format for the convolution operations.
        Defaults to `"channels_last"`.
    dilation_rate : int | list | tuple, optional
        Dilation rate for the convolutional forward sub-model.
        Defaults to 1.
    groups : int | list | tuple, optional
        Number of groups rate for the convolutional forward sub-model.
        Defaults to 1.
    downsampling_filters : int, optional
        Number of filters for the downsampling operation.
        If `None`, this parameter is set to the last entry of `filters`.
        Defaults to `None`.
    downsampling_groups : int, optional
        Number of groups for the downsampling operation.
        If `None`, this parameter is set to the last entry of `filters`.
        Defaults to `None`.
    activation : str | keras.activations.Activation | keras.layers.Layer, optional
        Activation for the convolutional forward sub-model.
        Can be either a `str`, a `keras.activations.Activation`, or a `keras.layers.Layer`.
        Defaults to `"relu"`.
    use_skip_connection : bool, optional
        Whether to use skip connections.
        Defaults to `False`.
    use_bias : bool, optional
        Whether to use bias.
        Defaults to `True`.
    kernel_initializer : str | keras.initializers.Initializer, optional
        Kernel initializer.
        Defaults to `"he_normal"`.
    bias_initializer : str | keras.initializers.Initializer, optional
        Bias initializer.
        Defaults to `"zeros"`.
    kernel_regularizer : str | keras.regularizers.Regularizer, optional
        Kernel regularizer.
        Defaults to `None`.
    bias_regularizer : str | keras.regularizers.Regularizer, optional
        Bias regularizer.
        Defaults to `None`.
    kernel_constraint : str | keras.constraints.Constraint, optional
        Kernel constraint.
        Defaults to `None`.
    bias_constraint : str | keras.constraints.Constraint, optional
        Bias constraint.
        Defaults to `None`.
    name : str, optional
        Name of the layer.
        If `None`, `name` is automatically inherited from the class name `"Encoder3D"`.
        Defaults to `None`.
    **kwargs : Additional keyword arguments for the `keras.layers.Layer` super-class.

    """

    def __init__(
            self, 
            filters, 
            kernel_size=5, 
            strides=1, 
            data_format="channels_last", 
            dilation_rate=1, 
            groups=1, 
            use_skip_connection = False, 
            activation="relu", 
            use_bias=True, 
            kernel_initializer="he_normal", 
            bias_initializer="zeros", 
            kernel_regularizer=None, 
            bias_regularizer=None, 
            kernel_constraint=None, 
            bias_constraint=None, 
            name=None, 
            **kwargs
        ):
        super().__init__(
            rank=3, 
            filters=filters, 
            kernel_size=kernel_size, 
            strides=strides, 
            data_format=data_format, 
            dilation_rate=dilation_rate, 
            groups=groups, 
            use_skip_connection=use_skip_connection, 
            activation=activation, 
            use_bias=use_bias, 
            kernel_initializer=kernel_initializer, 
            bias_initializer=bias_initializer, 
            kernel_regularizer=kernel_regularizer, 
            bias_regularizer=bias_regularizer, 
            kernel_constraint=kernel_constraint, 
            bias_constraint=bias_constraint, 
            name=name, 
            **kwargs
        )
