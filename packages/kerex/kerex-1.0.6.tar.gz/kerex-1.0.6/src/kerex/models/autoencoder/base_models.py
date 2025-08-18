from keras import models
from keras import regularizers, initializers, constraints
from keras import saving
from ...ops.helper import _IterableVars
from importlib import import_module


class BaseFCN(models.Model, _IterableVars):
    """
    Base class of FullyConvolutionalNetwork (FCN)

    Convolutional autoencoder *without* skip-connections

    Parameters
    ----------
    rank : int {1, 2, 3}
        Rank of `BaseFCN`. Must be within {1, 2, 3}.
    filters : int | list | tuple
        Number of filters. 
        The model will be build symmetrically, meaning that only the number of encoder filters is defined,
        and the decoder will mirror it.
    kernel_size : int | list | tuple, optional
        Kernel size for encoder blocks. 
        An `int` results in a global `kernel_size`, a `list` allows to define the `kernel_size` per layer.
        Decoder blocks will mirror the `kernel_size` of the encoder blocks.
        Defaults to 5.
    strides : int | list | tuple, optional
        Strides for encoder blocks. 
        An `int` results in a global value for `strides`, a `list` allows to define the `strides` per layer.
        Decoder blocks will mirror the `strides` of the encoder blocks.
        Defaults to 1.
    padding : str, optional
        Padding for encoder blocks. 
        Decoder blocks will mirror the `padding` of the encoder blocks.
        If `rank=1`, `padding` may be either `"same"` or `"causal"`, `rank>1` enforces `padding="same"`
        to maintain deterministic shapes throughout the model.
        Defaults to `"same"`.
    data_format : str, optional {`"channels_first"`, `"channels_last"`}
        Data format for the convolution operations.
        Defaults to `"channels_last"`.
    dilation_rate : int | list | tuple, optional
        Dilation rates for encoder blocks. 
        An `int` results in a global value for `dilation_rate`, a `list` allows to define the `dilation_rate` per layer.
        Decoder blocks will mirror the `dilation_rate` of the encoder blocks.
        Defaults to 1.
    groups : int, optional
        Number of convolutional groups for encoder blocks. 
        An `int` results in a global value for `groups`, a `list` allows to define the `groups` per layer.
        Decoder blocks will mirror the `groups` of the encoder blocks.
        Defaults to 1.
    use_skip_connection : bool | list, optional
        Whether to use skip connections (basically transform FCN to a Unet).
        Can be defined per layer, i.e., 
        `use_skip_connection=[True, False, False]` results in a skip connection on the highest level only.
        Defaults to `False`.
    activation : str | keras.activations.Activation | keras.layers.Layer, optional
        Global activation function.
        Can be either a `str`, a `keras.activations.Activation`, or a `keras.layers.Layer`.
        Defaults to `"relu"`.
    use_bias : bool, optional
        If `True`, all layers use a bias.
        Defaults to `True`.
    bottleneck : keras.layers.Layer | keras.models.Model, optional
        An optional `keras.layer.Layer` or `keras.models.Model` that is placed in the bottleneck of the model.
        Defaults to `None`.
    merge_layer : str | keras.layers.Layer, optional {`"concatenate"`, `"average"`, `"maximum"`, `"minimum"`, `"add"`, `"subtract"`, `"multiply"`, `"dot"`}
        Layer to merge the forward information with the (optional) information from skip connections.
        For this parameter to have an impact, there has to be at least one skip connection in the model.
        Defaults to `"concatenate"`.
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
        Name of the model.
        If `None`, `name` is automatically inherited from the class name `"BaseFCN"`.
        Defaults to `None`.

    Notes
    -----
    The `filters` argument steers the depth of the model and the layout of the encoder- and decoder blocks on each level:
    A list containing tuples results in multiple convolutions on the respective level, e.g.,
    `filters=[(8, 8), 16, 32]` will return a model with a depth of 3, 
    where the first encoder (and last decoder) block has two consecutive convolutions with `filters=8`,
    and the remaining two levels have only a single convolution with `filters=16` and `filters=32`, respectively.

    Downsampling is realized using a strided convolution as proposed by [Springenberger et al.](https://arxiv.org/abs/1412.6806)

    """

    def __init__(
        self,
        rank,
        filters=[8, 16, 32],
        kernel_size=5,
        strides=1,
        padding="same",
        data_format="channels_last",
        dilation_rate=1,
        groups=1,
        use_skip_connection=False,
        activation="relu",
        use_bias=True,
        bottleneck=None,
        merge_layer="concatenate",
        kernel_initializer="he_normal",
        bias_initializer="zeros",
        kernel_regularizer=None,
        bias_regularizer=None,
        kernel_constraint=None,
        bias_constraint=None,
        name=None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)

        self.rank = rank
        self.data_format = data_format
        self.activation = activation
        self.use_bias = use_bias
        self.merge_layer = merge_layer
        
        self.kernel_initializer = kernel_initializer
        self.bias_initializer = bias_initializer
        self.kernel_regularizer = kernel_regularizer
        self.bias_regularizer = bias_regularizer
        self.kernel_constraint = kernel_constraint
        self.bias_constraint = bias_constraint

        # set iterable class variables for the model
        self.set_vars(
            filters=filters, 
            kernel_size=kernel_size, 
            strides=strides,
            padding=padding,
            dilation_rate=dilation_rate,
            groups=groups,
            use_skip_connection=use_skip_connection
        )

        # check `padding` mode
        if (self.rank != 1) & any(item != "same" for item in self.padding):
            raise ValueError(f"For `rank={self.rank}`, `'same'` is the only valid padding mode, received `padding={self.padding}`.")
        
        if (self.rank == 1) & any(item not in ["same", "causal"] for item in self.padding):
            raise ValueError(f"Valid padding modes for `rank=1` are `'same'` and `'causal'`, received `padding={self.padding}`.")

        self.set_encoder_layers()
        self.bottleneck = bottleneck
        self.set_decoder_layers()

        # cache build shapes
        self.global_build_shapes_dict = None        

    def set_encoder_layers(self):
        self.encoder_layers = [
            getattr(import_module(name="...blocks.autoencoder", package=__package__), f"Encoder{self.rank}D")(
                filters=f,
                kernel_size=k,
                strides=s,
                padding=p,
                data_format=self.data_format,
                dilation_rate=d,
                groups=g,
                use_skip_connection=skip,
                activation=self.activation,
                use_bias=self.use_bias,
                kernel_initializer=self.kernel_initializer,
                bias_initializer=self.bias_initializer,
                kernel_regularizer=self.kernel_regularizer,
                bias_regularizer=self.bias_regularizer,
                kernel_constraint=self.kernel_constraint,
                bias_constraint=self.bias_constraint,
                activity_regularizer=self.activity_regularizer,
                name=f"Encoder_{i}"
            ) for i, (f, k, s, p, d, g, skip) in enumerate(
                zip(
                    self.filters,
                    self.kernel_size, 
                    self.strides,
                    self.padding, 
                    self.dilation_rate, 
                    self.groups, 
                    self.use_skip_connection
                )
            )
        ]
    
    def set_decoder_layers(self):
        self.decoder_layers = [
            getattr(import_module(name="...blocks.autoencoder", package=__package__), f"Decoder{self.rank}D")(
                filters=f,
                kernel_size=k,
                strides=s,
                padding=p,
                data_format=self.data_format,
                dilation_rate=d,
                groups=g,
                merge_layer=self.merge_layer, 
                activation=self.activation,
                use_bias=self.use_bias,
                kernel_initializer=self.kernel_initializer,
                bias_initializer=self.bias_initializer,
                kernel_regularizer=self.kernel_regularizer,
                bias_regularizer=self.bias_regularizer,
                kernel_constraint=self.kernel_constraint,
                bias_constraint=self.bias_constraint,
                activity_regularizer=self.activity_regularizer,
                name=f"Decoder_{len(self.filters) - i - 1}"
            ) for i, (f, k, s, p, d, g) in enumerate(
                zip(
                    list(reversed(self.filters)), 
                    list(reversed(self.kernel_size)),
                    list(reversed(self.strides)),
                    list(reversed(self.padding)),
                    list(reversed(self.dilation_rate)),
                    list(reversed(self.groups))
                )
            )
        ]

    def build(self, input_shape):
        """
        Build method of `BaseFNO`

        Builds all sub-modules and sets `self.built=True`.
        
        Parameters
        ----------
        input_shape : tuple
            Input shape

        """

        if self.built:
            return
        
        # cache build shapes
        self.global_build_shapes_dict = {}

        # build encoder layers
        output_shapes = []
        for layer, layer_uses_skip in zip(self.encoder_layers, self.use_skip_connection):
            # cache input shape
            self.global_build_shapes_dict.update({layer.name: {"input_shape": input_shape}})

            layer.build(input_shape=input_shape)

            # update input shape and append to output_shapes
            input_shape = layer.compute_output_shape(input_shape=input_shape)
            if layer_uses_skip:
                input_shape, input_shape_skip = input_shape
                output_shapes.append(input_shape_skip)
            else:
                output_shapes.append(None)

        # build bottleneck layers
        if self.bottleneck is not None:
            # cache input shape
            self.global_build_shapes_dict.update({self.bottleneck.name: {"input_shape": input_shape}})

            self.bottleneck.build(input_shape=input_shape)
            input_shape = self.bottleneck.compute_output_shape(input_shape=input_shape)

        # now build decoder layers
        output_shapes.reverse()

        for layer, input_shape_skip in zip(self.decoder_layers, output_shapes):
            # cache input shape
            self.global_build_shapes_dict.update({layer.name: {"input_shape": input_shape, "input_shape_skip": input_shape_skip}})

            layer.build(input_shape=input_shape, input_shape_skip=input_shape_skip)
            input_shape = layer.compute_output_shape(input_shape=input_shape, input_shape_skip=input_shape_skip)

        self.built = True

    def call(self, inputs):
        """
        
        Parameters
        ----------
        inputs : KerasTensor
            Input to BaseFCN

        Returns
        -------
        outputs : KerasTensor
            Output of BaseFCN

        """

        skip = []
        # forward path through encoder
        x = inputs
        for layer, layer_uses_skip in zip(self.encoder_layers, self.use_skip_connection):
            x = layer(x)
            if layer_uses_skip:
                x, x_skip = x
                skip.append(x_skip)
            else:
                skip.append(None)

        # apply bottlebeck layer
        if self.bottleneck is not None:
            x = self.bottleneck(x)

        # forward path through decoder
        for i, layer in enumerate(self.decoder_layers):
            x = layer(x, skip=skip[len(self.decoder_layers) - i - 1])

        return x
    
    def compute_output_shape(self, input_shape):
        """
        Compute output shape of `BaseFCN`

        Parameters
        ----------
        input_shape : tuple
            Input shape.

        Returns
        -------
        output_shape : tuple
            Output shape.

        """

        skip = []
        for layer, layer_uses_skip in zip(self.encoder_layers, self.use_skip_connection):
            if layer_uses_skip:
                
                input_shape, skip_shape = layer.compute_output_shape(input_shape=input_shape)
                skip.append(skip_shape)
            else:
                input_shape = layer.compute_output_shape(input_shape=input_shape)
                skip.append(None)

        # apply bottlebeck layer
        if self.bottleneck is not None:
            input_shape = self.bottleneck.compute_output_shape(input_shape=input_shape)

        # forward path through decoder
        for i, layer in enumerate(self.decoder_layers):
            input_shape = layer.compute_output_shape(input_shape=input_shape, input_shape_skip=skip[len(self.decoder_layers) - i - 1])

        return input_shape

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
            "padding": self.padding,
            "data_format": self.data_format,
            "dilation_rate": self.dilation_rate,
            "groups": self.groups,
            "use_skip_connection": self.use_skip_connection,
            "merge_layer": saving.serialize_keras_object(self.merge_layer),
            "activation": saving.serialize_keras_object(self.activation),
            "use_bias": self.use_bias,
            "kernel_initializer": initializers.serialize(self.kernel_initializer),
            "bias_initializer": initializers.serialize(self.bias_initializer),
            "kernel_regularizer": regularizers.serialize(self.kernel_regularizer),
            "bias_regularizer": regularizers.serialize(self.bias_regularizer),
            "kernel_constraint": constraints.serialize(self.kernel_constraint),
            "bias_constraint": constraints.serialize(self.bias_constraint)
        })
        
        if self.bottleneck is not None:
            config.update({"bottleneck": saving.serialize_keras_object(self.bottleneck)})
        return config
    
    @classmethod
    def from_config(cls, config):
        """
        Necessary for Keras deserialization

        Parameters
        ----------
        cls : BaseFCN
            The `BaseFCN` class.
        config : dict
            Dictionary with the layer configuration.

        Returns
        -------
        cls : BaseFCN
            Instance of `BaseFCN` from `config`.
            
        """

        activation_cfg = config.pop("activation")
        merge_layer_cfg = config.pop("merge_layer")
        kernel_initializer_cfg = config.pop("kernel_initializer")
        bias_initializer_cfg = config.pop("bias_initializer")
        kernel_regularizer_cfg = config.pop("kernel_regularizer")
        bias_regularizer_cfg = config.pop("bias_regularizer")
        kernel_constraints_cfg = config.pop("kernel_constraint")
        bias_constraints_cfg = config.pop("bias_constraint")
        bottleneck_cfg = config.pop("bottleneck", None)

        # now update with deserialized version
        config.update({
            "activation": saving.deserialize_keras_object(activation_cfg),
            "merge_layer": saving.deserialize_keras_object(merge_layer_cfg),
            "kernel_initializer": initializers.deserialize(kernel_initializer_cfg),
            "bias_initializer": initializers.deserialize(bias_initializer_cfg),
            "kernel_regularizer": regularizers.deserialize(kernel_regularizer_cfg),
            "bias_regularizer": regularizers.deserialize(bias_regularizer_cfg),
            "kernel_constraint": constraints.deserialize(kernel_constraints_cfg),
            "bias_constraint": constraints.deserialize(bias_constraints_cfg)
        })
        if bottleneck_cfg:
            config.update({"bottleneck": saving.deserialize_keras_object(bottleneck_cfg)})

        return cls(**config)
    
    def get_build_config(self) -> dict:
        return self.global_build_shapes_dict
    
    def build_from_config(self, config):
        for layer in self.layers:
            try:
                layer.build(**config[layer.name])
            except ValueError:
                # layer is already build
                pass
            except KeyError:
                # layer has not input shape, e.g., activation layer like ReLU
                pass

        self.built = True


class BaseUnet(BaseFCN):
    """
    Base class of Unet, cf. [Ronneberger et al.](https://arxiv.org/abs/1505.04597)

    Convolutional autoencoder *with* skip-connections

    Parameters
    ----------
    rank : int {1, 2, 3}
        Rank of `BaseUnet`. Must be within {1, 2, 3}.
    filters : int | list | tuple
        Number of filters. 
        The model will be build symmetrically, meaning that only the number of encoder filters is defined,
        and the decoder will mirror it.
    kernel_size : int | list | tuple, optional
        Kernel size for encoder blocks. 
        An `int` results in a global `kernel_size`, a `list` allows to define the `kernel_size` per layer.
        Decoder blocks will mirror the `kernel_size` of the encoder blocks.
        Defaults to 5.
    strides : int | list | tuple, optional
        Strides for encoder blocks. 
        An `int` results in a global value for `strides`, a `list` allows to define the `strides` per layer.
        Decoder blocks will mirror the `strides` of the encoder blocks.
        Defaults to 1.
    padding : str, optional
        Padding for all convolutional layers in the model.
        If `rank=1`, `padding` may be either `"same"` or `"causal"`, `rank>1` enforces `padding="same"`
        to maintain deterministic shapes throughout the model.
        Defaults to `"same"`.
    data_format : str, optional {`"channels_first"`, `"channels_last"`}
        Data format for the convolution operations.
        Defaults to `"channels_last"`.
    dilation_rate : int | list | tuple, optional
        Dilation rates for encoder blocks. 
        An `int` results in a global value for `dilation_rate`, a `list` allows to define the `dilation_rate` per layer.
        Decoder blocks will mirror the `dilation_rate` of the encoder blocks.
        Defaults to 1.
    groups : int, optional
        Number of convolutional groups for encoder blocks. 
        An `int` results in a global value for `groups`, a `list` allows to define the `groups` per layer.
        Decoder blocks will mirror the `groups` of the encoder blocks.
        Defaults to 1.
    activation : str | keras.activations.Activation | keras.layers.Layer, optional
        Global activation function.
        Can be either a `str`, a `keras.activations.Activation`, or a `keras.layers.Layer`.
        Defaults to `"relu"`.
    use_bias : bool, optional
        If `True`, all layers use a bias.
        Defaults to `True`.
    bottleneck : keras.layers.Layer | keras.models.Model, optional
        An optional `keras.layer.Layer` or `keras.models.Model` that is placed in the bottleneck of the model.
        Defaults to `None`.
    merge_layer : str | keras.layers.Layer, optional {`"concatenate"`, `"average"`, `"maximum"`, `"minimum"`, `"add"`, `"subtract"`, `"multiply"`, `"dot"`}
        Layer to merge the forward information with the information from skip connections.
        Defaults to `"concatenate"`.
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
        Name of the model.
        If `None`, `name` is automatically inherited from the class name `"BaseUnet"`.
        Defaults to `None`.

    Notes
    -----
    The `filters` argument steers the depth of the model and the layout of the encoder- and decoder blocks on each level:
    A list containing tuples results in multiple convolutions on the respective level, e.g.,
    `filters=[(8, 8), 16, 32]` will return a model with a depth of 3, 
    where the first encoder (and last decoder) block has two consecutive convolutions with `filters=8`,
    and the remaining two levels have only a single convolution with `filters=16` and `filters=32`, respectively.

    Downsampling is realized using a strided convolution as proposed by [Springenberger et al.](https://arxiv.org/abs/1412.6806)

    """

    def __init__(self,
        rank,
        filters=[8, 16, 32],
        kernel_size=5,
        strides=1,
        padding="same",
        data_format="channels_last",
        dilation_rate=1, 
        groups=1, 
        activation="relu",
        use_bias=True,
        bottleneck=None,
        merge_layer="concatenate",
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
            rank=rank,
            filters=filters,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            data_format=data_format,
            dilation_rate=dilation_rate,
            groups=groups,
            use_skip_connection=True,
            activation=activation,
            use_bias=use_bias,
            bottleneck=bottleneck,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            name=name,
            merge_layer=merge_layer,
            **kwargs
        )

    def get_config(self) -> dict:
        config = super().get_config()
        config.pop("use_skip_connection", None)  # This should always be `True` for UNet

        return config
    