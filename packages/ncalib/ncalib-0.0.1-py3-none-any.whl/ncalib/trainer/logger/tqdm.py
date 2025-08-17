import sys
from typing import Optional

import torch
from tqdm.auto import tqdm

from ncalib.trainer import NCA_StoppingCriterion, NCA_Trainer
from ncalib.trainer.dataset import DataSample
from ncalib.trainer.logger import NCA_Logger
from ncalib.trainer.loss_function import LossResult


class TQDMLogger(NCA_Logger):
    def __init__(self, *, file=sys.stdout):
        super().__init__(epoch_interval=1)
        self.file = file

        self._pbar: Optional[tqdm] = None

    @property
    def progress_bar(self) -> tqdm:
        if self._pbar is None:
            self.not_initialized_yet()
        return self._pbar

    def init_training(self, trainer: NCA_Trainer, stopping_criterion: NCA_StoppingCriterion):
        super().init_training(trainer, stopping_criterion)
        total = len(stopping_criterion)
        self._pbar = tqdm(total=total, file=self.file)

    def _log(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        self.progress_bar.update(1)
        self.progress_bar.set_postfix({
            name: f"{loss:.10f}"
            for name, (loss, weight)
            in loss.detailed_loss(include_total=True).items()
        })

    def close(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        super().close(data_sample, state_progression, loss)
        self.progress_bar.close()
