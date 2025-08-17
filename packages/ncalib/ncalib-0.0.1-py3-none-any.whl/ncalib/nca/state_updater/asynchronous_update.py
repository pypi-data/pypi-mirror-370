from typing import Any

import torch

from ncalib.nca.state_updater import NCA_StateUpdater


class AsynchronousUpdate(NCA_StateUpdater):
    def __init__(self, *, update_probability: float = 0.5):
        super().__init__()
        self.update_probability = update_probability

    def forward(
            self,
            state: torch.Tensor,
            delta_state: torch.Tensor,
            **kwargs
    ) -> tuple[torch.Tensor, torch.Tensor]:
        n, c, w, h = delta_state.shape

        # Create random Mask
        random_mask = torch.rand((n, 1, w, h), device=delta_state.device)
        random_mask = random_mask < self.update_probability

        # State Update
        next_delta = delta_state * random_mask
        return state, next_delta

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["update_probability"] = self.update_probability
        return cfg
