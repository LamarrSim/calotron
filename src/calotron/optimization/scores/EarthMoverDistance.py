import numpy as np

from calotron.optimization.scores.BaseScore import BaseScore


class EarthMoverDistance(BaseScore):
    def __init__(self, name="emd_score", dtype=None) -> None:
        super().__init__(name, dtype)

    def __call__(self, x_true, x_pred, bins=10, range=None) -> float:
        h_true, bins_ = np.histogram(x_true, bins=bins, range=range)
        h_pred, bins_ = np.histogram(x_pred, bins=bins_, range=None)

        h_true = h_true.astype(self._dtype) / np.sum(h_true, dtype=self._dtype)
        h_pred = h_pred.astype(self._dtype) / np.sum(h_pred, dtype=self._dtype)

        emd_scores = np.zeros(shape=(len(bins_)))
        for i in np.arange(len(emd_scores) - 1):
            emd_scores[i + 1] = h_true[i] + emd_scores[i] - h_pred[i]

        score = np.sum(np.abs(emd_scores))
        return float(score)
