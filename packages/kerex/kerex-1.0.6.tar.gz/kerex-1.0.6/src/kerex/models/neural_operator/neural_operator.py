from keras import saving
from .base_neural_operator import BaseNeuralOperator


@saving.register_keras_serializable(package="Kerex.Models.NeuralOperator", name="NeuralOperator1D")
class NeuralOperator1D(BaseNeuralOperator):
    """
    NeuralOperator1D, cf. [Zongyi etl al.](https://doi.org/10.48550/arXiv.2010.08895)

    Parameters
    ----------
    filters : int | list | tuple
        Number of filters for the sequential FNO layers.
        If this is a list/tuple, the length of this argument determines the number of FNO layers.
    modes : int | list
        Number of Fourier modes for FNO layers.
        An `int` results in global `modes`, a `list` allows to define the `modes` per FNO layer.
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
        super().__init__(
            rank=1,
            filters=filters,
            modes=modes,
            input_projection_dimension=input_projection_dimension,
            output_projection_dimension=output_projection_dimension,
            data_format=data_format,
            merge_layer=merge_layer,
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


@saving.register_keras_serializable(package="Kerex.Models.NeuralOperator", name="NeuralOperator2D")
class NeuralOperator2D(BaseNeuralOperator):
    """
    NeuralOperator2D, cf. [Zongyi etl al.](https://doi.org/10.48550/arXiv.2010.08895)

    Parameters
    ----------
    filters : int | list | tuple
        Number of filters for the sequential FNO layers.
        If this is a list/tuple, the length of this argument determines the number of FNO layers.
    modes : int | list | tuple
        Number of Fourier modes for FNO layers.
        An `int` results in global `modes`, a `list` allows to define the `modes` per FNO layer.
        The `modes` can be defined in terms of tuples, 
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
        super().__init__(
            rank=2,
            filters=filters,
            modes=modes,
            input_projection_dimension=input_projection_dimension,
            output_projection_dimension=output_projection_dimension,
            data_format=data_format,
            merge_layer=merge_layer,
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


@saving.register_keras_serializable(package="Kerex.Models.NeuralOperator", name="NeuralOperator3D")
class NeuralOperator3D(BaseNeuralOperator):
    """
    NeuralOperator3D, cf. [Zongyi etl al.](https://doi.org/10.48550/arXiv.2010.08895)

    Parameters
    ----------
    filters : int | list | tuple
        Number of filters for the sequential FNO layers.
        If this is a list/tuple, the length of this argument determines the number of FNO layers.
    modes : int | list | tuple
        Number of Fourier modes for FNO layers.
        An `int` results in global `modes`, a `list` allows to define the `modes` per FNO layer.
        The `modes` can be defined in terms of tuples, 
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
        super().__init__(
            rank=3,
            filters=filters,
            modes=modes,
            input_projection_dimension=input_projection_dimension,
            output_projection_dimension=output_projection_dimension,
            data_format=data_format,
            merge_layer=merge_layer,
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