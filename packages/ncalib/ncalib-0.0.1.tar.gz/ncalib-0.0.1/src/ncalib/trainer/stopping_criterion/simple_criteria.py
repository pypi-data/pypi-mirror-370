import torch

from ncalib.trainer import NCA_StoppingCriterion
from ncalib.trainer.dataset import DataSample
from ncalib.trainer.loss_function import LossResult


class MaxEpochs(NCA_StoppingCriterion):
    def __init__(self, max_epochs: int = 1000):
        super().__init__(f"Reached max epochs ({max_epochs})")
        self.max_epochs = max_epochs

    def evaluate(self, trainer: "NCA_Trainer", sample: DataSample, state_progression: torch.Tensor,
                 loss: LossResult) -> bool:
        return trainer.epoch >= self.max_epochs

    def __len__(self):
        return self.max_epochs


class MaxTime(NCA_StoppingCriterion):
    def __init__(self, time_limit: float = 600):
        super().__init__(f"Reached time_limit ({time_limit} seconds)")
        self.time_limit = time_limit  # in seconds

    def evaluate(self, trainer: "NCA_Trainer", sample: DataSample, state_progression: torch.Tensor,
                 loss: LossResult) -> bool:
        if trainer._time_started is None:
            return False  # Training not started yet

        return trainer.training_duration >= self.time_limit

    def __len__(self):
        return self.time_limit


class LossIsNaN(NCA_StoppingCriterion):
    def __init__(self):
        super().__init__("Loss is not a number (NaN)", is_fatal=True)

    def evaluate(self, trainer: "NCA_Trainer", sample: DataSample, state_progression: torch.Tensor,
                 loss: LossResult) -> bool:
        if loss is None:
            # Training not started yet
            return False
        return bool(not torch.isfinite(loss.total_loss(ignore_inf=True)))


class LossSmallerThan(NCA_StoppingCriterion):
    def __init__(self, threshold: float):
        super().__init__(f"Loss below threshold ({threshold})", is_fatal=False)
        self.threshold = threshold

    def evaluate(self, trainer: "NCA_Trainer", sample: DataSample, state_progression: torch.Tensor,
                 loss: LossResult) -> bool:
        if loss is None:
            # Training not started yet
            return False
        if not torch.isfinite(loss.total_loss(ignore_inf=True)):
            return False
        return loss.total_loss() < self.threshold
