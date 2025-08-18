from keras import layers
from keras import saving
from keras.src.layers.merging.base_merge import Merge
from ...ops import get_layer


@saving.register_keras_serializable(package="Kerex.Layers.Wrapper", name="Residual")
class Residual(layers.Wrapper):
    """
    Residual Wrapper

    Can be used to add a residual connection to any Keras layer.

    Parameters
    ----------
    layer : Layer
        Keras `layer` or `Model` to be wrapped.
    merge_layer : str | Layer, optional {`"concatenate"`, `"average"`, `"maximum"`, `"minimum"`, `"add"`, `"subtract"`, `"multiply"`, `"dot"`}
        Identifier or layer of a valid Keras merge layer, cf. https://keras.io/api/layers/merging_layers/.
        Defaults to `"add"`.
    residual_layer : str | Layer, optional
        Identifier or Keras layer that is placed in the residual connection.
        Defaults to `None`.
    name : str, optional
        Name of the wrapper, that is prepended to the name of the wrapped layer.
        Defaults to `"residual"`.
    **kwargs : Additional keyword arguments for the `Wrapper` super-class.

    Raises
    ------
    ValueError
        If `merge_layer` is not a valid Keras merge layer, cf. https://keras.io/api/layers/merging_layers/

    Notes
    -----
    This wrapper allows to implement more complex data flow within the Keras `Sequential` model.
    
    When the wrapped layer modifies the shape of the data, the `residual_layer` has to account for that,
    especially when using a `merge_layer` that expects two inputs of the same shape (e.g., `layers.Add()`).

    Examples
    --------
    The number of filters in the wrapped `Conv1D` layer matches the number of channels in the input,
    such that no `residual_layer` is necessary to merge the information using `merge_layer="add"`.
    >>> from keras import Sequential, layers, ops
    >>> x = ops.ones((1, 32, 3))
    >>> model = Sequential([Residual(layers.Conv1D(filters=3, kernel_size=3, padding="same"))])
    >>> model.build(input_shape=x.shape)
    >>> y = model(x)
    >>> y.shape
    TensorShape([1, 32, 3])
    
    The number of filters in the wrapped `Conv1D` layer **does not match** the number of channels in the input
    Hence, we have to account for the shape modification by projecting the residual information 
    by using a 1x1-`Conv1D` layer with matching number of filters.
    >>> from keras import Sequential, layers, ops
    >>> x = ops.ones((1, 32, 3))
    >>> model = Sequential([Residual(layers.Conv1D(filters=8, kernel_size=3, padding="same"), residual_layer=layers.Conv1D(filters=8, kernel_size=1))])
    >>> model.build(input_shape=x.shape)
    >>> y = model(x)
    >>> y.shape
    TensorShape([1, 32, 8])

    Another way to account for a shape missmatch between then wrapped layer output and the residual information
    is by using a `merge_layer="concatenate"`. The layer just appends the two Tensors along the channel dimension.
    >>> from keras import Sequential, layers, ops
    >>> x = ops.ones((1, 32, 3))
    >>> model = Sequential([Residual(layers.Conv1D(filters=8, kernel_size=3, padding="same"), merge_layer="concatenate")])
    >>> model.build(input_shape=x.shape)
    >>> y = model(x)
    >>> y.shape
    TensorShape([1, 32, 11])  # NOTE 8 + 3 = 11 output channels!

    """

    def __init__(self, layer, merge_layer="add", residual_layer=None, name="residual", **kwargs):
        # get channel axis
        try:
            self.data_format = layer.data_format
        except AttributeError:
            self.data_format = "channels_last"  # this is valid for dense layer for example! TODO: check if it really is ;-D

        # get merge layer
        merge_axis = -1 if self.data_format == "channels_last" else 1
        try:
            self.merge_layer = get_layer(merge_layer, axis=merge_axis)
        except TypeError:
            self.merge_layer = get_layer(merge_layer)

        if not issubclass(type(self.merge_layer), Merge):
            raise ValueError(
                f"Merge-layer {self.merge_layer} supplied to Wrapper isn't "
                "a supported merge-layer."
            )
        
        # get residual layer
        self.residual_layer = get_layer(residual_layer)
        if self.residual_layer is not None:
            if not issubclass(type(self.residual_layer), layers.Layer):
                raise ValueError(
                    f"Residual-layer {self.residual_layer} supplied to Wrapper isn't "
                    "a supported layer type. Please "
                    "ensure residual-layer is a valid Keras layer."
                )
        
        name = '_'.join([name, layer.name])
        super().__init__(layer=layer, name=name, **kwargs)

    def build(self, input_shape):
        """
        Build method of `Residual`.

        Builds all sub-modules and sets `self.built=True`.

        Parameters
        ----------
        input_shape : tuple
            Shape of the input data.

        """

        super().build(input_shape=input_shape)
        forward_shape = self.layer.compute_output_shape(input_shape)

        if self.residual_layer is not None:
            self.residual_layer.build(input_shape)
            input_shape = self.residual_layer.compute_output_shape(input_shape)

        try:
            self.merge_layer.build([forward_shape, input_shape])
        except ValueError:
            raise ValueError(f"Merge layer could not be build. Please provide a residual layer which makes the wrapper layers output and the inputs compatible in shape!")

    def call(self, inputs):
        """
        Call method of `Residual`

        Parameters
        ----------
        inputs : KerasTensor
            Input tensor for the wrapped Keras `layer` or `Model`.

        Returns
        -------
        outputs : KerasTensor
            Output tensor of the wrapped Keras `layer` or `Model`.

        """
        
        x1 = self.layer(inputs)

        if self.residual_layer is not None:
            inputs = self.residual_layer(inputs)
        return self.merge_layer([x1, inputs])
    
    def get_config(self):
        """
        Get config method.
        Required for serialization.

        Returns
        -------
        config : dict
            Dictionary with the configuration of `Residual`.

        """

        config = super().get_config()
        config.update({
            "merge_layer": saving.serialize_keras_object(self.merge_layer),
            "residual_layer": saving.serialize_keras_object(self.residual_layer)
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
            Dictionary with the configuration of `Residual`.

        Returns
        -------
        cls : Residual
            A instance of class `Residual` based on `config`.

        """

        layer_config = config.pop("layer")
        merge_layer_config = config.pop("merge_layer")
        residual_layer_config = config.pop("residual_layer")

        layer = saving.deserialize_keras_object(layer_config)
        merge_layer = saving.deserialize_keras_object(merge_layer_config)
        residual_layer = saving.deserialize_keras_object(residual_layer_config)

        return cls(layer=layer, merge_layer=merge_layer, residual_layer=residual_layer, **config)

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
            Shape of the output of `Residual`.

        """

        forward_shape = self.layer.compute_output_shape(input_shape)

        if self.residual_layer is not None:
            input_shape = self.residual_layer.compute_output_shape(input_shape)

        output_shape = self.merge_layer.compute_output_shape([forward_shape, input_shape])

        return output_shape
