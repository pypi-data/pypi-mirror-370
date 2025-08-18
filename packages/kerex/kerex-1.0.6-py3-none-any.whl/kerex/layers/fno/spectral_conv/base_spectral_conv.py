from keras import Layer
from keras import initializers
from keras import regularizers
from keras import constraints
from keras import ops
from keras.src.layers.input_spec import InputSpec
from keras.src.backend.config import backend
from keras.src.backend import standardize_data_format
from keras.src.utils.argument_validation import standardize_tuple
from importlib import import_module
from functools import partial


class BaseSpectralConv(Layer):
    """
    https://arxiv.org/abs/2010.08895
    
    """
    def __init__(
        self,
        rank,
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
        super().__init__(name=name, **kwargs)
        self.rank = rank
        self.filters = filters
        self.modes = standardize_tuple(modes, rank, name="modes")
        self.use_bias = use_bias
        self.kernel_initializer = initializers.get(kernel_initializer)
        self.bias_initializer = initializers.get(bias_initializer)
        self.kernel_regularizer = regularizers.get(kernel_regularizer)
        self.bias_regularizer = regularizers.get(bias_regularizer)
        self.kernel_constraint = constraints.get(kernel_constraint)
        self.bias_constraint = constraints.get(bias_constraint)
        self.data_format = standardize_data_format(data_format)

        fft_module = import_module(name="....ops.fft", package=__package__)
        self.rfft_fn = getattr(fft_module, "rfft" if self.rank == 1 else f"rfft{self.rank}")
        self.irfft_fn = getattr(fft_module, "irfft" if self.rank == 1 else f"irfft{self.rank}")

        # checks
        if self.filters is not None and self.filters <= 0:
            raise ValueError(
                "Invalid value for argument `filters`. Expected a strictly "
                f"positive value. Received filters={self.filters}."
            )
        
        if not all(self.modes):
            raise ValueError(
                "The argument `modes` cannot contain 0. Received "
                f"modes={self.modes}."
            )
        
    def build(self, input_shape):
        if self.built:
            return

        # get data axes
        axes = list(range(len(input_shape)))

        if self.data_format == "channels_last":
            channel_axis = -1
            input_channel = input_shape[-1]

            # if data format is `"channels_last"`, we have to transpose in order to apply the rfft and irfft along the last axes
            transpose_axes = axes.copy()
            inverse_transpose_axes = axes.copy()

            transpose_axes.insert(1, transpose_axes.pop(-1))
            inverse_transpose_axes.append(inverse_transpose_axes.pop(1))

            self.transpose = partial(ops.transpose, axes=transpose_axes)
            self.inverse_transpose = partial(ops.transpose, axes=inverse_transpose_axes)

        else:
            # NOTE this does not matter too much since currently the layer is restricted to use `"channels_last"` data format!
            channel_axis = 1
            input_channel = input_shape[1]

            # if data format is already `"channels_first"`, we do not have to transpose in order to apply the rfft and irfft
            self.transpose = lambda x: x
            self.inverse_transpose = lambda x: x

        # check pad with
        self.pad_width = (
                (0, 0),
                (0, 0), 
                *[(0, s // 2 + 1 - m if i == (len(self.modes) - 1) else s - m) for i, (m, s) in enumerate(zip(self.modes, input_shape[(1 if self.data_format == "channels_last" else 2):]))]
            )
        if list(filter(lambda x: x < (0, 0), self.pad_width)):
                raise ValueError("Too many modes for input shape!")
        
        self.input_spec = InputSpec(
            min_ndim=self.rank + 2, axes={channel_axis: input_channel}
        )

        kernel_shape = (input_channel, self.filters, *self.modes)

        # define real- and imaginary weights
        self._real_kernel = self.add_weight(
            name="real_kernel",
            shape=kernel_shape,
            initializer=self.kernel_initializer,
            regularizer=self.kernel_regularizer,
            constraint=self.kernel_constraint,
            trainable=True,
            dtype=self.dtype
        )
        self._imag_kernel = self.add_weight(
            name="imag_kernel",
            shape=kernel_shape,
            initializer=self.kernel_initializer,
            regularizer=self.kernel_regularizer,
            constraint=self.kernel_constraint,
            trainable=True,
            dtype=self.dtype
        )

        if self.use_bias:
            self._real_bias = self.add_weight(
                name="bias",
                shape=(self.filters,), 
                initializer=self.bias_initializer,
                regularizer=self.bias_regularizer,
                constraint=self.bias_constraint,
                trainable=True,
                dtype=self.dtype
            )
            self._imag_bias = self.add_weight(
                name="bias",
                shape=(self.filters,), 
                initializer=self.bias_initializer,
                regularizer=self.bias_regularizer,
                constraint=self.bias_constraint,
                trainable=True,
                dtype=self.dtype
            )
        else:
            self._real_bias = None
            self._imag_bias = None

        """
        The layer operates in the complex Fourier space.
        Here, it is always `data_format="channels_first"`, such that the RFFT can be applied along the last axis or axes.

        Now, we need a slice object to truncate the mode / reduce the complex data to the relevant modes.
        The first two dimensions are the batch and the channel/filters. Then come the modes.

        In 1-D, the RFFT output is just `[0, *positive_freqs]`, shape is `(batch, channels, n // 2 + 1)`.

        In 2-D, we have a 2-D output with shape `(batch, channels, n, n // 2 + 1)`,
        because we have only positive frequencies in `x` but the full spectrum in `y`.

        we can apply an fftshift along the first feature dimension, which would make things way easier!
        In `y`-direction, we will then have `[*negative_freqs, 0, *positive_freqs]`.

        Note that the modes have to be doubled in order to see `m` positive and negative modes!

        """
        feature_axes = axes.copy()
        feature_axes.pop(0)  # remove batch dimension
        feature_axes.pop(channel_axis)  # -1 if self.data_format == "channels_last" else 1)  # remove channel dimension

        self.feature_dims = tuple(input_shape[a] for a in feature_axes)

        # derive rfft shift arguments using `ops.roll`
        # shift have to be (m // 2 for m in modes) for all modes but the last
        # axis have to be all feature axes except for the last!
        _truncation_shifts = [m // 2 for m in self.modes]
        _truncation_shifts.pop(-1)  # remove last since there is no shift in RFFTN along the last axis
        self._truncation_shifts = tuple(_truncation_shifts)

        shift_axes = feature_axes.copy()
        shift_axes.pop(-1)  # remove last axis
        if self.data_format == "channels_last":
            shift_axes = [a + 1 for a in shift_axes]
        self.shift_axes = tuple(shift_axes)
        
        self.mode_truncation_slice = tuple([slice(None), slice(None), *[slice(None, m) for m in self.modes]])

        # declare einsum operation to apply weights
        einsum_dim = "".join([d for _, d in zip(self.modes, ["X", "Y", "Z"])])  # einsum dimensions are just letters for each mode, i.e., "XY" for modes=(8, 16)
        self.einsum_op_forward = f"bi{einsum_dim},io{einsum_dim}->bo{einsum_dim}"
        self.einsum_op_bias = f"bo{einsum_dim},o->bo{einsum_dim}"

        if backend() == "tensorflow":
            # Backpropagation with `tensorflow` backend is a bit cumbersome and requires the exact gradient flow.
            # Therefore, we must declare additional `einsum_ops`.
            self.einsum_op_backprop_weights = f"bo{einsum_dim},bi{einsum_dim}->io{einsum_dim}"
            self.einsum_op_backprop_x = f"bo{einsum_dim},io{einsum_dim}->bi{einsum_dim}"
            self.einsum_op_backprop_bias = f"bo{einsum_dim}->o"  # sum over all axis except output channels

        self.built = True

    def rfft(self, x):
        """
        Performs fast Fourier transform on the real-valued `inputs`.
        
        Parameters
        ----------
        inputs : KerasTensor
            Real-valued input tensor.
        
        Returns
        -------
        (y_real, y_imag) : (KerasTensor, KerasTensor)
            Real- and imaginary part of fast Fourier tranform applied to `inputs`.

        Notes
        -----
        `inputs` must be of shape `(batch, channels, *features)`.

        """
        
        x = self.transpose(x)
        x_real, x_imag = self.rfft_fn(x)

        # # scale outputs for numerical stability in Fourier space
        # x_real /= self.rfft_scaling
        # x_imag /= self.rfft_scaling

        return x_real, x_imag
    
    def irfft(self, inputs):
        """
        Performs inverse fast Fourier transform on the `inputs`.
        
        Parameters
        ----------
        inputs : tuple
            Tuple of `KerasTensor` (real and imaginary part).
        
        Returns
        -------
        outputs : KerasTensor
            Real-valued output of inverse fast Fourier transform applied to `inputs`.

        Notes
        -----
        `inputs` must be of shape `((batch, channels, *features), (batch, channels, *features))`.

        """

        x_real, x_imag = inputs
        y_real = self.irfft_fn((x_real, x_imag))

        # # scale back to "normal" scale
        # y_real *= self.rfft_scaling

        return self.inverse_transpose(y_real)

    def truncation_shift(self, inputs, inverse=False):
        """
        Shifts the Fourier transformed data about `modes` in all directions except `x`.

        Parameters
        ----------
        inputs : KerasTensor
            Real-valued input tensor.
        inverse : bool, optional
            Whether to invert the shift that was applied by calling `truncation_shift` once.
            Defaults to `False`.

        shifted_inputs : KerasTensor
            Shifted version of `inputs`

        """

        if self.rank == 1:
            # if `self.rank==1`, we do not have to shift the inputs!
            return inputs
        
        truncation_shifts = tuple([-s for s in self._truncation_shifts]) if inverse else self._truncation_shifts

        return ops.roll(inputs, shift=truncation_shifts, axis=self.shift_axes)
    
    def call(self, inputs):
        """
        Forward (and backprop) of BaseSpectralConv layer

        The layer first applies a RFFT, truncates the data such that only `self.modes` remain,
        applies the weights, pads the truncated data to match its initial shape.
        The padded data is then transformed using an IRFFT call.

        Since the RFFT and IRFFT are applied along the last axes by default,
        the `inputs` are always transposed to `data_format="channels_first"`,
        and the `outputs` are eventually transformed back to the initial `data_format`.

        Tensorflow can now handle the RFFT and IRFFT calls.
        Hence, the backprop has to be explicitly defined here.
        Thus, when using `backend()="tensorflow"`, this function returns both,
        the output of the spectral convolution `y` and the gradient function `grad`.
        
        Parameters
        ----------
        inputs : KerasTensor
            Input to `SpectralConv1D` layer.

        Returns
        -------
        y | (y, grad) : KerasTensor | (KerasTensor, callable)
            If Tensorflow backend is used, the function returns a tuple of the output of spectral convolution `y` and the gradient `grad`.
            If JAX backend is used, this function returns only the output of the spectral conv `y`

        Notes
        -----
        Since Keras does not have native support for complex dtypes,
        the real- and imaginary parts are handled as two real-valued tensors of `self.dtype`.
        Hence, there are two real-valued weights, `self._real_kernel` and `self._imag_kernel`,
        which are applied to the respective inputs.
        The bias is shared among real- and imaginary parts.

        """

        if backend() == "tensorflow":
            """

            Parameters
            ----------
            inputs : KerasTensor
                Input to `SpectralConv1D` layer.

            Returns
            -------
            (y, grad) : (KerasTensor, callable)
                Tuple of the output of `SpectralConv1D` and the gradient.

            """

            @ops.custom_gradient
            def forward(inputs):
                """
                Custom gradient for `tensorflow` backend
            
                Parameters
                ----------
                inputs : KerasTensor
                    Input to `SpectralConv1D` layer.

                Returns
                -------
                (y, grad) : (KerasTensor, callable)
                    Tuple of the output of `SpectralConv1D` and the gradient.
                    
                """
                
                # forward pass, input shape = (None, *x, ch_in)
                x_real, x_imag = self.rfft(inputs)  # (None, ch_in, *x)

                # apply fft shift
                x_real = self.truncation_shift(x_real)  # (None, ch_in, *x)
                x_imag = self.truncation_shift(x_imag)  # (None, ch_in, *x)

                # reduce to relevant modes
                x_real_truncated = x_real[self.mode_truncation_slice]  # (None, ch_in, *m)
                x_imag_truncated = x_imag[self.mode_truncation_slice]  # (None, ch_in, *m)

                # apply weights
                y_real_truncated = ops.einsum(self.einsum_op_forward, x_real_truncated, self._real_kernel) - ops.einsum(self.einsum_op_forward, x_imag_truncated, self._imag_kernel)  # (None, ch_out, *m)
                y_imag_truncated = ops.einsum(self.einsum_op_forward, x_imag_truncated, self._real_kernel) + ops.einsum(self.einsum_op_forward, x_real_truncated, self._imag_kernel)  # (None, ch_out, *m)

                # add bias
                if self.use_bias:
                    y_real_truncated = ops.einsum(self.einsum_op_bias, y_real_truncated, self._real_bias)  # (None, ch_out, *m)
                    y_imag_truncated = ops.einsum(self.einsum_op_bias, y_imag_truncated, self._imag_bias)  # (None, ch_out, *m)

                # pad to initial size
                y_real = ops.pad(y_real_truncated, pad_width=self.pad_width)  # (None, ch_out, *x)
                y_imag = ops.pad(y_imag_truncated, pad_width=self.pad_width)  # (None, ch_out, *x)

                # apply ifft shift
                y_real = self.truncation_shift(y_real, inverse=True)  # (None, ch_out, *x)
                y_imag = self.truncation_shift(y_imag, inverse=True)  # (None, ch_out, *x)

                # reconstruct y via irfft
                y = self.irfft((y_real, y_imag))  # (None, *x, ch_out)

                def backprop(dy, variables=None):
                    """
                    Backpropagation through the `SpectralConv1D` layer

                    Parameters
                    ----------
                    dy : KerasTensor
                        Gradient of `y`.
                    variables : list, optional
                        List of variables.
                        Defaults to `None`

                    Returns
                    -------
                    (dx, dw) : (KerasTensor, list)
                        Tuple of the gradient of `x` and a list containing the gradients of the weights.
                    
                    """

                    # input shape (None, *x, ch_out)
                    # get real and imaginary part via rfft
                    dy_real, dy_imag = self.rfft(dy)  # (None, ch_out, *x)
                    
                    # apply fft shift
                    dy_real = self.truncation_shift(dy_real)  # (None, ch_out, *x)
                    dy_imag = self.truncation_shift(dy_imag)  # (None, ch_out, *x)

                    # reduce to relevant modes
                    dy_real_truncated = dy_real[self.mode_truncation_slice]  # (None, ch_out, *m)
                    dy_imag_truncated = dy_imag[self.mode_truncation_slice]  # (None, ch_out, *m)

                    # compute gradients for weights
                    dw_real = ops.einsum(self.einsum_op_backprop_weights, dy_real_truncated, x_real_truncated) + ops.einsum(self.einsum_op_backprop_weights, dy_imag_truncated, x_imag_truncated)  # (None, ch_out, *m)
                    dw_imag = ops.einsum(self.einsum_op_backprop_weights, dy_imag_truncated, x_real_truncated) - ops.einsum(self.einsum_op_backprop_weights, dy_real_truncated, x_imag_truncated)  # (None, ch_out, *m)

                    if self.use_bias:
                        # compute gradients for bias
                        db_real = ops.einsum(self.einsum_op_backprop_bias, dy_real_truncated)  # (None, ch_out, *m)
                        db_imag = ops.einsum(self.einsum_op_backprop_bias, dy_imag_truncated)  # (None, ch_out, *m)

                    # compute gradient for inputs
                    dx_real_truncated = ops.einsum(self.einsum_op_backprop_x, dy_real_truncated, self._real_kernel) + ops.einsum(self.einsum_op_backprop_x, dy_imag_truncated, self._imag_kernel)  # (None, ch_in, *m)
                    dx_imag_truncated = ops.einsum(self.einsum_op_backprop_x, dy_imag_truncated, self._real_kernel) - ops.einsum(self.einsum_op_backprop_x, dy_real_truncated, self._imag_kernel)  # (None, ch_in, *m)

                    # pad to initial size
                    dx_real = ops.pad(dx_real_truncated, pad_width=self.pad_width)  # (None, ch_in, *x)
                    dx_imag = ops.pad(dx_imag_truncated, pad_width=self.pad_width)  # (None, ch_in, *x)

                    # apply ifft shift
                    dx_real = self.truncation_shift(dx_real, inverse=True)  # (None, ch_in, *x)
                    dx_imag = self.truncation_shift(dx_imag, inverse=True)  # (None, ch_in, *x)

                    # apply irfft
                    dx = self.irfft((dx_real, dx_imag))  # (None, *x, ch_in)
                    
                    if self.use_bias:
                        grads = [db_real, db_imag, dw_real, dw_imag]
                    else:
                        grads = [dw_real, dw_imag]
                    
                    return dx, grads

                return y, backprop
                
            return forward(inputs)

        if backend() == "jax":
            """
            
            Parameters
            ----------
            inputs : KerasTensor
                Input to `SpectralConv1D` layer.

            Returns
            -------
            y : KerasTensor
                The output of `SpectralConv1D`.

            """

            # forward pass, input shape = (None, *x, ch_in)
            x_real, x_imag = self.rfft(inputs)  # (None, ch_in, *x)

            # apply fft shift
            x_real = self.truncation_shift(x_real)  # (None, ch_in, *x)
            x_imag = self.truncation_shift(x_imag)  # (None, ch_in, *x)

            # reduce to relevant modes
            x_real_truncated = x_real[self.mode_truncation_slice]  # (None, ch_in, *m)
            x_imag_truncated = x_imag[self.mode_truncation_slice]  # (None, ch_in, *m)

            # apply weights
            y_real_truncated = ops.einsum(self.einsum_op_forward, x_real_truncated, self._real_kernel) - ops.einsum(self.einsum_op_forward, x_imag_truncated, self._imag_kernel)  # (None, ch_out, *m)
            y_imag_truncated = ops.einsum(self.einsum_op_forward, x_imag_truncated, self._real_kernel) + ops.einsum(self.einsum_op_forward, x_real_truncated, self._imag_kernel)  # (None, ch_out, *m)

            # add bias
            if self.use_bias:
                y_real_truncated = ops.einsum(self.einsum_op_bias, y_real_truncated, self._real_bias)  # (None, ch_out, *m)
                y_imag_truncated = ops.einsum(self.einsum_op_bias, y_imag_truncated, self._imag_bias)  # (None, ch_out, *m)

            # pad to initial size
            y_real = ops.pad(y_real_truncated, pad_width=self.pad_width)  # (None, ch_out, *x)
            y_imag = ops.pad(y_imag_truncated, pad_width=self.pad_width)  # (None, ch_out, *x)

            # apply ifft shift
            y_real = self.truncation_shift(y_real, inverse=True)  # (None, ch_out, *x)
            y_imag = self.truncation_shift(y_imag, inverse=True)  # (None, ch_out, *x)

            # reconstruct y via irfft
            y = self.irfft((y_real, y_imag))  # (None, *x, ch_out)

            return y

        raise NotImplementedError(f"The call method is only implemented for keras backends `'tensorflow'` and `'jax'`")

    def compute_output_shape(self, input_shape):
        """
        Compute output shape of `BaseSpectralConv`

        Parameters
        ----------
        input_shape : tuple
            Input shape.

        Returns
        -------
        output_shape : tuple
            Output shape.

        """

        input_shape: list = list(input_shape)
        channel_axis = -1 if self.data_format == 'channels_last' else 1

        input_shape[channel_axis] = self.filters
        return tuple(input_shape)

    def get_config(self):
        """
        Get config method.
        Required for serialization.

        Returns
        -------
        config : dict
            Dictionary with the configuration of `BaseSpectralConv`.

        Notes
        -----
        The `config` does not contain the `self.rank` parameter,
        which is not required when the class is subclassed with hard-coded `rank`.

        """
        
        config = super().get_config()
        config.update({
            "filters": self.filters,
            "modes": self.modes,
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
        """
        Necessary for Keras deserialization

        Parameters
        ----------
        cls : BasBaseSpectralConvFCN
            The `BaseSpectralConv` class.
        config : dict
            Dictionary with the layer configuration.

        Returns
        -------
        cls : BaseSpectralConv
            Instance of `BaseSpectralConv` from `config`.
            
        """

        kernel_initializer_cfg = config.pop("kernel_initialzer")
        bias_initializer_cfg = config.pop("bias_initialzer")
        kernel_constraint_cfg = config.pop("kernel_constraint")
        bias_constraint_cfg = config.pop("bias_constraint")
        kernel_regularizer_cfg = config.pop("kernel_regularizer")
        bias_regularizer_cfg = config.pop("bias_regularizer")

        config.update({
            "kernel_initializer": initializers.deserialize(kernel_initializer_cfg),
            "bias_initializer": initializers.deserialize(bias_initializer_cfg),
            "kernel_constraint": constraints.deserialize(kernel_constraint_cfg),
            "bias_constraint": constraints.deserialize(bias_constraint_cfg),
            "kernel_regularizer": regularizers.deserialize(kernel_regularizer_cfg),
            "bias_regularizer": regularizers.deserialize(bias_regularizer_cfg)
        })

        return cls(**config)
