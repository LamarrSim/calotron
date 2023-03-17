import tensorflow as tf


class BaseLoss:
    def __init__(self, name="loss") -> None:
        if not isinstance(name, str):
            raise TypeError(
                f"`name` should be a string " f"instead {type(name)} passed"
            )
        self._name = name

    def discriminator_loss(
        self,
        discriminator,
        source_true,
        target_true,
        target_pred,
        sample_weight=None,
        discriminator_training=True,
    ) -> tf.Tensor:
        raise NotImplementedError(
            "Only `BaseLoss` subclasses have the "
            "`discriminator_loss()` method implemented."
        )

    def transformer_loss(
        self,
        discriminator,
        source_true,
        target_true,
        target_pred,
        sample_weight=None,
        discriminator_training=False,
    ) -> tf.Tensor:
        raise NotImplementedError(
            "Only `BaseLoss` subclasses have the "
            "`transformer_loss()` method implemented."
        )

    @property
    def name(self) -> str:
        return self._name
