from typing import Optional

import torch

from ncalib.seed_factory import NCA_SeedFactory
from ncalib.utils.defaults import DEFAULT_DEVICE
from ncalib.utils.utils import slice_to_config


class IsotropicSeedFactory(NCA_SeedFactory):
    def __init__(
            self,
            width: int = 64,
            channels: int = 16,
            *,
            height: Optional[int] = None,
            angle_channel_id: int = 0,
            ignore_channels: Optional[slice] = None,
        limit_possible_values: Optional[int] = None,
    ):
        super().__init__(width=width, height=height, channels=channels)
        self.ignore_channels = ignore_channels
        self.angle_channel_id = angle_channel_id
        self.limit_possible_values = limit_possible_values

    def __call__(self, n: int = 1, *, device=DEFAULT_DEVICE) -> torch.Tensor:
        # Init with zeros
        seed = torch.zeros([n, self.channels, self.width, self.height], dtype=torch.float32, device=device)

        # Set center to 1
        mask_for_ones = torch.ones(self.channels, dtype=torch.bool)
        if self.ignore_channels is not None:
            mask_for_ones[self.ignore_channels] = False
        mask_for_ones[self.angle_channel_id] = False
        seed[:, mask_for_ones, self.width // 2, self.height // 2] = 1.0

        # Initialize random angles
        random_values = torch.rand((n, self.width, self.height))
        if self.limit_possible_values is not None:
            random_values = (random_values // (1 / self.limit_possible_values)) / self.limit_possible_values
        seed[:, self.angle_channel_id] = random_values * torch.pi * 2.0
        return seed

    @classmethod
    def for_target(cls, target: "NCA_Target", nca: "NCA", *, angle_channel_id: int = 0) -> "IsotropicSeedFactory":
        return cls(
            width=target.width,
            height=target.height,
            channels=nca.channels,
            angle_channel_id=angle_channel_id
        )

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["ignore_channels"] = slice_to_config(self.ignore_channels)
        cfg["angle_channel_id"] = self.angle_channel_id
        cfg["limit_possible_values"] = self.limit_possible_values
        return cfg
