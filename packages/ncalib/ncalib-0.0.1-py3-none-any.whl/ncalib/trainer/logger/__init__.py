import abc
from typing import Optional, Iterable, Union, Any

import torch

from ncalib.trainer.dataset import DataSample
from ncalib.trainer.loss_function import LossResult
from ncalib.utils.utils import NCA_Base


class NCA_Logger(NCA_Base, abc.ABC):
    def __init__(self, *, epoch_interval: int = 1000, log_final: bool = False):
        super().__init__()
        self.epoch_interval = epoch_interval
        self.log_final = log_final
        self._latest_logging_epoch = None

        # Training specific stuff
        self._trainer: Optional["NCA_Trainer"] = None
        self._stopping_criterion: Optional["NCA_StoppingCriterion"] = None

    def __add__(self, other: "NCA_Logger") -> "NCA_Logger":
        # Prepare each logger so that each is an iterable of simple logger
        if isinstance(self, CombinedLogger):
            loggers1 = self.loggers
        else:
            loggers1 = [self]

        if isinstance(other, CombinedLogger):
            loggers2 = other.loggers
        else:
            loggers2 = [other]

        # Combine Logger
        return CombinedLogger(*loggers1, *loggers2)

    def not_initialized_yet(self):
        raise RuntimeError(f"{self.__class__.__name__} not initialized yet. Please run `init_training()`")

    @property
    def trainer(self) -> "NCA_Trainer":
        if self._trainer is None:
            self.not_initialized_yet()
        return self._trainer

    @property
    def stopping_criterion(self) -> "NCA_StoppingCriterion":
        if self._stopping_criterion is None:
            self.not_initialized_yet()
        return self._stopping_criterion

    def init_training(self, trainer: "NCA_Trainer", stopping_criterion: "NCA_StoppingCriterion"):
        if self._trainer is not None or self._stopping_criterion is not None:
            raise RuntimeError("Logger already initialized. "
                               "Only use 1 instance of logger per training or it might yield to complications")
        self._stopping_criterion = stopping_criterion
        self._trainer = trainer

    def log(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        """
        :param data_sample: DataSample with at least .states, .targets, .num_steps
        :param state_progression: Tensor[T x B x C x W x H]
        :param loss: LossResult
        :return:
        """
        if self.trainer.epoch % self.epoch_interval == 0:
            self._latest_logging_epoch = self.trainer.epoch
            return self._log(data_sample, state_progression, loss)

    @abc.abstractmethod
    def _log(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        """
        :param data_sample: DataSample with at least .states, .targets, .num_steps
        :param state_progression: Tensor[T x B x C x W x H]
        :param loss: LossResult
        :return:
        """
        pass

    def close(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        if self.log_final and self.trainer.epoch != self._latest_logging_epoch:
            return self._log(data_sample, state_progression, loss)

    @classmethod
    def as_loggers_list(cls, loggers: Union["NCA_Logger", Iterable["NCA_Logger"], None]) -> list["NCA_Logger"]:
        if loggers is None:
            return []
        elif isinstance(loggers, NCA_Logger):
            return [loggers]

        for logger in loggers:
            if not isinstance(logger, cls):
                raise TypeError(f"{logger} is not a {cls.__name__}")

        return list(loggers)


class NoOPLogger(NCA_Logger):
    def _log(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        pass


class CombinedLogger(NCA_Logger):
    def __init__(self, *loggers: NCA_Logger):
        super().__init__()
        self.loggers = [logger for logger in loggers if not isinstance(logger, NoOPLogger)]

    def init_training(self, trainer: "NCA_Trainer", stopping_criterion: "NCA_StoppingCriterion"):
        for logger in self.loggers:
            self.logger.info(f"Initializing logger {logger}")
            logger.init_training(trainer, stopping_criterion)

    def log(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        for logger in self.loggers:
            logger.log(data_sample, state_progression, loss)

    def _log(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        raise RuntimeError("This method should never be called, as the .log()-Function is replaced")

    def close(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        for logger in self.loggers:
            logger.close(data_sample, state_progression, loss)

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["_args_"] = [logger.to_config_dict() for logger in self.loggers]
        return cfg
