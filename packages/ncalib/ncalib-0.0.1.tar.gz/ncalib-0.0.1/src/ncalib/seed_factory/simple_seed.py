from typing import Optional

import torch

from ncalib.seed_factory import NCA_SeedFactory
from ncalib.utils.defaults import DEFAULT_DEVICE


class ConstantFillSeedFactory(NCA_SeedFactory):
    def __init__(
            self,
            width: int = 64,
            channels: int = 16,
            height: Optional[int] = None,
            fill_value: float = 0
    ):
        super().__init__(width=width, height=height, channels=channels)
        self.fill_value = fill_value

    def __call__(self, n: int = 1, *, device=DEFAULT_DEVICE) -> torch.Tensor:
        seed = torch.ones([n, self.channels, self.width, self.height], dtype=torch.float32, device=device)
        return seed * self.fill_value

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["fill_value"] = self.fill_value
        return cfg


class NormalSeedFactory(NCA_SeedFactory):
    def __init__(
            self,
            width: int = 64,
            channels: int = 16,
            height: Optional[int] = None,
            visible_channel: int = 3
    ):
        super().__init__(width=width, height=height, channels=channels)
        self.visible_channel = visible_channel

    def __call__(self, n: int = 1, *, device=DEFAULT_DEVICE) -> torch.Tensor:
        seed = torch.zeros([n, self.channels, self.width, self.height], dtype=torch.float32, device=device)
        seed[:, self.visible_channel:, self.width // 2, self.height // 2] = 1.0
        return seed

    @classmethod
    def for_target(cls, target: "NCA_Target", nca: "NCA") -> "NormalSeedFactory":
        return NormalSeedFactory(
            width=target.width,
            height=target.height,
            channels=nca.channels,
        )

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["visible_channel"] = self.visible_channel
        return cfg


class SpreadSeedFactory(NCA_SeedFactory):
    def __init__(
            self,
            width: int = 64,
            channels: int = 16,
            height: Optional[int] = None,
            visible_channel: int = 3,
            *,
            seed=0
    ):
        super().__init__(width=width, height=height, channels=channels)
        self.visible_channel = visible_channel
        with torch.random.fork_rng():
            torch.random.manual_seed(seed)
            self._seed = torch.rand([self.channels, self.width, self.height], dtype=torch.float32)
            self._seed[:visible_channel] = 0

    def __call__(self, n: int = 1, *, device=DEFAULT_DEVICE) -> torch.Tensor:
        seed = self._seed.clone()
        return seed.to(device).repeat([n, 1, 1, 1])

    @classmethod
    def for_target(cls, target: "NCA_Target", nca: "NCA") -> "NormalSeedFactory":
        return NormalSeedFactory(
            width=target.width,
            height=target.height,
            channels=nca.channels,
        )

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["visible_channel"] = self.visible_channel
        return cfg


