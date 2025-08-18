from keras import layers
from keras import ops
from keras import saving


@saving.register_keras_serializable(package="Kerex.Layers.Wrapper", name="WeightNormalization")
class WeightNormalization(layers.Wrapper):
    """
    Weight Normalization wrapper for any Keras `layer`.
    
    The weight normalization is supposed to accelerate the convergence of stochastic gradient descent optimization.
    It replaces the original weights `w` with a normalized weight `v` that is multiplied by a bias `g`:
    `w -> g * v`
    The original layer bias `b` remains untouched.

    Parameters
    ----------
    layer : Layer
        Keras `layer` to be wrapped.
    name : str, optional
        Name of the wrapper, that is prepended to the name of the wrapped layer.
        Defaults to `"weight_normalization"`.
    **kwargs : Additional keyword arguments for the `Wrapper` super-class.

    Notes
    -----
    Reference: Talisman et al., Weight Normalization: A Simple Reparameterization to Accelerate Training of Deep Neural Networks
    https://arxiv.org/abs/1602.07868

    """

    def __init__(self, layer, name="weight_normalization", **kwargs): 
        name = '_'.join([layer.name, name])
        super().__init__(layer=layer, name=name, **kwargs)

    def build(self, input_shape):
        """
        Build method of `WeightNormalization`.

        Builds all sub-modules and sets `self.built=True`.

        Parameters
        ----------
        input_shape : tuple
            Shape of the input data.

        """

        super().build(input_shape=input_shape)
        self.v = self.add_weight(shape=self.layer.kernel.shape, initializer=self.layer.kernel_initializer, trainable=True)
        self.g = self.add_weight(shape=self.layer.bias.shape, initializer='ones', trainable=True)

    def call(self, inputs):
        """
        Call method of `WeightNormalization`

        The weight normalization is supposed to accelerate the convergence of stochastic gradient descent optimization.
        It replaces the original weights `w` with a normalized weight `v` that is multiplied by a bias `g`:
        `w -> g * v`
        The original layer bias `b` remains untouched.

        Parameters
        ----------
        inputs : KerasTensor
            Input tensor for the wrapped Keras `layer`.

        Returns
        -------
        outputs : KerasTensor
            Output tensor of the wrapped Keras `layer``.

        """
        norm_v = ops.normalize(self.v, axis=0)
        self.layer.set_weights([self.g * norm_v, self.layer.bias])
        return self.layer(inputs)
    
    def compute_output_shape(self, input_shape: tuple) -> tuple:
        """
        Compute output shape

        Parameters
        ----------
        input_shape : tuple
            Shape of the input.

        Returns
        -------
        output_shape : tuple
            Shape of the output of `WeightNormalization`.

        """

        return self.layer.compute_output_shape(input_shape)
    