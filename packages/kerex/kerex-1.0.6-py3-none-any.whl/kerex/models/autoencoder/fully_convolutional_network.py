from keras import saving
from .base_models import BaseFCN


@saving.register_keras_serializable(package="Kerex.Models.AutoEncoder", name="FCN1D")
class FCN1D(BaseFCN):
    """
    1-D implementation of Fully Convolutional Network (FCN)

    The model is build from a convolutional encoder- and a decoder path,
    and is able to extract features on different scale of the data
    by bisecting the features with each level of the model.

    Parameters
    ----------
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
    padding : str, optional {`"same"`, `"causal"`}
        Padding for all convolutional layers in the model.
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
        If `None`, `name` is automatically inherited from the class name `"FCN1D"`.
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
            bottleneck=bottleneck,
            merge_layer=merge_layer, 
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            name=name,
            **kwargs
        )


@saving.register_keras_serializable(package="Kerex.Models.AutoEncoder", name="FCN2D")
class FCN2D(BaseFCN):
    """
    2-D implementation of Fully Convolutional Network (FCN)

    The model is build from a convolutional encoder- and a decoder path,
    and is able to extract features on different scale of the data
    by bisecting the features with each level of the model.

    Parameters
    ----------
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
        If `None`, `name` is automatically inherited from the class name `"FCN2D"`.
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
        filters=[8, 16, 32],
        kernel_size=5,
        strides=1,
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
            bottleneck=bottleneck,
            merge_layer=merge_layer, 
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            name=name,
            **kwargs
        )


@saving.register_keras_serializable(package="Kerex.Models.AutoEncoder", name="FCN3D")
class FCN3D(BaseFCN):
    """
    3-D implementation of Fully Convolutional Network (FCN)

    The model is build from a convolutional encoder- and a decoder path,
    and is able to extract features on different scale of the data
    by bisecting the features with each level of the model.

    Parameters
    ----------
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
        If `None`, `name` is automatically inherited from the class name `"FCN3D"`.
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
        filters=[8, 16, 32],
        kernel_size=5,
        strides=1,
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
            bottleneck=bottleneck,
            merge_layer=merge_layer, 
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            name=name,
            **kwargs
        )
    