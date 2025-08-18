from keras import optimizers
from keras.src import backend
from keras.src import ops
from keras import saving


@saving.register_keras_serializable(package="Kerex.Optimizers", name="AdamW")
class AdamW(optimizers.Adam):
    """
    Optimizer that implements the AdamW algorithm.
    
    "AdamW is often superior to Adam with L2 regularization because it decouples
    the weight decay from the gradient-based updates, leading to more effective 
    regularization, better generalization, and improved convergence. 
    This makes AdamW a more robust and reliable optimizer for a wide range of 
    deep learning tasks."
    (https://www.geeksforgeeks.org/why-is-adamw-often-superior-to-adam-with-l2-regularization-in-practice/)

    AdamW optimization is a stochastic gradient descent method that is based on
    adaptive estimation of first-order and second-order moments with an added
    method to decay weights per the techniques discussed in the paper,
    'Decoupled Weight Decay Regularization' by
    [Loshchilov, Hutter et al., 2019](https://arxiv.org/abs/1711.05101).

    According to
    [Kingma et al., 2014](http://arxiv.org/abs/1412.6980),
    the underying Adam method is "*computationally
    efficient, has little memory requirement, invariant to diagonal rescaling of
    gradients, and is well suited for problems that are large in terms of
    data/parameters*".

    Parameters
    ----------
    learning_rate : float | keras.optimizers.schedules.LearningRateSchedule | callable
        The learning rate or a learning rate-scheduler. Defaults to `0.001`.
    beta_1 : float | KerasTensor | callable, optional
        The exponential decay rate for the 1st moment estimates.
        Defaults to `0.9`.
    beta_2 : float | KerasTensor | callable, optional
        The exponential decay rate for the 2nd moment estimates.
        Defaults to `0.999`.
    epsilon : float, optional
        A small constant for numerical stability. This epsilon is
        "epsilon hat" in the Kingma and Ba paper (in the formula just
        before Section 2.1), not the epsilon in Algorithm 1 of the paper.
        Defaults to 1e-7.
    amsgrad : bool, optional
        Whether to apply AMSGrad variant of this algorithm
        from the paper "On the Convergence of Adam and beyond".
        Defaults to `False`.    

    Notes
    -----
    In constrast to the default Keras implementation of AdamW, the weight
    decay is decoupled from the gradient update process!

    References:
    - [Loshchilov et al., 2019](https://arxiv.org/abs/1711.05101)
    - [Kingma et al., 2014](http://arxiv.org/abs/1412.6980) for `adam`
    - [Reddi et al., 2018](https://openreview.net/pdf?id=ryQu7f-RZ) for `amsgrad`.

    """

    def __init__(
        self,
        learning_rate=0.001,
        weight_decay=0.0001,
        beta_1=0.9,
        beta_2=0.999,
        epsilon=1e-7,
        amsgrad=False,
        clipnorm=None,
        clipvalue=None,
        global_clipnorm=None,
        use_ema=False,
        ema_momentum=0.99,
        ema_overwrite_frequency=None,
        loss_scale_factor=None,
        gradient_accumulation_steps=None,
        name="adamw",
        **kwargs,
    ):
        super().__init__(
            learning_rate=learning_rate,
            beta_1=beta_1,
            beta_2=beta_2,
            epsilon=epsilon,
            amsgrad=amsgrad,
            name=name,
            weight_decay=weight_decay,
            clipnorm=clipnorm,
            clipvalue=clipvalue,
            global_clipnorm=global_clipnorm,
            use_ema=use_ema,
            ema_momentum=ema_momentum,
            ema_overwrite_frequency=ema_overwrite_frequency,
            loss_scale_factor=loss_scale_factor,
            gradient_accumulation_steps=gradient_accumulation_steps,
            **kwargs,
        )

    def apply(self, grads, trainable_variables=None):
        """
        Update traininable variables according to provided gradient values.

        Parameters
        ----------
        grads : list
            list of gradient tensors with 1:1 mapping to the list of variables the optimizer was built with.
        trainable_variables : list, optional
            can be provided on the first call to build the optimizer.

        """

        if len(grads) == 0:
            # It is possible that the grad is empty. In this case,
            # `apply_gradients` is a no-op.
            return

        if trainable_variables is None:
            if not self.built:
                raise ValueError(
                    "When passing `grads` without `variables`, the optimizer "
                    "must already be built on a list of variables. "
                    "Call `optimizer.build(trainable_variables)` first. "
                )
            if len(grads) != len(self._trainable_variables_indices):
                raise ValueError(
                    "When passing `grads` as a list of gradient tensors, the "
                    f"gradients must match `optimizer.variables` one-to-on. "
                    f"Received a list of {len(grads)} gradients, but the "
                    f"optimizer is tracking {len(self._trainable_variables)} "
                    "trainable variables."
                )
            trainable_variables = self._trainable_variables
        else:
            trainable_variables = list(trainable_variables)
            # Optionally build optimizer.
            if not self.built:
                with backend.name_scope(self.name, caller=self):
                    self.build(trainable_variables)
                self.built = True
            self._check_variables_are_known(trainable_variables)

        with backend.name_scope(self.name, caller=self):
            # Overwrite targeted variables directly with their gradients if
            # their `overwrite_with_gradient` is set.
            grads, trainable_variables = (
                self._overwrite_variables_directly_with_gradients(
                    grads, trainable_variables
                )
            )

            # Filter empty gradients.
            grads, trainable_variables = self._filter_empty_gradients(
                grads, trainable_variables
            )
            if len(list(grads)) == 0:
                return

            # Unscale gradients.
            scale = self.loss_scale_factor
            if scale is not None:
                grads = [g if g is None else g / scale for g in grads]

            # Apply gradient updates.
            self._backend_apply_gradients(grads, trainable_variables)

            # Apply weight decay after gradient updates
            if self.weight_decay is not None:
                for variable in trainable_variables:
                    if self._use_weight_decay(variable):
                        lr = ops.cast(self.learning_rate, variable.dtype)
                        wd = ops.cast(self.weight_decay, variable.dtype)
                        variable.assign(variable - variable * wd * lr)

            # Apply variable constraints after applying gradients.
            for variable in trainable_variables:
                if variable.constraint is not None:
                    variable.assign(variable.constraint(variable))

    def _apply_weight_decay(self, variables):
        """
        Overwrite default weight decay to return None as it is not correct for AdamW!

        Parameters
        ----------
        variables : list
            list of variables

        """

        return
