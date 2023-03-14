import tensorflow as tf
from tensorflow.keras.losses import KLDivergence as TF_KLDivergence

from calotron.losses.BaseLoss import BaseLoss


class JSDivergence(BaseLoss):
    def __init__(self, name="js_loss") -> None:
        super().__init__(name)
        self._kl_div = TF_KLDivergence(reduction="auto")

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
        loss = self._js_div(y_true, y_pred, sample_weight=sample_weight)
        loss = tf.cast(loss, dtype=target_true.dtype)
        return -loss  # divergence maximization

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
        loss = self._js_div(y_true, y_pred, sample_weight=sample_weight)
        loss = tf.cast(loss, dtype=target_true.dtype)
        return loss  # divergence minimization

    def _js_div(self, y_true, y_pred, sample_weight=None) -> tf.Tensor:
        loss = 0.5 * self._kl_div(
            y_true, 0.5 * (y_true + y_pred), sample_weight=sample_weight
        ) + 0.5 * self._kl_div(
            y_pred, 0.5 * (y_true + y_pred), sample_weight=sample_weight
        )
        return loss
