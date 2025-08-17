import logging
from typing import Type, Any, Optional

import torch

from ncalib import NCA, NCA_Perception, ChainedPerception
from ncalib.nca.models import NCA_Model
from ncalib.nca.models.linear import LinearNCAModel
from ncalib.nca.perception.filter import IdentityPerception, SobelXPerception, SobelYPerception
from ncalib.nca.state_updater import NCA_StateUpdater
from ncalib.nca.state_updater.asynchronous_update import AsynchronousUpdate
from ncalib.nca.state_updater.simple_update import SimpleStateUpdater


class ReproducibilityError(Exception):
    pass


class ModularNCA(NCA):
    def __init__(
            self,
            channels: int,
            perception: NCA_Perception = ChainedPerception(perceptions=[
                IdentityPerception, SobelXPerception, SobelYPerception
            ]),
            model: NCA_Model | Type[NCA_Model] = LinearNCAModel,
            *,
            update_function: NCA_StateUpdater = AsynchronousUpdate() + SimpleStateUpdater(),
            device: torch.device | str = torch.device('cpu'),
            check_reproducibility=True,
    ):
        super().__init__(device=device)

        self.logger = logging.getLogger(self.__class__.__name__)
        # NCA Properties
        self._channels = channels

        # = Perception =
        self.perception = perception

        # = Model =
        if isinstance(model, type):
            if not issubclass(model, NCA_Model):
                raise TypeError(f"Expected type {NCA_Model} for model. Got {model}")
            self.model = model(self.perception.output_size_for_n_channels(channels), channels)
        else:
            self.model = model

        # = Post-processing =
        self.state_update_function = update_function

        # Update device
        super().to(device)
        self.model = self.model.to(self.device)
        # Perception and Post-processing gets device from state

        # Reproducibility check
        if check_reproducibility:
            self.reproducibility_check()

        # Properties
        self._last_perception: Optional[torch.Tensor] = None

    def compile(self, *, perception=True, model=True, update_function=True):
        if perception:
            self.perception = torch.compile(self.perception, mode="reduce-overhead")
        if model:
            self.model = torch.compile(self.model)  # Cannot use "reduce-overhead"
        if update_function:
            self.state_update_function = torch.compile(self.state_update_function, mode="reduce-overhead")

    def forward(self, state: torch.Tensor, **kwargs) -> torch.Tensor:
        # Perception
        perception = self.perception(state, **kwargs)

        # Model
        delta_state = self.model(perception, **kwargs)

        # Post-processing
        next_state, delta_state = self.state_update_function(
            state,
            delta_state,
            original_state=state.detach().clone(),
            perception=perception,
            **kwargs
        )

        self._last_perception = perception
        self._last_delta_state = delta_state
        return next_state

    @property
    def channels(self) -> int:
        return self._channels

    def reset(self):
        self.model.reset()
        self.perception.reset()
        self.state_update_function.reset()

    def reproducibility_check(self):
        config_dict = self.as_full_config_dict()
        nca = self.load_from(config_dict)

        if self.num_params != nca.num_params:
            raise ReproducibilityError("Number of parameters does not match!")

        self.logger.info("Reproducibility check passed!")

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["perception"] = self.perception.to_config_dict()
        cfg["model"] = self.model.to_config_dict()
        cfg["update_function"] = self.state_update_function.to_config_dict()
        cfg["channels"] = self.channels
        cfg["check_reproducibility"] = False  # Prevent infinite loop

        return cfg

    def to(
            self,
            device: torch.device | str
    ):
        super().to(device=device)
        self.model.to(device)

    def required_kwargs(self) -> set[str]:
        res = super().required_kwargs()
        res.update(self.perception.required_kwargs())
        res.update(self.model.required_kwargs())
        res.update(self.state_update_function.required_kwargs())
        return res
