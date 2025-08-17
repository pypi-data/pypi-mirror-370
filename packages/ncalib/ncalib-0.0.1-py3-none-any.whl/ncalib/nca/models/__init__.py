import abc
from typing import Any

import torch
import torch.nn as nn

from ncalib.utils.utils import NCA_Base


class NCA_Model(NCA_Base, nn.Module, abc.ABC):
    def __init__(self, input_size: int, output_size: int):
        super().__init__()
        nn.Module.__init__(self)

        self.input_size = input_size
        self.output_size = output_size

    @abc.abstractmethod
    def forward(self, perception: list[torch.Tensor], **kwargs) -> torch.Tensor:
        pass

    def reset(self):
        raise NotImplementedError(f"reset missing in {self.__class__.__name__}")

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["input_size"] = self.input_size
        cfg["output_size"] = self.output_size
        return cfg

    def required_kwargs(self) -> set[str]:
        return set()
