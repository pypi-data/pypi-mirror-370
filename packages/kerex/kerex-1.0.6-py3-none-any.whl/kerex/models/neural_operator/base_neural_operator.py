from keras import models
from keras import regularizers, initializers, constraints
from keras import saving
from ...ops.helper import _IterableVars
from importlib import import_module


class BaseNeuralOperator(models.Model, _IterableVars):
    """
    BaseNeuralOperator, cf. [Zongyi etl al.](https://doi.org/10.48550/arXiv.2010.08895)

    Parameters
    ----------
    rank : int {1, 2, 3}
        Rank of `BaseNeuralOperator`. Must be within {1, 2, 3}.
    filters : int | list | tuple
        Number of filters for the sequential FNO layers.
        If this is a list/tuple, the length of this argument determines the number of FNO layers.
    modes : int | list | tuple
        Number of Fourier modes for FNO layers.
        An `int` results in global `modes`, a `list` allows to define the `modes` per FNO layer.
        For `rank>1`, the `modes` can be defined in terms of tuples, 
        where each entry determines the modes in the respective direction,
        e.g., `modes=(8, 4)` will result in 8 modes in y, and 4 modes in x-direction.
    input_projection_dimension : int, optional
        Projection dimension for the input layer.
        If `None`, `input_projection_dimension` is set to the first argument in `filters`.
        Defaults to `None`.
    output_projection_dimension : int, optional
        Projection dimension for the output layer.
        If `None`, `output_projection_dimension` restores the initial channel dimension of the input data.
        Defaults to `None`.
    data_format : str, optional {`"channels_first"`, `"channels_last"`}
        Data format for the convolution operations.
        Defaults to `"channels_last"`.
    merge_layer : str | keras.layers.Layer, optional {`"concatenate"`, `"average"`, `"maximum"`, `"minimum"`, `"add"`, `"subtract"`, `"multiply"`, `"dot"`}
        Merge operation in FNO layers to combine the result from the spectral convolution with the result from the bypass convolution.
        Defaults to `"add"`.
    activation : str | keras.activations.Activation | keras.layers.Layer, optional
        Global activation function.
        Can be either a `str`, a `keras.activations.Activation`, or a `keras.layers.Layer`.
        Defaults to `"gelu"`.
    use_bias : bool, optional
        If `True`, all layers use a bias.
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
        Name of the model.
        If `None`, `name` is automatically inherited from the class name `"BaseNeuralOperator"`.
        Defaults to `None`.

    """

    def __init__(
        self,
        rank,
        filters,
        modes,
        input_projection_dimension=None,
        output_projection_dimension=None,
        data_format="channels_last",
        merge_layer="add",
        activation="gelu",
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
        super().__init__(name=name, **kwargs)

        self.rank = rank
        self.data_format = data_format
        self.activation = activation
        self.use_bias = use_bias
        self.merge_layer = merge_layer

        self.input_projection_dimension = input_projection_dimension
        self.output_projection_dimension = output_projection_dimension
        
        self.kernel_initializer = kernel_initializer
        self.bias_initializer = bias_initializer
        self.kernel_regularizer = kernel_regularizer
        self.bias_regularizer = bias_regularizer
        self.kernel_constraint = kernel_constraint
        self.bias_constraint = bias_constraint

        # set iterable class variables for the model
        self.set_vars(
            filters=filters, 
            modes=modes
        )

        # define layers
        layer_kwargs = dict(
            data_format=self.data_format, 
            use_bias=self.use_bias,
            kernel_initializer=self.kernel_initializer,
            bias_initializer=self.bias_initializer,
            kernel_regularizer=self.kernel_regularizer,
            bias_regularizer=self.bias_regularizer,
            kernel_constraint=self.kernel_constraint,
            bias_constraint=self.bias_constraint
        )

        self.input_projection = getattr(import_module(name="...layers.conv", package=__package__), f"Conv{self.rank}D")(
            filters=self.input_projection_dimension or self.filters[0], 
            kernel_size=1, 
            name="input_projection",
            **layer_kwargs
        )

        self.fno_layers = models.Sequential([
            getattr(import_module(name="...layers", package=__package__), f"FNO{self.rank}D")(
                filters=f, 
                modes=m,
                activation=self.activation,
                merge_layer=self.merge_layer,
                **layer_kwargs
            ) for f, m in zip(self.filters, self.modes)
        ], name="fno_layers")

        self.output_projection = getattr(import_module(name="...layers.conv", package=__package__), f"Conv{self.rank}D")(
            filters=self.output_projection_dimension or 1,  # this is updated in build method IF self.output_projection_filters is None
            kernel_size=1, 
            name="output_projection",
            **layer_kwargs
        )

    def build(self, input_shape):
        """
        Build method of `BaseNeuralOperator`

        Builds all sub-modules and sets `self.built=True`.
        
        Parameters
        ----------
        input_shape : tuple
            Input shape

        """

        if self.built:
            return
        
        if self.output_projection_dimension is None:
            # update filters attribute of `self.output_projection` layer
            # by default, the FNO output projection projects back to the initial dimension
            projection_filters = input_shape[-1 if self.data_format == "channels_last" else 1]
            self.output_projection.filters = projection_filters
                        
        for layer in [self.input_projection, self.fno_layers, self.output_projection]:
            layer.build(input_shape=input_shape)
            input_shape = layer.compute_output_shape(input_shape=input_shape)

        self.built = True

    def call(self, inputs):
        """
        Call method of `BaseNeuralOperator`

        The `inputs` are first projected to `self.input_projection_filters`,
        then processed by sequential FNO layers,
        and finally projected to `self.output_projection_filters`.
        
        Parameters
        ----------
        inputs : KerasTensor
            Input tensor.

        Returns
        -------
        outputs : KerasTensor
            outputs of `BaseNeuralOperator`

        """

        x = self.input_projection(inputs)
        x = self.fno_layers(x)
        x = self.output_projection(x)

        return x
    
    def compute_output_shape(self, input_shape):
        """
        Compute output shape of `BaseNeuralOperator`

        Parameters
        ----------
        input_shape : tuple
            Input shape.

        Returns
        -------
        output_shape : tuple
            Output shape.

        """

        for layer in self.layers:
            input_shape = layer.compute_output_shape(input_shape=input_shape)

        return input_shape
    
    def get_config(self):
        """
        Necessary for Keras serialization

        Returns
        -------
        config : dict
            Dictionary with the layer configuration.
            
        """

        config = super().get_config()
        config.update({
            "filters": self.filters,
            "modes": self.modes,
            "input_projection_dimension": self.input_projection_dimension,
            "output_projection_dimension": self.output_projection_dimension,
            "data_format": self.data_format,
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
        
        return config
    
    @classmethod
    def from_config(cls, config):
        """
        Necessary for Keras deserialization

        Parameters
        ----------
        cls : BaseNeuralOperator
            The `BaseNeuralOperator` class.
        config : dict
            Dictionary with the layer configuration.

        Returns
        -------
        cls : BaseNeuralOperator
            Instance of `BaseNeuralOperator` from `config`.
            
        """

        activation_cfg = config.pop("activation")
        merge_layer_cfg = config.pop("merge_layer")
        kernel_initializer_cfg = config.pop("kernel_initializer")
        bias_initializer_cfg = config.pop("bias_initializer")
        kernel_regularizer_cfg = config.pop("kernel_regularizer")
        bias_regularizer_cfg = config.pop("bias_regularizer")
        kernel_constraints_cfg = config.pop("kernel_constraint")
        bias_constraints_cfg = config.pop("bias_constraint")

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

        return cls(**config)
    
    def summary(self, *args, **kwargs):
        """
        Prints the summary of the model.

        Here `super().summary()` is called with `expand_nested=True`

        Parameters
        ----------
        line_length: int, optional
            Total length of printed lines
            (e.g. set this to adapt the display to different
            terminal window sizes).
        positions: list, optional
            Relative or absolute positions of log elements
            in each line. If not provided, becomes
            `[0.3, 0.6, 0.70, 1.]`. Defaults to `None`.
        print_fn: callable, optional
            Print function to use. By default, prints to `stdout`.
            If `stdout` doesn't work in your environment, change to `print`.
            It will be called on each line of the summary.
            You can set it to a custom function
            in order to capture the string summary.
        show_trainable: bool, optional
            Whether to show if a layer is trainable.
            Defaults to `False`.
        layer_range: list | tuple, optional
            a list or tuple of 2 strings,
            which is the starting layer name and ending layer name
            (both inclusive) indicating the range of layers to be printed
            in summary. It also accepts regex patterns instead of exact
            names. In this case, the start predicate will be
            the first element that matches `layer_range[0]`
            and the end predicate will be the last element
            that matches `layer_range[1]`.
            By default `None` considers all layers of the model.

        Raises
        ------
        ValueError
            If `summary()` is called before the model is built.
        
        """

        kwargs.pop("expand_nested", None)
        return super().summary(expand_nested=True, *args, **kwargs)
