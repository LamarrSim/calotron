import pytest
import numpy as np
import tensorflow as tf


chunk_size = int(1e5)

X = np.c_[
  np.random.uniform(-1, 1, size=chunk_size),
  np.random.normal(0, 1, size=chunk_size),
  np.random.exponential(5, size=chunk_size)
]
Y = np.tanh(X[:,0]) + 2 * X[:,1] * X[:,2]

model = tf.keras.Sequential()
model.add(tf.keras.layers.InputLayer(input_shape=(3,)))
for units in [16, 16, 16]:
  model.add(tf.keras.layers.Dense(units, activation="relu"))
model.add(tf.keras.layers.Dense(1))

adam = tf.keras.optimizers.Adam(learning_rate=0.001)
mse = tf.keras.losses.MeanSquaredError()


@pytest.fixture
def scheduler(staircase=False):
  from calotron.callbacks.schedulers import ExponentialDecay
  sched = ExponentialDecay(optimizer=adam,
                           decay_rate=0.9,
                           decay_steps=1000,
                           staircase=staircase,
                           verbose=False)
  return sched


###########################################################################


def test_sched_configuration(scheduler):
  from calotron.callbacks.schedulers import ExponentialDecay
  assert isinstance(scheduler, ExponentialDecay)
  assert isinstance(scheduler.optimizer, tf.keras.optimizers.Optimizer)
  assert isinstance(scheduler.decay_rate, float)
  assert isinstance(scheduler.decay_steps, int)
  assert isinstance(scheduler.staircase, bool)


@pytest.mark.parametrize("staircase", [False, True])
def test_sched_use(staircase):
  from calotron.callbacks.schedulers import ExponentialDecay
  sched = ExponentialDecay(optimizer=adam,
                           decay_rate=0.9,
                           decay_steps=1000,
                           staircase=staircase,
                           verbose=True)
  model.compile(optimizer=adam, loss=mse)
  history = model.fit(X, Y, batch_size=512, epochs=10, callbacks=[sched])
  assert isinstance(sched._dtype, np.dtype)
  last_lr = float(history.history["lr"][-1])
  assert  last_lr < 0.001
