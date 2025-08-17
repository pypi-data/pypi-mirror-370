import abc
from typing import Literal, Any

import torch
import torch.nn as nn
import torch.nn.functional as F

from ncalib.nca.perception import NCA_Perception
from ncalib.utils import kernels
from ncalib.utils.torch_helper import weight_init


class IdentityPerception(NCA_Perception):
    def forward(self, state: torch.Tensor, **kwargs) -> list[torch.Tensor]:
        return [self.get_state(state)]

    def to(self, device: torch.device | str) -> "IdentityPerception":
        return self


class FilterPerception(NCA_Perception, abc.ABC):
    KERNEL: torch.Tensor

    def __init__(
            self,
            *,
            padding_mode: Literal["constant", "reflect", "replicate", "circular"] = "replicate",
            channel_slice: slice = slice(None, None, None)
    ):
        """
        :param padding_mode: See https://pytorch.org/docs/stable/generated/torch.nn.functional.pad.html for more info
        """
        super().__init__(channel_slice=channel_slice)
        W, H = self.KERNEL.shape
        self.kernel = self.KERNEL.view(1, 1, W, H)
        self.padding_mode = padding_mode
        self._padding = (int(W // 2), int(H // 2)) * 2  # Creates a tuple of 4 values

    def forward(self, state: torch.Tensor, **kwargs) -> list[torch.Tensor]:
        state = self.get_state(state)
        channels = state.shape[1]
        padded = F.pad(state, self._padding, mode=self.padding_mode)
        return [F.conv2d(padded, self.kernel.repeat(channels, 1, 1, 1).to(state.device), groups=channels, padding=0)]

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["padding_mode"] = self.padding_mode
        return cfg


class SobelXPerception(FilterPerception):
    KERNEL = kernels.sobol_x


class SobelYPerception(FilterPerception):
    KERNEL = kernels.sobol_y


class SobelX5Perception(FilterPerception):
    KERNEL = kernels.sobol_x5


class SobelY5Perception(FilterPerception):
    KERNEL = kernels.sobol_y5


class LaPlace1Perception(FilterPerception):
    KERNEL = kernels.laplace_3x3_1


class LaPlace2Perception(FilterPerception):
    """ Version from https://distill.pub/selforg/2021/textures/ """
    KERNEL = kernels.laplace_3x3_2


class ConvPerception(FilterPerception, nn.Module):
    KERNEL = kernels.zeros_3x3

    def __init__(
            self,
            out_channels: int,
            kernel_size: int | tuple[int, int] = (3, 3),
            padding_mode: Literal["constant", "reflect", "replicate", "circular"] = "replicate",
    ):
        super().__init__(padding_mode=padding_mode)
        nn.Module.__init__(self)
        del self.kernel
        self.out_channels = out_channels
        if isinstance(kernel_size, int):
            kernel_size = (kernel_size, kernel_size)
        self.kernel_size = kernel_size
        self.register_parameter("kernel", nn.Parameter(torch.randn(out_channels, 1, *kernel_size)))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(out_channels={self.out_channels}, kernel_size={self.kernel_size}, padding_mode={self.padding_mode})"

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["out_channels"] = self.out_channels
        cfg["kernel_size"] = self.kernel_size
        return cfg

    def reset(self):
        self.apply(weight_init)
