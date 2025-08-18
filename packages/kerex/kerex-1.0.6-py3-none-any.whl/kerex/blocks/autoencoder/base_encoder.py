from keras import layers
from keras import Sequential
from keras import initializers
from keras import regularizers
from keras import constraints
from keras import saving
from ...ops.helper import _IterableVars
from importlib import import_module


class BaseEncoder(layers.Layer, _IterableVars):
    """
    Base class of convolutional encoder block

    Use to subclass 1-D, 2-D, and 3-D Encoder

    Parameters
    ----------
    rank : int {1, 2, 3}
        Rank of `BaseEncoder`. Must be within {1, 2, 3}.
    filters : int | list | tuple
        Number of filters for the convolutional forward sub-model.
    kernel_size : int | list | tuple, optional
        Kernel size for the convolutional forward sub-model.
        Defaults to 5.
    strides : int | list | tuple, optional
        Strides for the convolutional forward sub-model.
        Defaults to 1.
    padding : str, optional
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
        If `None`, `name` is automatically inherited from the class name `"BaseEncoder"`.
        Defaults to `None`.
    **kwargs : Additional keyword arguments for the `keras.layers.Layer` super-class.

    Notes
    -----
    Downsampling is realized using a strided convolution as proposed by [Springenberger et al.](https://arxiv.org/abs/1412.6806)

    """

    def __init__(
            self,
            rank,
            filters,
            kernel_size=5,
            strides=1,
            padding="same",
            data_format="channels_last",
            dilation_rate=1,
            groups=1,
            use_skip_connection=False,
            downsampling_filters=None,
            downsampling_groups=None,
            activation="relu",
            use_bias=True,
            kernel_initializer="he_normal",
            bias_initializer="zeros",
            kernel_regularizer=None,
            bias_regularizer=None,
            kernel_constraint=None,
            bias_constraint=None,
            name=None, 
            **kwargs):
        super().__init__(name=name, **kwargs)

        # set general class variables
        self.rank = rank
        self.padding = padding
        self.data_format = data_format
        self.activation = activation
        self.use_skip_connection = use_skip_connection
        self.use_bias = use_bias
        self.kernel_initializer = kernel_initializer
        self.bias_initializer = bias_initializer
        self.kernel_regularizer = kernel_regularizer
        self.bias_regularizer = bias_regularizer
        self.kernel_constraint = kernel_constraint
        self.bias_constraint = bias_constraint

        # set class variables for the Sequential model
        self.set_vars(filters=filters, kernel_size=kernel_size, strides=strides, dilation_rate=dilation_rate, groups=groups)

        # set class variables that are relevant for downsampling operation
        self.downsampling_filters = downsampling_filters or self.filters[-1]
        self.downsampling_groups = downsampling_groups or self.groups[-1]

        # define layers
        self.forward_conv = Sequential([
            getattr(import_module(name="...layers.conv", package=__package__), f"Conv{self.rank}D")(
                filters=f,
                kernel_size=k,
                strides=s,
                padding=self.padding,
                data_format=self.data_format,
                dilation_rate=d,
                groups=g,
                activation=self.activation,
                use_bias=self.use_bias,
                kernel_initializer=self.kernel_initializer,
                bias_initializer=self.bias_initializer,
                kernel_regularizer=self.kernel_regularizer,
                bias_regularizer=self.bias_regularizer,
                activity_regularizer=self.activity_regularizer,
                kernel_constraint=self.kernel_constraint,
                bias_constraint=self.bias_constraint
            ) for f, k, s, d, g in zip(self.filters, self.kernel_size, self.strides, self.dilation_rate, self.groups)
        ])

        self.downsampling = getattr(import_module(name="...layers.conv", package=__package__), f"Conv{self.rank}D")(
            filters=self.downsampling_filters,
            kernel_size=2,
            strides=2,
            padding="same",
            data_format=self.data_format,
            dilation_rate=1,
            groups=self.downsampling_groups,
            activation=None,
            use_bias=self.use_bias,
            kernel_initializer=self.kernel_initializer,
            bias_initializer=self.bias_initializer,
            kernel_regularizer=self.kernel_regularizer,
            bias_regularizer=self.bias_regularizer,
            activity_regularizer=self.activity_regularizer,
            kernel_constraint=self.kernel_constraint,
            bias_constraint=self.bias_constraint
        )

    def call(self, inputs):
        """
        Call method of `BaseEncoder`

        The `inputs` are first processed by `self.forward_conv`,
        and then bisected along the feature axes by `self.downsampling`.
        If `self.use_skip_connection=True`, the layer additionally returns the output of `self.forward_conv`
        alongside the output of `self.downsampling`.
        
        Parameters
        ----------
        inputs : KerasTensor
            Input tensor.

        Returns
        -------
        outputs | (outputs_forward, outputs_skip) : KerasTensor | (KerasTensor, KerasTensor)
            Output of `self.downsampling` if `self.use_skip_connection=False`.
            If `self.use_skip_connection=True`, the layer additionally returns the intermediate output before the downsampling operation.

        """

        x_skip = self.forward_conv(inputs)
        x_forward = self.downsampling(x_skip)

        if self.use_skip_connection:
            return x_forward, x_skip
        
        return x_forward
    
    def build(self, input_shape):
        """
        Build method of `BaseEncoder`

        Builds all sub-modules and sets `self.built=True`.
        
        Parameters
        ----------
        input_shape : tuple
            Input shape

        """

        if self.built:
            return
        
        super().build(input_shape)

        # build forward layer and update input_shape
        self.forward_conv.build(input_shape=input_shape)
        input_shape = self.forward_conv.compute_output_shape(input_shape=input_shape)

        # build downsampling layer
        self.downsampling.build(input_shape=input_shape)

        # update built state
        self.built = True
    
    def compute_output_shape(self, input_shape):
        """
        Compute output shape of `BaseEncoder`

        Parameters
        ----------
        input_shape : tuple
            Input shape.

        Returns
        -------
        output_shape : tuple
            Output shape.

        """

        output_shape_skip = self.forward_conv.compute_output_shape(input_shape=input_shape)
        output_shape_forward = self.downsampling.compute_output_shape(input_shape=output_shape_skip)

        if self.use_skip_connection:
            return (output_shape_forward, output_shape_skip)
        
        return output_shape_forward

    def get_config(self):
        """
        Necessary for Keras serialization

        Returns
        -------
        config : dict
            Dictionary with the layer configuration.
            
        """

        config: dict = super().get_config()
        config.update({
            "filters": self.filters,
            "kernel_size": self.kernel_size,
            "strides": self.strides,
            "padding": self.padding,
            "data_format": self.data_format,
            "dilation_rate": self.dilation_rate,
            "groups": self.groups,
            "use_skip_connection": self.use_skip_connection,
            "downsampling_filters": self.downsampling_filters,
            "downsampling_groups": self.downsampling_groups,
            "activation": saving.serialize_keras_object(self.activation),
            "use_bias": self.use_bias,
            "kernel_initializer": initializers.serialize(self.kernel_initializer),
            "bias_initializer": initializers.serialize(self.bias_initializer),
            "kernel_regularizer": regularizers.serialize(self.kernel_regularizer),
            "bias_regularizer": regularizers.serialize(self.bias_regularizer),
            "kernel_constraint": constraints.serialize(self.kernel_constraint),
            "bias_constraint": constraints.serialize(self.bias_constraint),
            "downsampling_filters": self.downsampling_filters,
            "downsampling_groups": self.downsampling_groups
        })
        
        return config
    
    @classmethod
    def from_config(cls, config):
        """
        Necessary for Keras deserialization

        Parameters
        ----------
        cls : BaseEncoder
            The `BaseEncoder` class.
        config : dict
            Dictionary with the layer configuration.

        Returns
        -------
        cls : BaseEncoder
            Instance of `BaseEncoder` from `config`.
            
        """

        # get configs of keras objects
        activation_cfg = config.pop("activation")
        kernel_initializer_cfg = config.pop("kernel_initializer")
        bias_initializer_cfg = config.pop("bias_initializer")
        kernel_regularizer_cfg = config.pop("kernel_regularizer")
        bias_regularizer_cfg = config.pop("bias_regularizer")
        kernel_constraint_cfg = config.pop("kernel_constraint")
        bias_constraint_cfg = config.pop("bias_constraint")

        config.update({
            "activation": saving.deserialize_keras_object(activation_cfg),
            "kernel_initializer": initializers.deserialize(kernel_initializer_cfg),
            "bias_initializer": initializers.deserialize(bias_initializer_cfg),
            "kernel_regularizer": regularizers.deserialize(kernel_regularizer_cfg),
            "bias_regularizer": regularizers.deserialize(bias_regularizer_cfg),
            "kernel_constraint": constraints.deserialize(kernel_constraint_cfg),
            "bias_constraint": constraints.deserialize(bias_constraint_cfg)
        })

        return cls(**config)
    