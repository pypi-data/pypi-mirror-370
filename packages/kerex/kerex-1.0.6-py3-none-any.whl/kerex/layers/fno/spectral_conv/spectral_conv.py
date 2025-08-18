from keras import saving
from .base_spectral_conv import BaseSpectralConv


@saving.register_keras_serializable(package="Kerex.Layers.FNO", name="SpectralConv1D")
class SpectralConv1D(BaseSpectralConv):
    def __init__(
        self,
        filters,
        modes,
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
        super().__init__(
            rank=1,
            filters=filters,
            modes=modes,
            data_format=data_format,
            use_bias=use_bias,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            name=name,
            **kwargs
        )


@saving.register_keras_serializable(package="Kerex.Layers.FNO", name="SpectralConv2D")
class SpectralConv2D(BaseSpectralConv):
    def __init__(
        self,
        filters,
        modes,
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
        super().__init__(
            rank=2,
            filters=filters,
            modes=modes,
            data_format=data_format,
            use_bias=use_bias,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            name=name,
            **kwargs
        )


@saving.register_keras_serializable(package="Kerex.Layers.FNO", name="SpectralConv3D")
class SpectralConv3D(BaseSpectralConv):
    def __init__(
        self,
        filters,
        modes,
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
        super().__init__(
            rank=3,
            filters=filters,
            modes=modes,
            data_format=data_format,
            use_bias=use_bias,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            name=name,
            **kwargs
        )
