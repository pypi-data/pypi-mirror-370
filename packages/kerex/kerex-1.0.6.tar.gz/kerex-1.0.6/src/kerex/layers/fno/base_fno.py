from keras import layers
from keras import activations
from keras import initializers
from keras import regularizers
from keras import constraints
from keras import saving
from ...layers.wrapper import Residual
from importlib import import_module


class BaseFNO(layers.Layer):
    def __init__(
        self,
        rank,
        filters,
        modes,
        activation="gelu",
        merge_layer="add",
        data_format="channels_last",
        use_bias=True,
        kernel_initializer="he_normal",
        bias_initializer="zeros",
        kernel_constraint=None,
        bias_constraint=None,
        kernel_regularizer=None,
        bias_regularizer=None,
        name=None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.rank = rank
        self.filters = filters
        self.modes = modes
        self.merge_layer = merge_layer
        self.data_format = data_format
        self.use_bias = use_bias
        self.kernel_initializer = kernel_initializer
        self.bias_initializer = bias_initializer
        self.kernel_constraint = kernel_constraint
        self.bias_constraint = bias_constraint
        self.kernel_regularizer = kernel_regularizer
        self.bias_regularizer = bias_regularizer

        self.forward = Residual(
            layer=getattr(import_module(name=".spectral_conv", package=__package__), f"SpectralConv{self.rank}D")(
                filters=self.filters,
                modes=self.modes,
                data_format=self.data_format,
                use_bias=self.use_bias,
                kernel_initializer=self.kernel_initializer,
                bias_initializer=self.bias_initializer,
                kernel_constraint=self.kernel_constraint,
                bias_constraint=self.bias_constraint,
                kernel_regularizer=self.kernel_regularizer,
                bias_regularizer=self.bias_regularizer,
                name="spectral_conv",
                **kwargs
            ),
            merge_layer=self.merge_layer,
            residual_layer=getattr(import_module(name="...layers.conv", package=__package__), f"Conv{self.rank}D")(
                filters=self.filters,
                kernel_size=1,
                data_format=self.data_format,
                use_bias=self.use_bias,
                kernel_initializer=self.kernel_initializer,
                bias_initializer=self.bias_initializer,
                kernel_constraint=self.kernel_constraint,
                bias_constraint=self.bias_constraint,
                kernel_regularizer=self.kernel_regularizer,
                bias_regularizer=self.bias_regularizer,
                name="bypass_conv"
            )
        )
        
        self.activation = activations.get(activation)

    def build(self, input_shape):
        if self.built:
            return
        
        self.forward.build(input_shape=input_shape)

        # inherit input spec from `spectral_conv` layer
        self.input_spec = self.forward.layer.input_spec
        
        self.built = True

    def call(self, inputs):
        x = self.forward(inputs)
        x = self.activation(x)

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
        
        return self.forward.compute_output_shape(input_shape=input_shape)        
    
    def get_config(self):
        config = super().get_config()
        config.update({
            "filters": self.filters,
            "modes": self.modes,
            "activation": saving.serialize_keras_object(self.activation),
            "merge_layer": saving.serialize_keras_object(self.merge_layer),
            "data_format": self.data_format,
            "use_bias": self.use_bias,
            "kernel_initializer": initializers.serialize(self.kernel_initializer),
            "bias_initializer": initializers.serialize(self.bias_initializer),
            "kernel_constraint": constraints.serialize(self.kernel_constraint),
            "bias_constraint": constraints.serialize(self.bias_constraint),
            "kernel_regularizer": regularizers.serialize(self.kernel_regularizer),
            "bias_regularizer": regularizers.serialize(self.bias_regularizer)
        })

        return config
    
    @classmethod
    def from_config(cls, config):
        activation_cfg = config.pop("activation")
        merge_layer_cfg = config.pop("merge_layer")
        kernel_initializer_cfg = config.pop("kernel_initializer")
        bias_initializer_cfg = config.pop("bias_initializer")
        kernel_constraint_cfg = config.pop("kernel_constraint")
        bias_constraint_cfg = config.pop("bias_constraint")
        kernel_regularizer_cfg = config.pop("kernel_regularizer")
        bias_regularizer_cfg = config.pop("bias_regularizer")

        config.update({
            "activation": saving.deserialize_keras_object(activation_cfg),
            "merge_layer": saving.deserialize_keras_object(merge_layer_cfg),
            "kernel_initializer": initializers.deserialize(kernel_initializer_cfg),
            "bias_initializer": initializers.deserialize(bias_initializer_cfg),
            "kernel_constraint": constraints.deserialize(kernel_constraint_cfg),
            "bias_constraint": constraints.deserialize(bias_constraint_cfg),
            "kernel_regularizer": regularizers.deserialize(kernel_regularizer_cfg),
            "bias_regularizer": regularizers.deserialize(bias_regularizer_cfg)
        })

        return cls(**config)
    