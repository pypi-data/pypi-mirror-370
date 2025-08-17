import abc

import torch

from ncalib.utils.defaults import DEFAULT_DEVICE
from ncalib.utils.utils import NCA_Base


class NCA_Target(NCA_Base, abc.ABC):
    def __init__(
            self,
            *,
            device: torch.device | str = DEFAULT_DEVICE
    ):
        super().__init__()

        self.device = device

    @abc.abstractmethod
    def __call__(self, n=1) -> torch.Tensor:
        """ Samples next targets [n x C x W x H]"""
        pass

    @property
    def channels(self) -> int:
        return self().shape[1]

    @property
    def width(self) -> int:
        return self().shape[2]

    @property
    def height(self) -> int:
        return self().shape[3]


class DummyTarget(NCA_Target):
    def __init__(self, channels=4, width=32, height=32, *, device: torch.device | str = DEFAULT_DEVICE):
        super().__init__(device=device)
        self._channels = channels
        self._width = width
        self._height = height

    def __call__(self, n=1) -> torch.Tensor:
        return torch.zeros((n, self._channels, self._width, self._height), device=self.device)
