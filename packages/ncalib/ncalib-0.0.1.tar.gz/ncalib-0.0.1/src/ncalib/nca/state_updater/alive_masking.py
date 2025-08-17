from typing import Any, Optional

import torch
import torch.nn.functional as F
from jaxtyping import Float

from ncalib.nca.state_updater import NCA_StateUpdater
from ncalib.utils.utils import slice_to_config


class AliveMasking(NCA_StateUpdater):
    def __init__(
            self,
            *,
            threshold: float = 0.1,
            max_pool_size: int = 3,
            alpha_channel: int = 3,
            ignore_channels: Optional[slice] = None
    ):
        super().__init__()
        self.threshold = threshold
        self.max_pool_size = max_pool_size

        self.alpha_channel = alpha_channel
        self.ignore_channels= ignore_channels

    def forward(
            self,
            state: Float[torch.Tensor, "B C W H"],
            delta_state: Float[torch.Tensor, "B C W H"],
            **kwargs
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        :param state: Current State of the NCA
        :param delta_state: Update for NCA
        :return: Next state of NCA
        """
        # Get Alive Mask
        max_pool = F.max_pool2d(state[:, self.alpha_channel, :, :], self.max_pool_size, stride=1, padding=self.max_pool_size // 2)
        alive = max_pool > self.threshold
        alive = torch.unsqueeze(alive, 1)
        alive = torch.repeat_interleave(alive, state.shape[1], 1)

        if self.ignore_channels is not None:
            alive[:, self.ignore_channels] = 1

        # Apply Alive Mask
        next_state = state * alive
        return next_state, delta_state

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["threshold"] = self.threshold
        cfg["max_pool_size"] = self.max_pool_size
        cfg["alpha_channel"] = self.alpha_channel
        cfg["ignore_channels"] = slice_to_config(self.ignore_channels)

        return cfg
