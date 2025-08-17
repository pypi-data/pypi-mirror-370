import abc
from pathlib import Path
from typing import Optional

import torch
import wandb
from wandb.apis.public import Run
from wandb.sdk.lib import RunDisabled

from ncalib.trainer import NCA_StoppingCriterion, NCA_Trainer
from ncalib.trainer.dataset import DataSample
from ncalib.trainer.logger import NCA_Logger
from ncalib.trainer.loss_function import LossResult


class WandBLogger(NCA_Logger, abc.ABC):
    """
    Extends the normal logger so that it basically gets disabled when wandb is disabled by replacing self.log with noop
    """

    def __init__(
            self,
            *,
            epoch_interval: int = 1000,
            log_final: bool = False
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final)
        self.run: Optional[Run] = None

    def init_training(self, trainer: NCA_Trainer, stopping_criterion: NCA_StoppingCriterion):
        super().init_training(trainer, stopping_criterion)
        if wandb.run is None:
            raise RuntimeError("WandB not initialized yet. Please call .wandb.init() when using WandBLogger!")
        self.run = wandb.run
        if isinstance(self.run, RunDisabled):
            self.logger.warn(f"WandB is disabled. Disabling {self}")
            self.log = self.log_noop

    def log_noop(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        """ Replaces self.log if mode =="disabled" """
        pass


class WandBModelLogger(WandBLogger):
    def __init__(
            self,
            *,
            leading_zeros: int = 5,
            epoch_interval: int = 1000,
            log_final: bool = False
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final)
        self.leading_zeros = leading_zeros
        self.latest_model_path = None

    def init_training(self, trainer: NCA_Trainer, stopping_criterion: NCA_StoppingCriterion):
        super().init_training(trainer, stopping_criterion)
        wandb.watch(self.trainer.nca, log_freq=self.epoch_interval)

    def _log(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        log_path = Path(self.run.dir) / "models" / f"model-{self.trainer.epoch:0{self.leading_zeros}d}.nca"
        log_path.parent.mkdir(exist_ok=True, parents=True)
        torch.save(self.trainer.nca.as_full_config_dict(), log_path)
        wandb.save(str(log_path.absolute()), base_path=self.run.dir)
        self.latest_model_path = log_path
