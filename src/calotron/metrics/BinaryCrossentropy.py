import tensorflow as tf
from tensorflow.keras.metrics import BinaryCrossentropy as TF_BCE

from calotron.metrics.BaseMetric import BaseMetric


class BinaryCrossentropy(BaseMetric):
    def __init__(
        self, name="bce", dtype=None, from_logits=False, label_smoothing=0.0
    ) -> None:
        super().__init__(name, dtype)
        self._bce = TF_BCE(
            name=name,
            dtype=dtype,
            from_logits=from_logits,
            label_smoothing=label_smoothing,
        )

    def update_state(self, y_true, y_pred, sample_weight=None) -> None:
        weights = self._prepare_weights(sample_weight)
        state = self._bce(tf.ones_like(y_pred), y_pred, sample_weight=weights)
        self._metric_values.assign(state)
