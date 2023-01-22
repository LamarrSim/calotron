import pytest
import numpy as np
import tensorflow as tf


np.random.seed(42)
chunk_size = int(1e4)
y_true = None
y_pred = np.random.uniform(0.0, 1.0, size=(chunk_size,))


@pytest.fixture
def metric():
  from calotron.metrics import Accuracy
  metric_ = Accuracy(name="accuracy",
                     dtype=None,
                     threshold=0.5)
  return metric_


###########################################################################


def test_metric_configuration(metric):
  from calotron.metrics import Accuracy
  assert isinstance(metric, Accuracy)
  assert isinstance(metric.name, str)


def test_metric_use_no_weights(metric):
  metric.update_state(y_true, y_pred, sample_weight=None)
  res = metric.result().numpy()
  assert (res > 0.48) and (res < 0.52)


def test_metric_use_with_weights(metric):
  metric.update_state(y_true, y_pred, sample_weight=1.0)
  res = metric.result().numpy()
  assert (res > 0.48) and (res < 0.52)
