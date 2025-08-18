from keras import layers
from keras import Sequential
from keras import initializers
from keras import saving
from keras import ops


@saving.register_keras_serializable(package="Kerex.Layers.Wrapper", name="FiLM")
class FiLM(layers.Wrapper):
    """
    Feature-wise Linear Modulation Wrapper

    This class provides a wrapper that allows to condition any Keras layer to an additional input.

    Parameters
    ----------
    layer : Layer
        Keras 'layer' or `Model` to be wrapped.
    num_hidden : int, optional
        Size of latent space of FiLM sub-network.
        Defaults to 16.
    name : str, optional
        Name of the wrapper, that is prepended to the name of the wrapped layer.
        Defaults to `"film_conditioned"`.
    **kwargs : Additional keyword arguments for the `Wrapper` super-class.

    Notes
    -----
    The FiLM approach generates two additional biases, `gamma` and `beta`.
    The activation of the layer `layer(x)` is refined by `y = gamma * layer(x) + beta`.
    The FiLM sub-networks are initiallized such that `gamma~1` and `beta~0`.
    
    The layer refines the features following the [FiLM](https://arxiv.org/abs/1709.07871) approach.

    """

    def __init__(self, layer, num_hidden=16, name="film_conditioned", **kwargs):
        name = "_".join([name, layer.name])
        super().__init__(layer=layer, name=name, **kwargs)
        self.num_hidden = num_hidden

        # inherit information from wrapped layer
        try:
            self.data_format = self.layer.data_format
        except AttributeError:
            self.data_format = "channels_last"  # this is valid for dense layer for example! TODO: check if it really is ;-D

        self.beta = None
        self.gamma = None

    def build(self, input_shape, conditioning_input_shape: tuple):
        """
        Build method of `FiLM`
        
        Builds all sub-modules and sets `self.built=True`.

        Parameters
        ----------
        input_shape : tuple
            Shape of the input.
        conditioning_input_shape : tuple
            Shape of the input used to conidtion the wrapped layer.

        """

        self.layer.build(input_shape)
        output_shape = self.layer.compute_output_shape(input_shape)

        # the output shape of FiLM is a tensor with shape (num_ch,)
        # it's basically and additional bias term!
        num_ch = output_shape[-1 if self.data_format == "channels_last" else 1]

        self.beta = Sequential([
            layers.Dense(
                units=self.num_hidden, 
                activation="relu"
            ),
            layers.Dense(
                units=num_ch, 
                activation="linear", 
                kernel_initializer=initializers.RandomNormal(mean=0.0, stddev=0.01),
                bias_initializer=initializers.Zeros()
            )
        ])
        self.gamma = Sequential([
            layers.Dense(
                units=self.num_hidden, 
                activation="relu"
            ),
            layers.Dense(
                units=num_ch, 
                activation="sigmoid", 
                kernel_initializer=initializers.RandomNormal(mean=0.0, stddev=0.01),
                bias_initializer=initializers.Zeros()
            ),
            layers.Lambda(lambda x: 0.75 + x * 0.5)  # rescale activation. With this, gamma is always in [0.75, 1.25]. Optionally, try x + 0.5 for symmetric activation between [0.5, 1.5]
        ])

        # now build the two sub-networks. For this, we need their input shape
        self.beta.build(conditioning_input_shape)
        self.gamma.build(conditioning_input_shape)

        # declare einsum operation for multiplication
        self.einsum_ops = "bc...,bc->bc..." if self.data_format == "channels_first" else "b...c,bc->b...c"

    def call(self, inputs, conditioning_inputs):
        """
        Call method of `FiLM`.

        Parameters
        ----------
        inputs : KerasTensor
            Input tensor for `FiLM`.
        conditioning_inputs : KerasTensor
            Conditioning input for `FiLM`

        Returns
        -------
        outputs : KerasTensor
            Refined features.

        """

        x = self.layer(inputs)
        beta = self.beta(conditioning_inputs)
        gamma = self.gamma(conditioning_inputs)

        # multiply using einsum
        y1 = ops.einsum(self.einsum_ops, x, gamma)

        # add bias; first, broadcast to same shape as x with einsum!
        bias = ops.einsum(self.einsum_ops, ops.ones_like(x), beta)
        
        return y1 + bias
    
    def get_config(self):
        """
        Get config method.
        Required for serialization.

        Returns
        -------
        config : dict
            Dictionary with the configuration of `SpatialAttentionModule`

        """

        config: dict = super().get_config()
        config.update({"num_hidden": self.num_hidden})
        return config
    
    def compute_output_shape(self, input_shape: tuple, conditioning_input_shape: tuple) -> tuple:
        """
        Compute output shape

        Parameters
        ----------
        input_shape : tuple
            Shape of the input.
        conditioning_input_shape : tuple
            Shape of the conditioning input.

        Returns
        -------
        output_shape : tuple
            Shape of the output of `CBAM`.

        Notes
        -----
        The `conditioning_input` has no impact on the shape.
        In general, `FiLM` does not modify the output shape at all.
        Hence, this layer simply calls the `compute_output_shape` method of the wrapped layer.

        """

        return self.layer.compute_output_shape(input_shape)
    