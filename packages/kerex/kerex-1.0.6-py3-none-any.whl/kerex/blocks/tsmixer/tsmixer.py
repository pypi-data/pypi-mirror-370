from keras import saving
from keras import layers


@saving.register_keras_serializable(package="KerasAddon.Blocks", name="TSMixerBlock")
class TSMixerBlock(layers.Layer):
    """
    TSMixer block, cf. [Chen et al.](https://doi.org/10.48550/arXiv.2303.06053)

    Parameters
    ----------
    num_hidden : int, optional
        Number of units in dense layer.
        If `None`, the feature space is expanded by factor of 4.
        Defaults to `None`.
    norm : str, optional {`"LN"`, `"BN"`}
        Normalization type, can be layer normalization (`"LN"`) or batch normalization (`"BN"`).
        Defaults to `"LN"`.
    activation : str | keras.activations.Activation | keras.layers.Layer, optional
        Activation for dense layers.
        Can be either a `str`, a `keras.activations.Activation`, or a `keras.layers.Layer`.
        Defaults to `"relu"`.
    dropout_rate : float, optional
        Dropout rate.
        Defaults to 0.1.
    name : str, optional
        Name of the layer.
        If `None`, `name` is automatically inherited from the class name `"TSMixerBlock"`.
        Defaults to `None`.
    **kwargs : Additional keyword arguments for the `keras.layers.Layer` super-class.

    Raises
    ------
    ValueError
        If `norm` other than `"LN"` or `"BN"` is provided.

    Notes
    -----
    Adapted for Keras3 from https://github.com/google-research/google-research/tree/master/tsmixer

    """

    def __init__(
        self,
        num_hidden=None,
        norm="LN",
        activation="relu",
        dropout_rate=0.1,
        name=None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)

        self.num_hidden = num_hidden
        self.norm = norm
        self.activation = activation
        self.dropout_rate = dropout_rate

        # define layers
        if self.norm == "LN":
            self.temporal_norm = layers.LayerNormalization(axis=(-2, -1), name="temporal_norm")
            self.feature_norm = layers.LayerNormalization(axis=(-2, -1), name="feature_norm")
        elif self.norm == "BN":
            self.temporal_norm = layers.BatchNormalization(axis=-2, name="temporal_norm")
            self.feature_norm = layers.BatchNormalization(axis=-1, name="feature_norm")
        else:
            raise ValueError(f"Unknown `norm` '{self.norm}'. Valid values for `norm` are `'LN'` (layer norm) and `'BN'` (batch norm).")

        self.transpose_1 = layers.Permute(dims=(2, 1), name="transpose_1")
        self.transpose_2 = layers.Permute(dims=(2, 1), name="transpose_2")

        # temporal linear layers
        self.temporal_dense = None  # depends on input shape! move to build method
        self.temporal_dropout = layers.Dropout(rate=self.dropout_rate)

        # feature linear layers
        self.feature_dense_1 = None
        self.feature_dropout_1 = layers.Dropout(rate=self.dropout_rate)
        self.feature_dense_2 = None  # depends on input shape! move to build method
        self.feature_dropout_2 = layers.Dropout(rate=self.dropout_rate)

    def build(self, input_shape):
        if self.built:
            return

        # build layers sequentually by building the layers and updating the input shape
        self.temporal_norm.build(input_shape=input_shape)
        forward_shape = self.temporal_norm.compute_output_shape(input_shape=input_shape)

        self.transpose_1.build(input_shape=forward_shape)
        forward_shape = self.transpose_1.compute_output_shape(input_shape=forward_shape)

        # temporal_dense is not defined yet
        self.temporal_dense = layers.Dense(units=forward_shape[-1], activation=self.activation, name="temporal_dense")
        self.temporal_dense.build(input_shape=forward_shape)
        forward_shape = self.temporal_dense.compute_output_shape(input_shape=forward_shape)

        self.transpose_2.build(input_shape=forward_shape)
        forward_shape = self.transpose_2.compute_output_shape(input_shape=forward_shape)

        # dropout does not modify `forward-shape`
        self.temporal_dropout.build(input_shape=forward_shape)

        # addition does not alter the `forward_shape` either!
        self.feature_norm.build(input_shape=forward_shape)
        forward_shape = self.feature_norm.compute_output_shape(input_shape=forward_shape)

        # feature_dense_1 is not defined yet
        self.feature_dense_1 = layers.Dense(units=self.num_hidden or 4 * forward_shape[-1], activation=self.activation, name="feature_dense_1")
        self.feature_dense_1.build(input_shape=forward_shape)
        forward_shape = self.feature_dense_1.compute_output_shape(input_shape=forward_shape)

        self.feature_dropout_1.build(input_shape=forward_shape)

        # feature_dense_2 is not defined yet
        self.feature_dense_2 = layers.Dense(units=input_shape[-1], name="feature_dense_2")
        self.feature_dense_2.build(input_shape=forward_shape)
        forward_shape = self.feature_dense_2.compute_output_shape(input_shape=forward_shape)

        self.feature_dropout_2.build(input_shape=forward_shape)

        self.built = True

    def call(self, inputs):
        # temporal linear
        x = self.temporal_norm(inputs)
        x = self.transpose_1(x)
        x = self.temporal_dense(x)
        x = self.transpose_2(x)
        x = self.temporal_dropout(x)

        res = x + inputs

        # feature linear
        x = self.feature_norm(res)
        x = self.feature_dense_1(x)
        x = self.feature_dropout_1(x)
        x = self.feature_dense_2(x)
        x = self.feature_dropout_2(x)

        return x + res
    
    def compute_output_shape(self, input_shape):
        forward_shape = self.temporal_norm.compute_output_shape(input_shape=input_shape)
        forward_shape = self.transpose_1.compute_output_shape(input_shape=forward_shape)
        forward_shape = self.temporal_dense.compute_output_shape(input_shape=forward_shape)
        forward_shape = self.transpose_2.compute_output_shape(input_shape=forward_shape)
        forward_shape = self.feature_norm.compute_output_shape(input_shape=forward_shape)
        forward_shape = self.feature_dense_1.compute_output_shape(input_shape=forward_shape)
        forward_shape = self.feature_dense_2.compute_output_shape(input_shape=forward_shape)

        return forward_shape
    
    def get_config(self):
        config = super().get_config()
        config.update({
            "num_hidden": self.num_hidden,
            "norm": self.norm,
            "activation": saving.serialize_keras_object(self.activation),
            "dropout_rate": self.dropout_rate
        })

        return config
    
    @classmethod
    def from_config(cls, config):
        activation_cfg = config.pop("activation")
        config.update({"activation": saving.deserialize_keras_object(activation_cfg)})

        return cls(**config)
    