from keras import layers
from ...ops import get_layer
from importlib import import_module


class BaseSmoothUpSampling(layers.Layer):
    def __init__(
        self, 
        rank,
        filters, 
        kernel_size, 
        strides=1,
        padding="valid",
        data_format=None,
        dilation_rate=1,
        groups=1,
        activation=None,
        use_bias=True,
        kernel_initializer="glorot_uniform",
        bias_initializer="zeros",
        kernel_regularizer=None,
        bias_regularizer=None,
        activity_regularizer=None,
        kernel_constraint=None,
        bias_constraint=None,
        name=None, 
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.rank = rank
        
        # get layers
        self.upsampling = None  # is set in subclassed layers since the args are vastly different across 1-D, 2-D, and 3-D
        self.conv = getattr(import_module(name="...layers.conv", package=__package__), f"Conv{self.rank}D")(
            filters=filters,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            data_format=data_format,
            dilation_rate=dilation_rate,
            groups=groups,
            activation=activation,
            use_bias=use_bias,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            **kwargs
        )

    def build(self, input_shape):
        if self.built:
            return
        
        # define input spec
        channel_axis = len(input_shape) if self.data_format == "channels_last" else 1
        input_channel = input_shape[channel_axis]
        self.input_spec = layers.InputSpec(ndim=self.rank + 2, axes={channel_axis: input_channel})

        # build upsampling layer
        self.upsampling.build(input_shape)
        input_shape = self.upsampling.compute_output_shape(input_shape=input_shape)

        # build conv layer
        self.conv.build(input_shape=input_shape)

        self.built = True

    def call(self, inputs):
        x = self.upsampling(inputs)
        return self.conv(x)
    
    def get_config(self):
        config = super().get_config()

        config.update({**self.upsampling.get_config()})
        config.update({**self.conv.get_config()})

        return config
