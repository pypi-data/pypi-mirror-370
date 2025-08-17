import abc
from typing import Optional

import torch

from ncalib.utils.defaults import DEFAULT_DEVICE
from ncalib.utils.utils import NCA_Base


class NCA_SeedFactory(NCA_Base, abc.ABC):
    def __init__(
            self,
            width: int = 64,
            channels: int = 16,
            height: Optional[int] = None,
    ):
        super().__init__()
        self.width = width
        self.height = height if height is not None else width
        self.channels = channels

    @abc.abstractmethod
    def __call__(self, n: int = 1, *, device=DEFAULT_DEVICE) -> torch.Tensor:
        pass

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["width"] = self.width
        cfg["height"] = self.height
        cfg["channels"] = self.channels
        return cfg


class NCA_SeedPostprocessing(NCA_SeedFactory, abc.ABC):
    def __init__(self, seed_factory: NCA_SeedFactory):
        super().__init__()
        self.base_seed_factory = seed_factory

    def __call__(self, n: int = 1, *, device=DEFAULT_DEVICE):
        seed = self.base_seed_factory(n, device=device)
        return self.update_seed(seed)

    @abc.abstractmethod
    def update_seed(self, original_seed: torch.Tensor) -> torch.Tensor:
        pass

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["seed_factory"] = self.base_seed_factory
        return cfg
