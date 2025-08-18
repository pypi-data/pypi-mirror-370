from keras import layers
from keras import Sequential
from keras import initializers
from keras import regularizers
from keras import constraints
from keras import saving
from keras.src.layers.merging.base_merge import Merge
from ...ops.helper import _IterableVars
from ...ops import get_layer
from importlib import import_module


class BaseDecoder(layers.Layer, _IterableVars):
    """
    Base class of convolutional decoder block

    Use to subclass 1-D, 2-D, and 3-D Decoder

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
    upsampling_filters : int, optional
        Number of filters for the upsampling operation.
        If `None`, this parameter is set to the last entry of `filters`.
        Defaults to `None`.
    activation : str | keras.activations.Activation | keras.layers.Layer, optional
        Activation for the convolutional forward sub-model.
        Can be either a `str`, a `keras.activations.Activation`, or a `keras.layers.Layer`.
        Defaults to `"relu"`.
    merge_layer : str | keras.layers.Layer, optional {`"concatenate"`, `"average"`, `"maximum"`, `"minimum"`, `"add"`, `"subtract"`, `"multiply"`, `"dot"`}
        Layer to merge the forward information with the (optional) information from the second input.
        Defaults to `"concatenate"`.
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
        If `None`, `name` is automatically inherited from the class name `"BaseDecoder"`.
        Defaults to `None`.
    **kwargs : Additional keyword arguments for the `keras.layers.Layer` super-class.

    Raises
    ------
    TypeError
        If `merge_layer` is not valid Keras merge layer, cf. https://keras.io/api/layers/merging_layers/
        
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
            upsampling_filters=None,
            activation="relu",
            use_bias=True,
            merge_layer="concatenate",
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
        self.use_bias = use_bias
        self.kernel_initializer = kernel_initializer
        self.bias_initializer = bias_initializer
        self.kernel_regularizer = kernel_regularizer
        self.bias_regularizer = bias_regularizer
        self.kernel_constraint = kernel_constraint
        self.bias_constraint = bias_constraint

        # set class variables for the Sequential model
        self.set_vars(filters=filters, kernel_size=kernel_size, strides=strides, dilation_rate=dilation_rate, groups=groups)        

        # set class variables that are relevant for upsampling operation
        self.upsampling_filters = upsampling_filters or self.filters[-1]

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

        self.upsampling = getattr(import_module(name="...layers.conv", package=__package__), f"Conv{self.rank}DTranspose")(
            filters=self.upsampling_filters,
            kernel_size=2,
            strides=2,
            padding="same",
            data_format=self.data_format,
            dilation_rate=1,
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

        # load merge layer
        try:
            self.merge_layer = get_layer(merge_layer, axis=-1 if self.data_format == "channels_last" else 1)
        except TypeError:  # layer does not supply axis argument
            self.merge_layer = get_layer(merge_layer)

        if not issubclass(type(self.merge_layer), Merge):
            raise TypeError(
                f"Merge-layer {self.merge_layer} supplied to Wrapper isn't "
                "a supported merge-layer."
            )
        
    def call(self, inputs, skip=None):
        """
        Call method of `BaseDecoder`

        The `inputs` are first processed by `self.forward_conv`,
        and then upsampled by factor of 2 along the feature axes by `self.upsampling`.
        If an additional input `skip` is provided, 
        the upsampled Tensor is merged with the `skip` Tensor using `self.merge_layer`.
        
        Parameters
        ----------
        inputs : KerasTensor
            Input tensor.
        skip : KerasTensor, optional
            Additional Tensor that is merged with the forward Tensor
            Defaults to `None`.

        Returns
        -------
        outputs : KerasTensor
            Output tensor.
            
        """

        x_forward = self.upsampling(inputs)

        if skip is not None:
            x_forward = self.merge_layer((x_forward, skip))

        x_forward = self.forward_conv(x_forward)

        return x_forward
    
    def build(self, input_shape, input_shape_skip=None):
        """
        Build method of `BaseDecoder`

        Builds all sub-modules and sets `self.built=True`.
        
        Parameters
        ----------
        input_shape : tuple
            Input shape
        input_shape_skip : tuple, optional
            Input shape of additional information from skip connection.
            Defaults to `None`.

        """

        if self.built:
            return
        
        # cache input shapes
        # self._build_shapes_dict = {"input_shape": input_shape, "input_shape_skip": input_shape_skip}
        self._build_shapes = {}

        super().build(input_shape)

        # build upsampling layer
        # cache build shape
        self._build_shapes.update({self.upsampling.name: {"input_shape": input_shape}})

        self.upsampling.build(input_shape=input_shape)
        input_shape = self.upsampling.compute_output_shape(input_shape=input_shape)

        # build merge layer
        if input_shape_skip is not None:
            # cache build shape
            self._build_shapes.update({self.merge_layer.name: {"input_shape": (input_shape, input_shape_skip)}})

            self.merge_layer.build(input_shape=(input_shape, input_shape_skip))
            input_shape = self.merge_layer.compute_output_shape(input_shape=(input_shape, input_shape_skip))

        # build forward layer and update input_shape
        # cache build shape
        self._build_shapes.update({self.forward_conv.name: {"input_shape": input_shape}})

        self.forward_conv.build(input_shape=input_shape)

        # update built state
        self.built = True
    
    def compute_output_shape(self, input_shape, input_shape_skip=None):
        """
        Compute output shape of `BaseDecoder`

        Parameters
        ----------
        input_shape : tuple
            Input shape
        input_shape_skip : tuple, optional
            Input shape of additional information from skip connection.
            Defaults to `None`.

        Returns
        -------
        output_shape : tuple
            Output shape.
            
        """

        input_shape = self.upsampling.compute_output_shape(input_shape=input_shape)
        if input_shape_skip is not None:
            input_shape = self.merge_layer.compute_output_shape(input_shape=(input_shape, input_shape_skip))

        output_shape = self.forward_conv.compute_output_shape(input_shape=input_shape)
        
        return output_shape

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
            "merge_layer": saving.serialize_keras_object(self.merge_layer),
            "upsampling_filters": self.upsampling_filters,
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
        cls : BaseDecoder
            The `BaseDecoder` class.
        config : dict
            Dictionary with the layer configuration.

        Returns
        -------
        cls : BaseDecoder
            Instance of `BaseDecoder` from `config`.
        """

        # get configs of keras objects
        merge_layer_cfg = config.pop("merge_layer")
        activation_cfg = config.pop("activation")
        kernel_initializer_cfg = config.pop("kernel_initializer")
        bias_initializer_cfg = config.pop("bias_initializer")
        kernel_regularizer_cfg = config.pop("kernel_regularizer")
        bias_regularizer_cfg = config.pop("bias_regularizer")
        kernel_constraint_cfg = config.pop("kernel_constraint")
        bias_constraint_cfg = config.pop("bias_constraint")

        config.update({
            "merge_layer": saving.deserialize_keras_object(merge_layer_cfg),
            "activation": saving.deserialize_keras_object(activation_cfg),
            "kernel_initializer": initializers.deserialize(kernel_initializer_cfg),
            "bias_initializer": initializers.deserialize(bias_initializer_cfg),
            "kernel_regularizer": regularizers.deserialize(kernel_regularizer_cfg),
            "bias_regularizer": regularizers.deserialize(bias_regularizer_cfg),
            "kernel_constraint": constraints.deserialize(kernel_constraint_cfg),
            "bias_constraint": constraints.deserialize(bias_constraint_cfg)
        })

        return cls(**config)
