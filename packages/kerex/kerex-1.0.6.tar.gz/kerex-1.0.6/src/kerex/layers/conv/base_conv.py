"""
Since the deserialization is broken in the keras BaseConv when using a layer (layers.ReLU()) as activation function,
I had to implement my own base conv and inherit ConvXD from it.

A simple fix in the get_config() and from_config() methods allows to use both sting identifiers ("relu") and layers (layers.ReLU()) as activation function
"""
from keras.src.layers.convolutional.base_conv import BaseConv
from keras.src.layers.convolutional.base_conv_transpose import BaseConvTranspose
from keras.src.layers.convolutional.base_separable_conv import BaseSeparableConv
from keras import saving


class MyBaseConv(BaseConv):
    def get_config(self):
        config: dict = super().get_config()
        config.update({"activation": saving.serialize_keras_object(self.activation)})

        return config
    
    @classmethod
    def from_config(cls, config: dict):
        activation_cfg = config.pop("activation")
        config.update({"activation": saving.deserialize_keras_object(activation_cfg)})

        return cls(**config)
    

class MyBaseConvTranspose(BaseConvTranspose):
    def get_config(self):
        config: dict = super().get_config()
        config.update({"activation": saving.serialize_keras_object(self.activation)})

        return config
    
    @classmethod
    def from_config(cls, config: dict):
        activation_cfg = config.pop("activation")
        config.update({"activation": saving.deserialize_keras_object(activation_cfg)})

        return cls(**config)
    

class MyBaseSeparableConv(BaseSeparableConv):
    def get_config(self):
        config: dict = super().get_config()
        config.update({"activation": saving.serialize_keras_object(self.activation)})

        return config
    
    @classmethod
    def from_config(cls, config: dict):
        activation_cfg = config.pop("activation")
        config.update({"activation": saving.deserialize_keras_object(activation_cfg)})

        return cls(**config)
    