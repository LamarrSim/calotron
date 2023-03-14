import tensorflow as tf
from tensorflow.keras.losses import MeanAbsoluteError as TF_MAE

from calotron.losses.BaseLoss import BaseLoss


class MeanAbsoluteError(BaseLoss):
    def __init__(self, name="mae_loss") -> None:
        super().__init__(name)
        self._loss = TF_MAE(reduction="auto")

    def discriminator_loss(
        self,
        discriminator,
        source_true,
        target_true,
        target_pred,
        sample_weight=None,
        discriminator_training=True,
    ) -> tf.Tensor:
        y_true = discriminator(target_true, training=discriminator_training)
        y_pred = discriminator(target_pred, training=discriminator_training)
        loss = self._loss(y_true, y_pred, sample_weight=sample_weight)
        loss = tf.cast(loss, dtype=target_true.dtype)
        return -loss  # error maximization

    def transformer_loss(
        self,
        discriminator,
        source_true,
        target_true,
        target_pred,
        sample_weight=None,
        discriminator_training=False,
    ) -> tf.Tensor:
        y_true = discriminator(target_true, training=discriminator_training)
        y_pred = discriminator(target_pred, training=discriminator_training)
        loss = self._loss(y_true, y_pred, sample_weight=sample_weight)
        loss = tf.cast(loss, dtype=target_true.dtype)
        return loss  # error minimization
