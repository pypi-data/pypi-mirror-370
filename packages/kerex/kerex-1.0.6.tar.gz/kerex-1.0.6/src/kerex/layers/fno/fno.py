from .base_fno import BaseFNO
from keras import saving


@saving.register_keras_serializable(package="KerasAddon.layers.FNO", name="FNO1D")
class FNO1D(BaseFNO):
    def __init__(
        self, 
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
        super().__init__(
            rank=1, 
            filters=filters, 
            modes=modes, 
            activation=activation, 
            merge_layer=merge_layer,  
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


@saving.register_keras_serializable(package="KerasAddon.layers.FNO", name="FNO2D")
class FNO2D(BaseFNO):
    def __init__(
        self, 
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
        super().__init__(
            rank=2, 
            filters=filters, 
            modes=modes, 
            activation=activation, 
            merge_layer=merge_layer,  
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


@saving.register_keras_serializable(package="KerasAddon.layers.FNO", name="FNO3D")
class FNO3D(BaseFNO):
    def __init__(
        self, 
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
        super().__init__(
            rank=3, 
            filters=filters, 
            modes=modes, 
            activation=activation, 
            merge_layer=merge_layer,  
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
        