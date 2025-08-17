from typing import Any, Optional

import torch
from jaxtyping import Float

from ncalib.trainer.loss_function import NamedLossFunction
from ncalib.utils.utils import slice_to_config


class OverflowLoss(NamedLossFunction):
    # https://colab.research.google.com/github/google-research/self-organising-systems/blob/master/isotropic_nca/blogpost_isonca_single_seed_pytorch.ipynb#scrollTo=3pxjdESnYlIC&line=1&uniqifier=1
    def __init__(
            self,
            channels: slice = slice(None, None, None),
            *,
            min: Optional[float] = None,
            max: Optional[float] = None,
            loss_name="OverflowLoss",
    ):
        super().__init__(loss_name=loss_name)
        self.channels = channels
        self.min = min
        self.max = max

    def _calculate_loss(
            self,
            state_progression: Float[torch.Tensor, "N B C W H"],
            target: Float[torch.Tensor, "B ..."],
            **kwargs
    ) -> Float[torch.Tensor, "B"]:
        clamped = torch.clamp(state_progression[:, :, self.channels], min=self.min, max=self.max)
        diff = state_progression[:, :, self.channels] - clamped
        return diff.square().sum(dim=[0, 2, 3, 4])

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["channels"] = slice_to_config(self.channels)
        cfg["min"] = self.min
        cfg["max"] = self.max
        return cfg


class DiffLoss(NamedLossFunction):
    # https://colab.research.google.com/github/google-research/self-organising-systems/blob/master/isotropic_nca/blogpost_isonca_single_seed_pytorch.ipynb#scrollTo=3pxjdESnYlIC&line=1&uniqifier=1
    def __init__(
            self,
            channels: slice = slice(None, None, None),
            *,
            loss_name="DiffLoss",
    ):
        super().__init__(loss_name)
        self.channels = channels

    def _calculate_loss(
            self,
            state_progression: Float[torch.Tensor, "N B C W H"],
            target: Float[torch.Tensor, "B ..."],
            **kwargs
    ) -> Float[torch.Tensor, "B"]:
        diffs = state_progression[1:, self.channels] - state_progression[:-1, self.channels]
        return diffs.abs().mean(dim=[2, 3, 4]).sum(dim=0)

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["channels"] = slice_to_config(self.channels)
        return cfg
