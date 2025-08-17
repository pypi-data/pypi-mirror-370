from typing import Any
from ncalib.utils.torch_helper import weight_init

import torch
from torch import nn

from ncalib.nca.models import NCA_Model


class LinearNCAModel(NCA_Model):
    def __init__(self, input_size: int, output_size: int, hidden_channels: int = 128, hidden_layers: int = 1, out_bias=True):
        super().__init__(input_size, output_size)
        layers = []
        for i in range(hidden_layers):
            layers += [
                nn.Conv2d(input_size, hidden_channels, kernel_size=1),
                nn.ReLU(),
            ]
            input_size = hidden_channels

        self.conv_hidden = nn.Sequential(*layers)

        # Final output layer
        self.out_bias = out_bias
        self.conv_output = nn.Conv2d(input_size, output_size, kernel_size=1, bias=self.out_bias)

        self.hidden_channels = hidden_channels
        self.hidden_layers = hidden_layers

    def forward(self, perception: list[torch.Tensor], **kwargs) -> torch.Tensor:
        total_perception = torch.cat(perception, 1)
        delta_state = self.conv_hidden(total_perception)
        delta_state = self.conv_output(delta_state)

        return delta_state

    def reset(self):
        self.apply(weight_init)

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["hidden_channels"] = self.hidden_channels
        cfg["hidden_layers"] = self.hidden_layers
        cfg["out_bias"] = self.out_bias
        return cfg
