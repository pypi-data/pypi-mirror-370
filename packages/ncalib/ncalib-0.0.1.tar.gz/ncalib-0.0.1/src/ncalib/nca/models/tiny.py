from typing import Any

import torch
import torch.nn.functional as F
from torch import nn

from ncalib.nca.models import NCA_Model


class TinyNCAModel(NCA_Model):
    def __init__(self, input_size: int, output_size: int):
        super().__init__(input_size, output_size)

        self.conv1 = nn.Conv2d(input_size, 8, 1)
        self.conv2 = nn.Conv2d(input_size, 8, 1)

    def forward(self, perception: list[torch.Tensor], **kwargs) -> torch.Tensor:
        perception = torch.cat(perception, 1)
        return self.conv2(F.relu(self.conv1(perception)))

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        return cfg
