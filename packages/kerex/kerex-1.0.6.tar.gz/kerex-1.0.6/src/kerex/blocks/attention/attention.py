from keras import saving
from .base_attention import BaseAttention


@saving.register_keras_serializable(package="KerasAddon.Blocks.Attention", name="GlobalSelfAttention")
class GlobalSelfAttention(BaseAttention):
    """
    Global self-attention layer.
    
    This layer calculates the self-attention of the `query`.

    Parameters
    ----------
    num_heads : int
        Number of attention heads.
    key_dim : int
        Size of each attention head for query and key.
    value_dim : int, optional
        Size of each attention head for value.
        If this is `None`, it is set to `key_dim`.
        Defaults to `None`.
    dropout : float, optional
        Dropout probability. Defaults to 0.
    use_bias : bool, optional
        If this is set, a bias is ued. Defaults to `True`.
    output_shape : tuple, optional
        The expected shape of an output tensor, besides the batch and sequence dims.
        If not specified, projects back to the query feature dim (the query input's last dimension).
        Defaults to `None`.
    attention_axes : int, optional
        Axes over which the attention is applied.
        `None` means attention over all axes, but batch, heads, and features.
        Defaults to `None`.
    kernel_initializer : str, optional
        Initializer for dense layer kernels. Defaults to `"glorot_uniform"`.
    bias_initializer : str, optional
        Initializer for dense layer biases. Defaults to `"zeros"`.
    kernel_regularizer : str, optional
        Regularizer for dense layer kernels. Defaults to `None`.
    bias_regularizer : str, optional
        Regularizer for dense layer biases. Defaults to `None`.
    activity_regularizer : str, optional
        Regularizer for dense layer activity. Defaults to `None`.
    kernel_constraint : str, optional
        Constraint for dense layer kernels. Defaults to `None`.
    bias_constraint : str, optional
        Constraint for dense layer kernels. Defaults to `None`.
    seed : int, optional
        Optional integer to seed the dropout layer. Defaults to `None`

    Notes
    -----
    With flash attention (Keras>3.6.0), the dropout probability has to be 0.

    """

    def call(self, x, return_attention_scores=False):
        """
        Call method of GlobalSelfAttention layer

        Parameters
        ----------
        x : KerasTensor
            Tensor for which the self-attention is calculated.
        return_attention_scores : bool, optional
            If `True`, the attention scores are returned. 
            Defaults to `False`.

        Returns
        -------
        y | (y, attention_scores) : KerasTensor | (KerasTensor, KerasTensor)
            The output of the self-attention.
            If `return_attention_scores==True`, the layer additionally returns the attention scores.

        """

        attn_output = self.mha(
            query=x,
            value=x,
            key=x,
            return_attention_scores=return_attention_scores
        )
        if return_attention_scores:
            attn_output, attn_scores = attn_output

        x = self.add([x, attn_output])
        x = self.layernorm(x)

        if return_attention_scores:
            return x, attn_scores
        return x


@saving.register_keras_serializable(package="KerasAddon.Blocks.Attention", name="CausalSelfAttention")
class CausalSelfAttention(BaseAttention):
    """
    Causal self-attention layer.
    
    This layer calculates the self-attention of the `query`.

    Parameters
    ----------
    num_heads : int
        Number of attention heads.
    key_dim : int
        Size of each attention head for query and key.
    value_dim : int, optional
        Size of each attention head for value.
        If this is `None`, it is set to `key_dim`.
        Defaults to `None`.
    dropout : float, optional
        Dropout probability. Defaults to 0.
    use_bias : bool, optional
        If this is set, a bias is ued. Defaults to `True`.
    output_shape : tuple, optional
        The expected shape of an output tensor, besides the batch and sequence dims.
        If not specified, projects back to the query feature dim (the query input's last dimension).
        Defaults to `None`.
    attention_axes : int, optional
        Axes over which the attention is applied.
        `None` means attention over all axes, but batch, heads, and features.
        Defaults to `None`.
    kernel_initializer : str, optional
        Initializer for dense layer kernels. Defaults to `"glorot_uniform"`.
    bias_initializer : str, optional
        Initializer for dense layer biases. Defaults to `"zeros"`.
    kernel_regularizer : str, optional
        Regularizer for dense layer kernels. Defaults to `None`.
    bias_regularizer : str, optional
        Regularizer for dense layer biases. Defaults to `None`.
    activity_regularizer : str, optional
        Regularizer for dense layer activity. Defaults to `None`.
    kernel_constraint : str, optional
        Constraint for dense layer kernels. Defaults to `None`.
    bias_constraint : str, optional
        Constraint for dense layer kernels. Defaults to `None`.
    seed : int, optional
        Optional integer to seed the dropout layer. Defaults to `None`

    Notes
    -----
    With flash attention (Keras>3.6.0), the dropout probability has to be 0.

    """

    def call(self, x, prefix=0, prediction_step=0, return_attention_scores=False):
        """
        Call method of GlobalSelfAttention layer

        Parameters
        ----------
        x : KerasTensor
            Tensor for which the self-attention is calculated.
        prefix : int, optional
            Modifies the attention mask if `prefix>0`.
            Defaults to 0.
        prediction_step : int, optional
            Modifies the attention mask if `prediction_step>0`.
            Defaults to 0.
        return_attention_scores : bool, optional
            If `True`, the attention scores are returned. 
            Defaults to `False`.

        Returns
        -------
        y | (y, attention_scores) : KerasTensor | (KerasTensor, KerasTensor)
            The output of the self-attention.
            If `return_attention_scores==True`, the layer additionally returns the attention scores.

        """
        
        attn_output = self.mha(
            query=x,
            value=x,
            key=x,
            use_causal_mask=True,
            prefix=prefix,
            prediction_step=prediction_step,
            return_attention_scores=return_attention_scores
        )

        if return_attention_scores:
            attn_output, attn_scores = attn_output

        x = self.add([x, attn_output])
        x = self.layernorm(x)

        if return_attention_scores:
            return x, attn_scores
        return x


@saving.register_keras_serializable(package="KerasAddon.Block.Attention", name="CrossAttention")
class CrossAttention(BaseAttention):
    """
    Cross-attention layer.
    
    This layer calculates the cross-attention of the `query` and the `key`.
    The `key` represents the context that is merged with an input.

    Parameters
    ----------
    num_heads : int
        Number of attention heads.
    key_dim : int
        Size of each attention head for query and key.
    value_dim : int, optional
        Size of each attention head for value.
        If this is `None`, it is set to `key_dim`.
        Defaults to `None`.
    dropout : float, optional
        Dropout probability. Defaults to 0.
    use_bias : bool, optional
        If this is set, a bias is ued. Defaults to `True`.
    output_shape : tuple, optional
        The expected shape of an output tensor, besides the batch and sequence dims.
        If not specified, projects back to the query feature dim (the query input's last dimension).
        Defaults to `None`.
    attention_axes : int, optional
        Axes over which the attention is applied.
        `None` means attention over all axes, but batch, heads, and features.
        Defaults to `None`.
    kernel_initializer : str, optional
        Initializer for dense layer kernels. Defaults to `"glorot_uniform"`.
    bias_initializer : str, optional
        Initializer for dense layer biases. Defaults to `"zeros"`.
    kernel_regularizer : str, optional
        Regularizer for dense layer kernels. Defaults to `None`.
    bias_regularizer : str, optional
        Regularizer for dense layer biases. Defaults to `None`.
    activity_regularizer : str, optional
        Regularizer for dense layer activity. Defaults to `None`.
    kernel_constraint : str, optional
        Constraint for dense layer kernels. Defaults to `None`.
    bias_constraint : str, optional
        Constraint for dense layer kernels. Defaults to `None`.
    seed : int, optional
        Optional integer to seed the dropout layer. Defaults to `None`

    Notes
    -----
    With flash attention (Keras>3.6.0), the dropout probability has to be 0.

    """

    def call(self, x, context, return_attention_scores=False):
        """
        Call method of GlobalSelfAttention layer

        Parameters
        ----------
        x : KerasTensor
            Input tensor (query).
        context : KerasTensor
            Context for `x` to calculate the attention.
        return_attention_scores : bool, optional
            If `True`, the attention scores are returned. 
            Defaults to `False`.

        Returns
        -------
        y | (y, attention_scores) : KerasTensor | (KerasTensor, KerasTensor)
            The output of the self-attention.
            If `return_attention_scores==True`, the layer additionally returns the attention scores.

        """
        attn_output = self.mha(
            query=x,
            key=context,
            value=context,
            return_attention_scores=return_attention_scores
        )

        if return_attention_scores:
            attn_output, attn_scores = attn_output

        x = self.add([x, attn_output])
        x = self.layernorm(x)

        if return_attention_scores:
            return x, attn_scores
        return x
