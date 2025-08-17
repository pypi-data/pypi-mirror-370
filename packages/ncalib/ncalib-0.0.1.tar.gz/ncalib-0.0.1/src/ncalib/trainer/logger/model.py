import json
import time
import warnings
from pathlib import Path

import torch

from ncalib.trainer import NCA_Logger
from ncalib.trainer.dataset import DataSample
from ncalib.trainer.loss_function import LossResult


class ModelLogger(NCA_Logger):
    def __init__(
            self,
            log_dir: str | Path,
            model_name: str = None,
            *,
            leading_zeros: int = 5,
            epoch_interval: int = 1000,
            log_final: bool = False
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final)
        self.log_dir = Path(log_dir)

        if model_name is None:
            model_name = f"model-{time.time():.0f}"

        self.model_name = model_name
        self.leading_zeros = leading_zeros
        self._latest_model_path = None

    @property
    def latest_model_path(self) -> Path:
        if self._latest_model_path is None:
            raise FileNotFoundError("No model saved yet!")
        return self._latest_model_path

    def init_training(self, trainer: "NCA_Trainer", stopping_criterion: "NCA_StoppingCriterion"):
        super().init_training(trainer, stopping_criterion)
        self.log_dir.mkdir(exist_ok=True, parents=True)

    def _log(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        full_config = self.trainer.nca.as_full_config_dict()
        log_file = self.log_dir / f"{self.model_name}.{self.trainer.epoch:0{self.leading_zeros}d}.nca"

        self.logger.debug(f"Saving model for epoch {self.trainer.epoch} at \"{log_file}\"")
        torch.save(full_config, log_file)
        self._latest_model_path = log_file


class LossJSONLinesLogger(NCA_Logger):
    def __init__(
            self,
            filename: Path | str,
            epoch_interval: int = 10,
            log_final: bool = True
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final)
        self.filename = Path(filename)
        self.opened_file = None

        self._i = 0

    def init_training(self, trainer: "NCA_Trainer", stopping_criterion: "NCA_StoppingCriterion"):
        super().init_training(trainer, stopping_criterion)
        self.filename.parent.mkdir(exist_ok=True, parents=True)
        self.opened_file = self.filename.open("w")
        self._i = 0

    def _log(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        detailed_loss = loss.detailed_loss(include_total=True)
        log_data = {
            "epoch": self.trainer.epoch
        }
        log_data.update({f"loss_{name}": loss for name, (loss, weight) in detailed_loss.items()})
        log_data.update({f"lossweighted_{name}": loss * weight for name, (loss, weight) in detailed_loss.items() if
                         name != "total"})
        if self.opened_file is not None:
            self.opened_file.write(json.dumps(log_data) + "\n")
            self._i += 1
            if self._i % 20 == 0:
                self.opened_file.flush()
        else:
            warnings.warn(f"File {self.filename} not opened! Skip logging...")

    def close(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        if self.opened_file is not None:
            self.opened_file.close()
