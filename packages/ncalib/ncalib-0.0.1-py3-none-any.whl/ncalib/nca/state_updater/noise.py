from typing import Optional, Any

import torch

from ncalib.nca.state_updater import NCA_StateUpdater


class AddNormalNoiseStateUpdater(NCA_StateUpdater):
    def __init__(self, mu: float = 0, std: float = 0.02, *, seed: Optional[int] = None):
        super().__init__()
        self.mu = mu
        self.std = std
        self.rng = None
        self.seed = seed

    def forward(
            self,
            state: torch.Tensor,
            delta_state: torch.Tensor,
            **kwargs
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if self.rng is None:
            self.rng = torch.Generator(device=state.device)
            if self.seed is not None:
                self.rng.manual_seed(self.seed)
            else:
                self.rng.seed()
        noise = torch.normal(self.mu, self.std, delta_state.shape, generator=self.rng, device=state.device)
        return state, delta_state + noise

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["mu"] = self.mu
        cfg["std"] = self.std
        return cfg
