import tensorflow as tf

from calotron.models import Transformer


class Simulator(tf.Module):
    def __init__(self, transformer, start_token, name=None) -> None:
        super().__init__(name=name)
        if not isinstance(transformer, Transformer):
            raise TypeError(
                "`transformer` should be a calotron's `Transformer`, "
                f"instead {type(transformer)} passed"
            )
        self._transformer = transformer
        self._dtype = self._transformer.dtype

        start_token = tf.convert_to_tensor(start_token, dtype=self._dtype)
        assert isinstance(start_token, tf.Tensor)
        if len(start_token.shape) > 2:
            raise ValueError(
                "`start_token` shape should match with "
                "(batch_size, target_depth) or (target_depth,)"
            )
        if start_token.shape[-1] != self._transformer.output_depth:
            raise ValueError(
                "`start_token` elements should match with "
                "the `transformer` output depth, instead "
                f"{start_token.shape[-1]} passed"
            )
        self._start_token = start_token

    def __call__(self, source, max_length) -> tf.Tensor:
        source = tf.convert_to_tensor(source, dtype=self._dtype)
        assert isinstance(source, tf.Tensor)
        assert max_length >= 1
        max_length = int(max_length)

        if len(self._start_token.shape) == 1:
            start_token = self._start_token[None, :]
            start_token = tf.tile(start_token, (tf.shape(source)[0], 1))
        else:
            if source.shape[0] != self._start_token.shape[0]:
                raise ValueError(
                    "`source` and `start_token` batch-sizes should "
                    f"match, instead {tf.shape(source)[0]} and "
                    f"{self._start_token.shape[0]} passed"
                )
            else:
                start_token = tf.identity(self._start_token)

        ta_target = tf.TensorArray(dtype=self._dtype, size=0, dynamic_size=True)
        ta_target = ta_target.write(index=0, value=start_token)
        for i in tf.range(max_length):
            out_target = tf.transpose(ta_target.stack(), perm=[1, 0, 2])
            predictions = self.transformer((source, out_target), training=False)
            ta_target = ta_target.write(index=i + 1, value=predictions[:, -1, :])

        out_target = tf.transpose(ta_target.stack(), perm=[1, 0, 2])
        return out_target[:, 1:, :]

    @property
    def transformer(self) -> Transformer:
        return self._transformer

    @property
    def start_token(self) -> tf.Tensor:
        return self._start_token
