from typing import Optional, Protocol, Any

import torch
import torch.nn.functional as F
from jaxtyping import Float

from ncalib import full_class_name
from ncalib.trainer.loss_function import NamedLossFunction
from ncalib.utils.utils import slice_to_config


class _LossFnProtocol(Protocol):
    def __call__(self, state: torch.Tensor, target: torch.Tensor, reduction: Optional[str], **kwargs) -> torch.Tensor:
        pass


class _ReductionFnProtocol(Protocol):
    def __call__(self, values: torch.Tensor, *, dim: tuple[int, int, int]) -> torch.Tensor:
        pass


class ImageTargetLoss(NamedLossFunction):
    def __init__(
            self,
            state_channels: slice = slice(0, 3),
            state_weights_channel: Optional[slice | int] = None,
            target_channels: slice = slice(None, None),
            *,
            loss_fn: _LossFnProtocol = F.mse_loss,
            reduction_fn: _ReductionFnProtocol = torch.mean,
            target_position_x: slice = slice(None, None),
            target_position_y: slice = slice(None, None),
            loss_name: str = "rgb",
            state_activation = None
    ):
        super().__init__(loss_name=loss_name)
        self.state_channels = state_channels
        self.target_channels = target_channels
        if isinstance(state_weights_channel, int):
            state_weights_channel = slice(state_weights_channel, state_weights_channel + 1)
        self.state_weights_channel = state_weights_channel
        self.loss_fn = loss_fn
        self.reduction_fn = reduction_fn
        self.target_position_x = target_position_x
        self.target_position_y = target_position_y
        self.state_activation = state_activation

    def _calculate_loss(
            self,
            state_progression: Float[torch.Tensor, "N B C W H"],
            target: Float[torch.Tensor, "B K W H"],
            **kwargs
    ) -> Float[torch.Tensor, "B"]:
        state = state_progression[-1]
        if self.state_weights_channel is None:
            weights = 1
        else:
            weights = torch.mean(torch.abs(state[:, self.state_weights_channel]), dim=1, keepdim=True)
        cropped_state = state[:, self.state_channels, self.target_position_x, self.target_position_y]
        if self.state_activation is not None:
            cropped_state = self.state_activation(cropped_state)

        cellwise_loss = self.loss_fn(cropped_state, target[:, self.target_channels].to(state.device), reduction="none",
                                     **kwargs)
        loss_data = self.reduction_fn(
            cellwise_loss * weights,
            dim=(1, 2, 3)
        )
        return loss_data

    @classmethod
    def create_from_sizes(
            cls,
            seed_size: tuple[int, int],
            target_size: tuple[int, int],
            state_channels: slice = slice(0, 3),
            *,
            loss_fn: _LossFnProtocol = F.mse_loss,
            reduction_fn: _ReductionFnProtocol = torch.mean
    ):
        target_pad_x_start = (seed_size[0] - target_size[0]) // 2
        target_pad_x_end = target_pad_x_start + target_size[0]
        target_pad_y_start = (seed_size[1] - target_size[1]) // 2
        target_pad_y_end = target_pad_y_start + target_size[1]

        return cls(
            state_channels=state_channels,
            loss_fn=loss_fn,
            target_position_x=slice(target_pad_x_start, target_pad_x_end),
            target_position_y=slice(target_pad_y_start, target_pad_y_end),
            reduction_fn=reduction_fn
        )

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["loss_fn"] = full_class_name(self.loss_fn)
        cfg["state_channels"] = slice_to_config(self.state_channels)
        cfg["state_weights_channel"] = slice_to_config(self.state_weights_channel)
        cfg["target_channels"] = slice_to_config(self.target_channels)
        cfg["target_position_x"] = slice_to_config(self.target_position_x)
        cfg["target_position_y"] = slice_to_config(self.target_position_y)
        cfg["state_activation"] = self.state_activation.__name__ if self.state_activation is not None else None
        return cfg
