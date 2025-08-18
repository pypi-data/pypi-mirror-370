from .base_upsampling import BaseSmoothUpSampling
from keras import layers
from keras import saving


@saving.register_keras_serializable(package="Kerex.Layers.Reshape", name="SmoothUpSampling1D")
class SmoothUpSampling1D(BaseSmoothUpSampling):
    def __init__(
        self, 
        filters, 
        kernel_size, 
        size=2,
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
        super().__init__(
            rank=1,
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
            name=name, 
            **kwargs
        )

        self.upsampling = layers.UpSampling1D(size=size)


@saving.register_keras_serializable(package="Kerex.Layers.Reshape", name="SmoothUpSampling2D")
class SmoothUpSampling2D(BaseSmoothUpSampling):
    def __init__(
        self, 
        filters, 
        kernel_size, 
        size=(2, 2),
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
        interpolation="nearest",
        name=None, 
        **kwargs
    ):
        super().__init__(
            rank=2,
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
            name=name, 
            **kwargs
        )
        
        self.upsampling = layers.UpSampling2D(
            size=size, 
            interpolation=interpolation,
            data_format=data_format, 
        )


@saving.register_keras_serializable(package="Kerex.Layers.Reshape", name="SmoothUpSampling3D")
class SmoothUpSampling3D(BaseSmoothUpSampling):
    def __init__(
        self, 
        filters, 
        kernel_size, 
        size=(2, 2, 2),
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
        super().__init__(
            rank=3,
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
            name=name, 
            **kwargs
        )

        self.upsampling = layers.UpSampling3D(
            size=size, 
            data_format=data_format, 
        )
