import warnings
from typing import Any
from ncalib.utils.torch_helper import weight_init

import torch
import torch.nn.functional as F
from torch import nn

from ncalib.nca.models import NCA_Model



class BasicNCAModel(NCA_Model):
    def __init__(self, input_size: int, output_size: int, hidden_channels: int = 128):
        super().__init__(input_size, output_size)
        warnings.warn(f"`{self.__class__.__name__}` is a legacy model that is kept only for backwards compatibility reasons. Please use `nca.models.linear.LinearNCAModel` instead!")


        self.conv1 = nn.Conv2d(input_size, hidden_channels, 1)
        self.conv2 = nn.Conv2d(hidden_channels, output_size, 1)
        self.hidden_channels = hidden_channels

    def forward(self, perception: list[torch.Tensor], **kwargs) -> torch.Tensor:
        total_perception = torch.cat(perception, 1)
        delta_state = F.relu(self.conv1(total_perception))
        delta_state = self.conv2(delta_state)

        return delta_state

    def reset(self):
        self.apply(weight_init)

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["hidden_channels"] = self.hidden_channels
        return cfg
