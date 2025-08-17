import abc
from typing import Any, Iterable

import torch

from ncalib.trainer.dataset import DataSample
from ncalib.utils.utils import NCA_Base


class PoolEvictionPolicy(NCA_Base, abc.ABC):
    def __init__(self, weight: float = 1):
        super().__init__()
        self.weight = weight

    def __call__(self, data_sample: DataSample, losses: torch.Tensor):
        return self.weight * self.score_batch(data_sample, losses)

    def __add__(self, other: "PoolEvictionPolicy") -> "CombinedPoolEvictionPolicy":
        # Prepare each policy so that each is an iterable of simple policies
        if isinstance(self, CombinedPoolEvictionPolicy):
            policies1 = tuple(self.policies)
        else:
            policies1 = (self,)

        if isinstance(other, CombinedPoolEvictionPolicy):
            policies2 = tuple(other.policies)
        else:
            policies2 = (other,)

        # Combine Loss function
        return CombinedPoolEvictionPolicy(policies1 + policies2)

    def __mul__(self, value: float) -> "PoolEvictionPolicy":
        self.weight *= value
        return self

    def __rmul__(self, value) -> "PoolEvictionPolicy":
        return self.__mul__(value)

    @abc.abstractmethod
    def score_batch(self, data_sample: DataSample, losses: torch.Tensor) -> torch.Tensor:
        """
        Calculates scores between 0 and 1 for each sample
        :param data_sample:
        :param losses:
        :return:
        """
        pass

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["weight"] = self.weight
        return cfg


class CombinedPoolEvictionPolicy(PoolEvictionPolicy):
    def __init__(self, policies: Iterable[PoolEvictionPolicy], weight=1):
        super().__init__(weight=weight)
        self.policies = tuple(policies)

    def score_batch(self, data_sample: DataSample, losses: torch.Tensor) -> torch.Tensor:
        result = self.policies[0](data_sample, losses)
        for policy in self.policies[1:]:
            result += policy(data_sample, losses)

        return result

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["policies"] = [policy.to_config_dict() for policy in self.policies]
        return cfg
