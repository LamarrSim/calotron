import tensorflow as tf
from tensorflow.keras.metrics import MeanAbsoluteError as TF_MAE

from calotron.metrics.BaseMetric import BaseMetric


class MeanAbsoluteError(BaseMetric):
    def __init__(self, name="mae", dtype=None, **kwargs) -> None:
        super().__init__(name, dtype, **kwargs)
        self._mae = TF_MAE(name=name, dtype=dtype)

    def update_state(self, y_true, y_pred, sample_weight=None) -> None:
        weights = self._prepare_weights(sample_weight)
        state = self._mae(y_true, y_pred, sample_weight=weights)
        self._metric_values.assign(state)
