from keras.src.layers.merging.base_merge import Merge
from keras import layers
from keras import KerasTensor
from keras import saving
from ...ops import get_layer


@saving.register_keras_serializable(package="Kerex.Layers.Merge", name="AttentionGate")
class AttentionGate(Merge):
    """
    Attention gate for expressive and expensive merging of two tensors

    Parameters
    ----------
    data_format : str, optional {`"channels_first"`, `"channels_last"`}
        Format of the data. Defaults to `"channels_last"`.
    merge_layer : str | Layer, optional {`"concatenate"`, `"average"`, `"maximum"`, `"minimum"`, `"add"`, `"subtract"`, `"multiply"`, `"dot"`}
        Identifier or layer of a valid Keras merge layer, cf. https://keras.io/api/layers/merging_layers/.
        Defaults to `"concatenate"`.
    **kwargs : Additional keyword arguments for the `Merge` super-class.
    
    Raises
    ------
    ValueError
        If `merge_layer` is not a valid Keras merge layer, cf. https://keras.io/api/layers/merging_layers/

    Notes
    -----
    Original paper: https://arxiv.org/pdf/1804.03999

    `merge="add"` is default additive attention gate mechanism from paper,
    `merge="concatenate"` would allow for different input shapes.

    """

    def __init__(self, data_format="channels_last", merge_layer="add", **kwargs):
        super().__init__(**kwargs)
        self.data_format = data_format
        self.axis = -1 if self.data_format == "channels_last" else 1
        try:
            self.merge_layer = get_layer(merge_layer, axis=self.axis)
        except TypeError:
            # if layer does not support axis keyword try again without
            self.merge_layer = get_layer(merge_layer)

        if not issubclass(type(self.merge_layer), Merge):
            raise ValueError(
                f"Merge-layer {self.merge_layer} supplied to Wrapper isn't "
                "a supported merge-layer."
            )

        self.relu = layers.ReLU()
        self.gate = layers.Multiply()

    def build(self, input_shape):
        """
        Build method of `AttentionGate`

        Parameters
        ----------
        input_shape : tuple
            Shape of the input data.

        """

        # Used purely for shape validation.
        if len(input_shape) < 1 or not isinstance(
            input_shape[0], (tuple, list)
        ):
            raise ValueError(
                "A `AttentionGate` layer should be called on a list of "
                f"at least 1 input. Received: input_shape={input_shape}"
            )
        if all(shape is None for shape in input_shape):
            return
        
        # If the inputs have different ranks, we have to reshape them  # TODO check what this exactly does in Merge
        # to make them broadcastable.
        if None not in input_shape and len(set(map(len, input_shape))) == 1:
            self._reshape_required = False
        else:
            self._reshape_required = True

        # derive dimension for convolution from input shapes
        shape_x, shape_g = input_shape
        
        dim = len(shape_x)
        if dim < 3:
            raise ValueError(
                "Dimension of input data too small,"
                f"expect dim>=3, received dim={dim}."
            )
        
        if dim > 5:
            raise ValueError(
                "Dimension of input data too large,"
                f"expect dim<=5, received dim={dim}."
            )
        
        channels_x = shape_x[self.axis]
        channels_g = shape_g[self.axis]

        # channels = min(channels_x, channels_g)

        conv_kwargs = dict(kernel_size=1, padding="same", data_format=self.data_format)

        # get layers
        self.conv_x = get_layer(f"Conv{dim - 2}D", filters=channels_g, **conv_kwargs)
        self.conv_g = get_layer(f"Conv{dim - 2}D", filters=channels_g, **conv_kwargs)
        self.psi = get_layer(f"Conv{dim - 2}D", filters=channels_x, activation="sigmoid", **conv_kwargs)

        # build layers in forward fashion
        self.conv_x.build(input_shape=shape_x)
        self.conv_g.build(input_shape=shape_g)

        shape_x_forward = self.conv_x.compute_output_shape(input_shape=shape_x)
        shape_g = self.conv_g.compute_output_shape(input_shape=shape_g)

        self.merge_layer.build(input_shape=[shape_x_forward, shape_g])  # NOTE this will throw an exception if shapes don't match, so I don't have to implement it myself :-)
        forward_shape = self.merge_layer.compute_output_shape(input_shape=[shape_x_forward, shape_g])
        
        self.psi.build(input_shape=forward_shape)
        shape_alpha = self.psi.compute_output_shape(input_shape=forward_shape)

        # self.merge_layer.build(input_shape=[shape_x, shape_psi])  # NOTE this will throw an exception if shapes don't match, so I don't have to implement it myself :-)
        assert shape_alpha == shape_x  # has to be given to apply gating mechanism

        # build gate layer (just mutliplication)
        self.gate.build(input_shape=[shape_x, shape_alpha])

        self.built = True

    def _merge_function(self, inputs) -> KerasTensor:
        """ unpack inputs.
        convention for UNet model:
        - inputs[0]: x_forward
        - inputs[1]: skip information

        goal is to modulate the skip information, not the forward information,
        at the end, both information (the modulated skip information and the original forward information) are merged
        """
        x_forward, x_skip = inputs

        # apply 1x1 convolutions to inputs
        x_forward_projection = self.conv_x(x_forward)
        x_skip_projection = self.conv_g(x_skip)

        # add inputs and apply relu activation
        alpha = self.merge_layer((x_forward_projection, x_skip_projection))
        alpha = self.relu(alpha)

        # apply 1x1 convolution with sigmoid to get gating behavior
        alpha = self.psi(alpha)

        # apply gating mechanism to x
        # modulated_skip = x_skip * alpha  # NOTE shapes have to match exactly!
        
        # finally apply the merge operation
        return self.gate([x_forward, alpha])
    
    def get_config(self):
        """
        Get config method.
        Required for serialization.

        Returns
        -------
        config : dict
            Dictionary with the configuration of `AttentionGate`.

        """

        config: dict = super().get_config()
        config.update({
            "data_format": self.data_format,
            "merge_layer": saving.serialize_keras_object(self.merge_layer)
        })
        return config

    @classmethod
    def from_config(cls, config: dict):
        """
        From config method.
        Required for deserialization.

        Parameters
        ----------
        config : dict
            Dictionary with the configuration of `AttentionGate`.

        Returns
        -------
        cls : AttentionGate
            A instance of class `AttentionGate` based on `config`.
            
        """
        
        merge_cfg = config.pop("merge_layer")
        config.update({"merge_layer": saving.deserialize_keras_object(merge_cfg)})
        
        return cls(**config)
    
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
            Shape of the output of `AttentionGate`.

        """

        x_shape, g_shape = input_shape

        # go through alpha branch 
        alpha_shape = self.merge_layer.compute_output_shape(input_shape=[x_shape, g_shape])
        alpha_shape = self.psi.compute_output_shape(input_shape=alpha_shape)
        
        output_shape = self.gate.compute_output_shape(input_shape=[x_shape, alpha_shape])

        return output_shape
        