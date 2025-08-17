from typing import Any, Optional

import torch

from ncalib.nca.state_updater import NCA_StateUpdater
from ncalib.utils.torch_helper import update_part_of_state
from ncalib.utils.utils import slice_to_config


class SimpleStateUpdater(NCA_StateUpdater):
    def __init__(self, *, channels: slice = slice(None, None), scaling: float = 1., delta_channels=None):
        super().__init__()
        self.scaling = scaling
        self.channels = channels

        if delta_channels is None:
            delta_channels = channels

        self.delta_channels = delta_channels


    def forward(
            self,
            state: torch.Tensor,
            delta_state: torch.Tensor,
            **kwargs
    ) -> tuple[torch.Tensor, torch.Tensor]:
        new_state = state[:, self.channels] + self.scaling * delta_state[:, self.delta_channels]
        state = update_part_of_state(state, new_state, self.channels)

        return state, delta_state

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["scaling"] = self.scaling
        cfg["channels"] = slice_to_config(self.channels)
        cfg["delta_channels"] = slice_to_config(self.delta_channels)
        return cfg


class FixedStatesUpdater(NCA_StateUpdater):
    def __init__(self, fixed_channels: int | slice):
        super().__init__()
        if isinstance(fixed_channels, int):
            fixed_channels = slice(fixed_channels, fixed_channels + 1)
        self.fixed_channels = fixed_channels

    def forward(
            self,
            state: torch.Tensor,
            delta_state: torch.Tensor,
            *,
            original_state: Optional[torch.Tensor] = None,
            **kwargs
    ) -> tuple[torch.Tensor, torch.Tensor]:
        state[:, self.fixed_channels] = original_state[:, self.fixed_channels]
        return state, delta_state

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["fixed_channels"] = slice_to_config(self.fixed_channels)
        return cfg

    def required_kwargs(self) -> set[str]:
        res = super().required_kwargs()
        res.add("original_state")
        return res


