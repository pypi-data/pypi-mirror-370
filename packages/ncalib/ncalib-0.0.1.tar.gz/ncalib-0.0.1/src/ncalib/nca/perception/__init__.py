import abc
from typing import Type, Any, Iterable

import torch
import torch.nn as nn
from hydra.utils import instantiate

from ncalib.utils.utils import NCA_Base


class NCA_Perception(NCA_Base, nn.Module, abc.ABC):
    def __init__(self, channel_slice: slice = slice(None, None, None)):
        super().__init__()
        nn.Module.__init__(self)
        self.channel_slice = channel_slice

    def __add__(self, other: "NCA_Perception") -> "ChainedPerception":
        return ChainedPerception(perceptions=[self, other])

    def __getitem__(self, item: slice | int):
        if isinstance(item, int):
            item = slice(item, item + 1)

        if not (self.channel_slice is None or self.channel_slice == slice(None, None, None)) and item != self.channel_slice:
            raise ValueError("This perception already has a channel slice!")

        assert isinstance(item, slice)
        cpy = instantiate(self.to_config_dict())
        cpy.channel_slice = item
        return cpy

    def get_state(self, state: torch.Tensor) -> torch.Tensor:
        return state[:, self.channel_slice]

    @abc.abstractmethod
    def forward(self, state: torch.Tensor, **kwargs) -> list[torch.Tensor]:
        """
        :param state: Tensor [B x C x W x H]
        :return: List of Tensor [B x C x W x H]
        """
        pass

    def output_size_for_n_channels(self, channels: int) -> int:
        img = torch.zeros((1, channels, 1, 1))
        perception = self(img)
        return len(self.concat(perception)[0])

    @classmethod
    def concat(cls, perceptions: list[torch.Tensor]) -> torch.Tensor:
        """
        Concatenates a list of perceptions as one tensor in the channel dimension
        :param perceptions: list of Tensor [B x C x W x H]
        :return: [B x C*n x W x H]
        """
        return torch.cat(perceptions, dim=1)

    def required_kwargs(self) -> set[str]:
        return set()

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["channel_slice"] = self.channel_slice
        return cfg


class ChainedPerception(NCA_Perception):
    def __init__(
            self,
            *,
            perceptions: Iterable[Type[NCA_Perception] | NCA_Perception],
            channel_slice: slice = slice(None, None, None)
    ):
        super().__init__(channel_slice=channel_slice)
        self.perceptions: tuple[perceptions] = self._unchain(tuple(perceptions))

    def forward(self, state: torch.Tensor, **kwargs) -> list[torch.Tensor]:
        perceptions = []
        state = self.get_state(state)
        for perception in self.perceptions:
            perceptions += perception(state, **kwargs)
        return perceptions

    def _unchain(
            self,
            perceptions: tuple[NCA_Perception | Type[NCA_Perception]],
    ) -> tuple[NCA_Perception]:
        """
        Unchains perceptions, so that chained perceptions do not have chained perceptions as perceptions.
        E.g.
        Input: (SobelXPerception(), ChainedPerception(perceptions=[SobelYPerception(), LaPlacePerception()]))
        Output: (SobelXPerception(), SobelYPerception(), LaPlacePerception())

        Input: (SobelXPerception(), SobelYPerception(), LaPlacePerception())
        Output: (SobelXPerception(), SobelYPerception(), LaPlacePerception())
        """
        res = []
        for perception in perceptions:
            if isinstance(perception, type):
                if not issubclass(perception, NCA_Perception):
                    raise TypeError(f"Perception has to be a subclass of {NCA_Perception} (Got {perception})")
                res.append(perception())
            if isinstance(perception, ChainedPerception):
                res += list(self._unchain(perception.perceptions))
            elif isinstance(perception, NCA_Perception):
                res.append(perception)
            else:
                TypeError(f"Unknown type for {perception}: {type(perception)}")
        return tuple(res)

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["perceptions"] = [perception.to_config_dict() for perception in self.perceptions]
        return cfg

    def required_kwargs(self) -> set[str]:
        res = set()
        for perception in self.perceptions:
            res.update(perception.required_kwargs())

        return res

    def reset(self):
        for perception in self.perceptions:
            perception.reset()
