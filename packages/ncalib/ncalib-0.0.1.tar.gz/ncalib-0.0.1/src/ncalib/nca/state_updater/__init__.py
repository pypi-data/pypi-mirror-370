import abc

import torch
from torch import nn

from ncalib.utils.utils import NCA_Base


class NCA_StateUpdater(NCA_Base, nn.Module, abc.ABC):
    """
    Takes a state and a state update as input and returns the next state. E.g. normal Update and Alive-Masking Update
    """

    def __init__(self):
        super().__init__()
        nn.Module.__init__(self)
        self.model_size_factor = 1

    @abc.abstractmethod
    def forward(
            self,
            state: torch.Tensor,
            delta_state: torch.Tensor,
            **kwargs
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        :return: updated state, updated delta_state
        """
        pass

    def __add__(self, other: "NCA_StateUpdater"):
        # Prepare each state updater so that each is an iterable of simple state updaters
        if isinstance(self, CombinedStateUpdater):
            states1 = self.state_updater
        else:
            states1 = [self]

        if isinstance(other, CombinedStateUpdater):
            states2 = other.state_updater
        else:
            states2 = [other]

        # Combine State Updaters
        return CombinedStateUpdater(*states1, *states2)

    def required_kwargs(self) -> set[str]:
        return set()


class CombinedStateUpdater(NCA_StateUpdater):
    def __init__(self, *state_updater: NCA_StateUpdater):
        super().__init__()
        self.state_updater = nn.ModuleList(state_updater)
        self.model_size_factor = 1
        for updater in state_updater:
            self.model_size_factor *= updater.model_size_factor

    def forward(
            self,
            state: torch.Tensor,
            delta_state: torch.Tensor,
            **kwargs
    ) -> tuple[torch.Tensor, torch.Tensor]:
        for state_updater in self.state_updater:
            state, delta_state = state_updater(state, delta_state, **kwargs)

        return state, delta_state

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["_args_"] = [
            state_updater.to_config_dict()
            for state_updater in self.state_updater
        ]
        return cfg

    def reset(self):
        for state_updater in self.state_updater:
            state_updater.reset()

    def required_kwargs(self) -> set[str]:
        res = super().required_kwargs()
        for state_updater in self.state_updater:
            res.update(state_updater.required_kwargs())
        return res
