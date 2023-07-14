import tensorflow as tf
from tensorflow.keras.metrics import RootMeanSquaredError as TF_RMSE

from calotron.metrics.BaseMetric import BaseMetric


class RootMeanSquaredError(BaseMetric):
    def __init__(self, name="rmse", dtype=None, **kwargs):
        super().__init__(name, dtype, **kwargs)
        self._rmse = TF_RMSE(name=name, dtype=dtype)

    def update_state(self, y_true, y_pred, sample_weight=None):
        weights = self._prepare_weights(sample_weight)
        state = self._rmse(y_true, y_pred, sample_weight=weights)
        self._metric_values.assign(state)
