from keras import layers
from keras import ops
from keras import saving
from keras.src.models import Sequential
from keras.src.models import Functional
from keras.src.layers.convolutional.base_conv import BaseConv
from keras.src.layers.convolutional.base_separable_conv import BaseSeparableConv
from keras.src.layers.convolutional.base_conv_transpose import BaseConvTranspose
from keras.src.backend import standardize_data_format


@saving.register_keras_serializable(package="Kerex.Layers.Wrapper", name="TemporalSlice")
class TemporalSlice(layers.Wrapper):
    """
    Temporal slice wrapper

    Can be used to wrap any Keras `layer` or `Model`.
    This wrapper executes the wrapped Keras `layer` or `Model` multiple times and stacks the output.

    For example, given an input `(1, 32, 10)` of shape `(batch_size, x, t)`,
    this wrapper can be used to wrap a pre-trained model which processes inputs of shape `(1, 32, 8)`.
    With `strides=1`, the model has to be called three times in order to process the input of shape `(1, 32, 10)`.
    
    Parameters
    ----------
    layer : Layer
        Keras `layer` or `Model` to be wrapped.
    window_size : int
        Length (time steps) of the input to a single wrapped `layer` or `Model`.
    strides : int, optional
        Strides between temporal windows.
        Defaults to 1.
    axis : int, optional
        Axis along which the sequence of outputs is stacked along.
        If not set, the axis is derived from the `data_format`.
        Defaults to `None`.
    name : str, optional
        Name of the wrapper, that is prepended to the name of the wrapped layer.
        Defaults to `"temporal_slice"`.
    **kwargs : Additional keyword arguments for the `Wrapper` super-class.

    Raises
    ------
    RuntimeError
        If there is a reshape layer in the `Model` that is not the last layer.

    Notes
    -----
    The layer is fully compatible with Keras automatic differentiation,
    and thus can be used on trainable layers and Models.

    If the wrapped layer is a Sequential model which contains a (non-trainable) reshape layer,
    the layer is removed, since it complicates things a lot!

    """

    def __init__(self, layer, window_size, strides=1, axis=None, name="temporal_slice", **kwargs):
        name = "_".join([name, layer.name])
        super().__init__(layer, **kwargs)

        if isinstance(self.layer, Sequential):
            is_reshape_layer = [issubclass(type(layer), layers.Reshape) for layer in self.layer.layers]
            if any(is_reshape_layer):
                if (sum(is_reshape_layer) == 1) and (is_reshape_layer.index(True) + 1 == len(is_reshape_layer)):
                    # there is only a single reshape layer and it is the last layer in the Sequential model. we can simply remove it
                    model_layers: list = self.layer.layers
                    model_layers.pop(-1)
                    self.layer = Sequential(model_layers)
                else:
                    raise RuntimeError(f"Wrapped model has reshape layers. Please remove those before wrapping model.")

        # inherit data format from wrapped layer
        try:
            self.data_format = self.layer.data_format
            self.is_convolutional = True
        except AttributeError:
            if isinstance(self.layer, Sequential):
                seq_layers = self.layer.layers
            elif not isinstance(self.layer, Functional):
                # We treat subclassed models as a simple sequence of layers, for logging
                # purposes.
                seq_layers = self.layer.layers

            conv_layers = [isinstance(type(l), (BaseConv, BaseConvTranspose, BaseSeparableConv)) for l in seq_layers]
            if any(conv_layers):
                self.is_convolutional = True
                self.data_format = seq_layers[conv_layers.index(True)].data_format
            else:
                self.is_convolutional = False
                self.data_format = "channels_last"  # make an educated guess regarding the data format

        # set axis for temporal slice. defaults to the channel axis / -1
        self.axis = axis or -1 if self.data_format == "channels_last" else 1

        # sliding window parameters
        self.window_size = window_size
        self.strides = strides
        self.num_windows = None  # is set in build method, since it depends on the input shape!

        self.transpose_axes = None  # is set in build method, too

    def build(self, input_shape):
        """
        Build method of `TemporalSlice`.

        Builds all sub-modules and sets `self.built=True`.

        Parameters
        ----------
        input_shape : tuple
            Shape of the input data.

        """

        # get feature axes, i.e., axes that remain untouched for input shape for a single wrapped instance
        feature_axes = list(range(len(input_shape)))
        feature_axes.pop(0)  # remove batch
        feature_axes.pop(self.axis)  # remove axis we operate on

        # update input shape
        input_slice = [None, *[input_shape[item] for item in feature_axes]]

        # if self.is_convolutional:
        if self.axis == -1:
            input_slice.append(self.window_size)
        else:
            input_slice.insert(self.axis, self.window_size)

        input_slice = tuple(input_slice)

        # build super()
        super().build(input_shape=input_slice)

        # now, set sliding window params
        sequence_length = input_shape[self.axis]
        self.num_windows = max(0, (sequence_length - self.window_size) // self.strides + 1)
        if self.num_windows < 2:
            raise ValueError(f"Invalid number of windows {self.num_windows}. Increase window size ({self.window_size}) or increase strides ({self.strides}).")

        """ define transpose axis
        The output of the vectorized map will be (self.num_windows, *output_shape)
        We first have to move the first dimension to the last axis,
        to then stack the last two axes with a reshape layer
        """
        # define transpose axes
        transpose_axes = list(range(1, len(input_shape) + 1 if self.is_convolutional else len(input_shape)))

        # first, move first axis (0) after the original channel axis
        if self.axis == -1:
            transpose_axes.append(0)
        else:
            transpose_axes.insert(self.axis + 1 if self.is_convolutional else self.axis, 0)

        self.transpose_axes = transpose_axes

        """ define reshape op
        we have to merge the channel axes
        """
        # if self.is_convolutional:
        output_shape = self.layer.compute_output_shape(input_shape=input_slice)

        # remove batch dimension from output shape
        output_shape = list(output_shape)
        output_shape.pop(0)

        target_shape = [1] * len(output_shape)
        target_shape[self.axis] = self.num_windows

        self.target_shape = tuple([int(ts * os) for ts, os in zip(output_shape, target_shape)])

        self.reshape = layers.Reshape(target_shape=self.target_shape)

        self.built = True

    def call(self, inputs):
        """
        Call method of `TemporalSlice`

        The input is first processed using a sliding window along `self.axis` of the data.
        Then, the wrapped `layer` or `Model` is called on each slice.
        The outputs are stacked along `self.axis` of the data.

        Parameters
        ----------
        inputs : KerasTensor
            Input tensor for the wrapped Keras `layer` or `Model`.

        Returns
        -------
        outputs : KerasTensor
            Output tensor of the wrapped Keras `layer` or `Model`.

        """

        slices = ops.array([ops.take(inputs, indices=ops.arange(i, i + self.window_size, self.strides), axis=self.axis) for i in range(self.num_windows)])        
        x = ops.vectorized_map(self.layer, slices)

        # combine first and last dimension somehow. we need to stack them ideally
        x = ops.transpose(x, axes=self.transpose_axes)
        if self.is_convolutional:
            x = self.reshape(x)

        return x
    
    def get_config(self):
        """
        Get config method.
        Required for serialization.

        Returns
        -------
        config : dict
            Dictionary with the configuration of `Residual`.

        """

        config: dict = super().get_config()
        config.update({
            "window_size": self.window_size,
            "strides": self.strides,
            "axis": self.axis
        })
        return config
    
    @classmethod
    def from_config(cls, config):
        """
        From config method.
        Required for deserialization.

        Parameters
        ----------
        config : dict
            Dictionary with the configuration of `TemporalSlice`.

        Returns
        -------
        cls : TemporalSlice
            A instance of class `TemporalSlice` based on `config`.

        """

        layer_config = config.pop('layer')
        layer = saving.deserialize_keras_object(layer_config)

        return cls(layer=layer, **config)

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
            Shape of the output of `TemporalSlice`.

        """

        input_shape = list(input_shape)
        b = input_shape.pop(0)
        output_shape = (b, *self.target_shape)
        return output_shape


class TemporalSliceV2(layers.Wrapper):
    """
    call model on windows along an axis of the data

    e.g. 
    input_shape = (1, 16, 32, 32, 3)
    model_input_shape = (1, 4, 32, 32, 3)
    model_output_shape = (1, 1, 32, 32, 3)
    --> call model 13 times along first axis of input and stacks the output along the same axis
    --> TemporalSliceV2(model): (1, 16, 32, 32, 3) -> (1, 13, 32, 32, 3)

    It is assumed, that the wrapper layer or model is convolutional

    """

    def __init__(self, layer, window_size, strides=1, axis=None, data_format=None, name="temporal_slice", **kwargs):
        name = f"{name}({layer.name})"
        super().__init__(layer=layer, name=name, **kwargs)

        # remove reshape layer from any `Sequential` model
        if isinstance(self.layer, Sequential):
            is_reshape_layer = [issubclass(type(layer), layers.Reshape) for layer in self.layer.layers]
            if any(is_reshape_layer):
                if (sum(is_reshape_layer) == 1) and (is_reshape_layer.index(True) + 1 == len(is_reshape_layer)):
                    # there is only a single reshape layer and it is the last layer in the Sequential model. we can simply remove it
                    model_layers: list = self.layer.layers
                    model_layers.pop(-1)
                    self.layer = Sequential(model_layers)
                else:
                    raise RuntimeError(f"Wrapped model has reshape layers. Please remove those before wrapping model.")

        self.data_format = standardize_data_format(data_format)  # defaults to `"channels_last"`

        # set axis for temporal slice. defaults to the channel axis / -1
        self.axis = axis or -1 if self.data_format == "channels_last" else 1

        # sliding window parameters
        self.window_size = window_size
        self.strides = strides
        self.num_windows = None  # is set in build method, since it depends on the input shape!

        self.transpose_axes = None  # is set in build method, too

    def build(self, input_shape):
        if self.built:
            return
        
        # get feature axes, i.e., axes that remain untouched for input shape for a single wrapped instance
        feature_axes = list(range(len(input_shape)))
        feature_axes.pop(0)  # remove batch
        feature_axes.pop(self.axis)  # remove axis we operate on

        # update input shape
        input_slice = [None, *[input_shape[item] for item in feature_axes]]

        if self.axis == -1:
            input_slice.append(self.window_size)
        else:
            input_slice.insert(self.axis, self.window_size)

        input_slice = tuple(input_slice)

        # build super()
        super().build(input_shape=input_slice)

        # define input_spec
        channel_axis = input_shape[self.axis]
        input_time_steps = input_shape[self.axis]

        self.input_spec = layers.InputSpec(ndim=len(input_slice) - 2, axes={channel_axis: input_time_steps})