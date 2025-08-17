from typing import Any

import torch

from ncalib.trainer.batcher.pool import PoolEvictionPolicy
from ncalib.trainer.dataset import DataSample


class LossSortEvictionPolicy(PoolEvictionPolicy):
    def __init__(self, *, logarithmic=True):
        super().__init__()
        self.logarithmic = logarithmic

    def score_batch(self, data_sample: DataSample, losses: torch.Tensor) -> torch.Tensor:
        scores = losses
        if self.logarithmic:
            scores = torch.log(scores)

        scores_min = scores.min()
        scores_max = scores.max()
        if scores_max - scores_min != 0:
            scores = (scores - scores_min) / (scores_max - scores_min)
            return scores

        return torch.zeros_like(scores)

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["logarithmic"] = self.logarithmic
        return cfg


class MeanLossEvictionPolicy(PoolEvictionPolicy):
    def __init__(self, *, logarithmic=True):
        super().__init__()
        self.logarithmic = logarithmic

    def score_batch(self, data_sample: DataSample, losses: torch.Tensor) -> torch.Tensor:
        scores = losses
        if self.logarithmic:
            scores = torch.log(scores)

        scores = torch.abs(scores - scores.mean())
        max_score = torch.max(scores)
        if max_score != 0:
            scores = scores / torch.max(scores)
        return scores

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["logarithmic"] = self.logarithmic
        return cfg
