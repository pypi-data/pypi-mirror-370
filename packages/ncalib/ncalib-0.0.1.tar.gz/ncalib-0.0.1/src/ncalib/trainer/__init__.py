import abc
import time
from typing import Optional, Any

import torch.nn as nn
import torch.optim
from lightning import Fabric
from torch.nn.modules.loss import _Loss

from ncalib import NCA
from ncalib.nca.modular_nca import ModularNCA
from ncalib.trainer.logger import NCA_Logger
from ncalib.trainer.stopping_criterion import NCA_StoppingCriterion
from ncalib.trainer.stopping_criterion.simple_criteria import MaxEpochs
from ncalib.trainer.target import NCA_Target
from ncalib.utils.utils import NCA_Base


class NCA_Trainer(NCA_Base, abc.ABC):
    def __init__(
            self,
            nca: ModularNCA,
            *,
            optimizer: Optional[torch.optim.Optimizer] = None,  # Defaults to Adam with lr=1e-3
            scheduler: Optional[Any] = None,  # Needs to be of type torch.optim._LRScheduler
    ):
        super().__init__()
        self.nca = nca

        # PyTorch training
        if optimizer is None:
            optimizer = torch.optim.Adam(self.nca.parameters(), lr=1e-3)

        self.optimizer = optimizer
        self.scheduler = scheduler

        # Optimize with Fabric
        torch.set_float32_matmul_precision("high")
        self.fabric = Fabric(precision="16-mixed")  # bf16-mixed for 4090, otherwise 16-mixed
        self.nca, self.optimizer = self.fabric.setup(self.nca, self.optimizer)

        # Used during training
        self.losses: list[float] = []
        self._epoch: Optional[int] = None
        self._time_started: Optional[float] = None
        self._time_finished: Optional[float] = None
        self._latest_metrics: dict[str, float] = {}

    @property
    def latest_metrics(self) -> dict[str, float]:
        metrics = {
            "loss": self.latest_loss
        }
        metrics.update(self._latest_metrics)
        return metrics

    @property
    def epoch(self) -> int:
        if self._epoch is None:
            raise RuntimeError("Training not started yet")
        return self._epoch

    @property
    def latest_loss(self) -> float:
        if len(self.losses) == 0:
            raise RuntimeError("Training not started yet")
        return self.losses[-1]

    @property
    def training_duration(self) -> float:
        if self._time_started is None:
            raise RuntimeError("Training not started yet")
        if self._time_finished is None:
            return time.perf_counter() - self._time_started
        return self._time_finished - self._time_started

    @abc.abstractmethod
    def train(
            self,
            stopping_criterion: NCA_StoppingCriterion = MaxEpochs(1000),
            *,
            loggers: NCA_Logger | None = None
    ):
        pass

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["nca"] = self.nca.to_config_dict()
        cfg["normalize_gradients"] = self.normalize_gradients
        return cfg
