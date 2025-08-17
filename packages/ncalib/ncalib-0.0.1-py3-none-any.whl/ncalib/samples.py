from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F

from ncalib import NCA
from ncalib.nca.models.basic import BasicNCAModel
from ncalib.nca.models.tiny import TinyNCAModel
from ncalib.nca.modular_nca import ModularNCA
from ncalib.nca.perception.filter import IdentityPerception, SobelXPerception, SobelYPerception, LaPlace1Perception
from ncalib.nca.state_updater.alive_masking import AliveMasking
from ncalib.nca.state_updater.asynchronous_update import AsynchronousUpdate
from ncalib.nca.state_updater.simple_update import SimpleStateUpdater
from ncalib.utils.defaults import DEFAULT_DEVICE
from ncalib.utils.kernels import sobol_x, sobol_y


def generate_default_nca(channels=16, *, device=DEFAULT_DEVICE) -> ModularNCA:
    perception = IdentityPerception() + SobelXPerception() + SobelYPerception()

    model = BasicNCAModel(perception.output_size_for_n_channels(channels), channels)

    nca = ModularNCA(
        channels,
        perception,
        model,
        update_function=AsynchronousUpdate() + SimpleStateUpdater() + AliveMasking(),
        device=device
    )
    return nca


def generate_tiny_nca(channels=8, *, device=DEFAULT_DEVICE) -> ModularNCA:
    perception = LaPlace1Perception()

    model = TinyNCAModel(perception.output_size_for_n_channels(channels), channels)

    nca = ModularNCA(channels, perception, model, device=device)
    return nca


class HardcodedNCA(NCA):
    """ Code taken from https://github.com/SethPipho/pytorch-neural-cellular-automata """

    def __init__(
            self,
            channels=16,
            *,
            device: torch.device | str = torch.device('cpu')
    ):
        super().__init__(device=device)
        self._channels = channels

        self.conv1 = nn.Conv2d(self.channels * 3, 128, 1)
        self.conv2 = nn.Conv2d(128, self.channels, 1)

        self.sobol_x_kernel = sobol_x.to(self.device).view(1, 1, 3, 3).repeat(self.channels, 1, 1, 1)
        self.sobol_y_kernel = sobol_y.to(self.device).view(1, 1, 3, 3).repeat(self.channels, 1, 1, 1)

        self.to(self.device)

    def perception(self, state):
        sobol_x = F.conv2d(state, self.sobol_x_kernel, groups=self.channels, padding=1)
        sobol_y = F.conv2d(state, self.sobol_y_kernel, groups=self.channels, padding=1)
        return torch.cat((state, sobol_x, sobol_y), 1)

    def forward(self, state):
        perception = self.perception(state)

        ds = F.relu(self.conv1(perception))
        ds = self.conv2(ds)

        # simulate async update
        random_mask = (torch.rand((state.shape[0], 1, state.shape[2], state.shape[3]), device=self.device) < .5)
        ds = ds * random_mask

        # alive masking
        alive = F.max_pool2d(state[:, 3, :, :], 3, stride=1, padding=1) > .1
        alive = torch.unsqueeze(alive, 1)
        next_state = state + ds
        next_state = next_state * alive

        self._last_delta_state = ds

        return next_state

    @property
    def channels(self) -> int:
        return self._channels

    def reset(self):
        def reset_conv2d(layer):
            n = layer.in_channels
            for k in layer.kernel_size:
                n *= k
            stdv = 1. / torch.sqrt(n)
            layer.weight.data.uniform_(-stdv, stdv)
            if layer.bias is not None:
                layer.bias.data.uniform_(-stdv, stdv)

        reset_conv2d(self.conv1)
        reset_conv2d(self.conv2)
        self.conv2.weight.data.fill_(0.0)

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        # cfg["channels"] = self.channels  # Already set in super()
        cfg["model"] = {
            "channels": 128
        }

        return cfg
