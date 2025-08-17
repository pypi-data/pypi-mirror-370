import torch

from ncalib.trainer.batcher.pool import PoolEvictionPolicy
from ncalib.trainer.dataset import DataSample


class RandomEvictionPolicy(PoolEvictionPolicy):
    def score_batch(self, data_sample: DataSample, losses: torch.Tensor) -> torch.Tensor:
        return torch.zeros_like(losses)
