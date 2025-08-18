from keras import callbacks
from keras.src import backend
from keras import ops
from keras.src.utils import io_utils


class LRCSVLogger(callbacks.CSVLogger):
    """
    Learning rate is logged alongside metrics and loss
    """
    def on_epoch_end(self, epoch, logs=None):
        try:
            current_lr = self.model.optimizer._get_current_learning_rate()  # returns current learning rate
            logs["learning_rate"] = float(
            backend.convert_to_numpy(current_lr)
        )
        except AttributeError:
            pass
        
        return super().on_epoch_end(epoch, logs)
    

class WeightNormLogger(callbacks.CSVLogger):
    def on_train_begin(self, logs=None):
        super().on_train_begin(logs)
        self.initial_norm = self.get_norm_weights()

    def on_train_batch_end(self, batch, logs=None):
        logs = {}

        # write to logs
        logs["weights_norm"] = self.get_norm_weights()
        logs["relative_change"] = logs["weights_norm"] / self.initial_norm
        return super().on_epoch_end(batch, logs)
    
    def get_norm_weights(self) -> float:
        # get model weights
        weights: list = self.model.get_weights()
        
        # flatten list and get norm over all weights
        flat_norm = [ops.linalg.norm(ops.ravel(w)) for w in weights]
        norm = ops.linalg.norm(flat_norm)
        return float(backend.convert_to_numpy(norm))


class ThresholdEarlyStopping(callbacks.EarlyStopping):
    """
    ThresholdEarlyStopping Callback

    This callback adds a threshold parameter to the EarlyStopping callback.
    If threshold is set, the early stopping will not be active until the monitored loss falls below the threshold.

    Parameters
    ----------
    monitor : str, optional
        Quantity to be monitored. Defaults to `"val_loss"`.
    min_delta : float, optional
        Minimum change in the monitored quantity to qualify as an improvement, 
        i.e. an absolute change of less than min_delta, will count as no improvement. 
        Defaults to `0`.
    patience : int, optional
        Number of epochs with no improvement after which training will be stopped. Defaults to `0`.
    verbose : int, optional {0, 1}
        Verbosity mode. 
        Mode 0 is silent, and mode 1 displays messages when the callback takes an action. 
        Defaults to `0`.
    mode : str, optional {"auto", "min", "max"}
        In `min` mode, training will stop when the quantity monitored has stopped decreasing; 
        in `"max"` mode it will stop when the quantity monitored has stopped increasing; 
        in `"auto"` mode, the direction is automatically inferred from the name of the monitored quantity. 
        Defaults to `"auto"`.
    threshold : float, optional
        Threshold value for the monitored quantity.
        If not `None`, the callback will not be active until the monitored quantity does not undercut the threshold.
        Defaults to `None`.
    baseline : float, optional
        Baseline value for the monitored quantity. 
        If not `None`, training will stop if the model doesn't show improvement over the baseline. 
        Defaults to `None`.
    restore_best_weights: bool, optional
        Whether to restore model weights from the epoch with the best value of the monitored quantity. 
        If `False`, the model weights obtained at the last step of training are used. 
        An epoch will be restored regardless of the performance relative to the `baseline`. 
        If no epoch improves on `baseline`, training will run for `patience` epochs 
        and restore weights from the best epoch in that set. 
        Defaults to `False`.
    start_from_epoch: int, optional
        Number of epochs to wait before starting to monitor improvement. 
        This allows for a warm-up period in which no improvement is expected and thus training will not be stopped.
        Defaults to `0`.

    """
    def __init__(
        self, 
        monitor="val_loss",
        min_delta=0, 
        patience=0, 
        verbose=0, 
        mode="auto", 
        threshold=None,
        baseline=None, 
        restore_best_weights=False, 
        start_from_epoch=0
    ):
        super().__init__(monitor, min_delta, patience, verbose, mode, baseline, restore_best_weights, start_from_epoch)
        self.threshold = threshold
        self.threshold_matched_once = False

        # sanity check
        if self.baseline and self.threshold:
            if self.baseline <= self.threshold:
                raise ValueError(f"Baseline must be greater than threshold, received a baseline of{self.baseline} and a threshold of {self.threshold}.")

    def on_epoch_end(self, epoch, logs=None):
        if self.monitor_op is None:
            # Delay setup until the model's metrics are all built
            self._set_monitor_op()

        current = self.get_monitor_value(logs)
        if current is None or epoch < self.start_from_epoch:
            # If no monitor value exists or still in initial warm-up stage.
            return
        if self.restore_best_weights and self.best_weights is None:
            # If best weights were never set,
            # then the current weights are the best.
            self.best_weights = self.model.get_weights()
            self.best_epoch = epoch
        
        # check if threshold is reached. If not, return. If yes, increase wait by one and set flag to true.
        # this code will only be reached once!
        if self.threshold is not None and not self.threshold_matched_once:
            if current < self.threshold:
                self.threshold_matched_once = True
            else:
                return
    
        if self._is_improvement(current, self.best):
            self.best = current
            self.best_epoch = epoch
            if self.restore_best_weights:
                self.best_weights = self.model.get_weights()
            # Only restart wait if we beat both the baseline and our previous
            # best.
            if self.baseline is None or self._is_improvement(current, self.baseline):
                self.wait = 0
                self.threshold_matched_once = True

            return

        self.wait += 1   

        if self.wait >= self.patience and epoch > 0:
            # Patience has been exceeded: stop training
            self.stopped_epoch = epoch
            self.model.stop_training = True
