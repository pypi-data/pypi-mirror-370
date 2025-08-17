import abc
from typing import Optional

import torch

from ncalib.trainer.dataset import DataSample
from ncalib.trainer.loss_function import LossResult
from ncalib.utils.utils import NCA_Base


class NCA_StoppingCriterion(NCA_Base, abc.ABC):

    def __init__(self, message: str = "", is_fatal: bool = False):
        super().__init__()
        self.message = message
        self.is_fatal = is_fatal
        self.last_evaluation = False

    def __call__(self, trainer: "NCA_Trainer", sample: DataSample, state_progression: torch.Tensor,
                 loss: LossResult) -> bool:
        """
        :param trainer:
        :param sample: DataSample with at least .states[B x C x W x H], .targets[B x C' x W x H] and .num_steps[B]
        :param state_progression: Tensor[T x B x C x W x H]
        :param loss: LossResult
        :return: True if it should stop, False otherwise
        """
        self.last_evaluation = self.evaluate(trainer, sample, state_progression, loss)
        return self.last_evaluation

    def __neg__(self) -> "ChainedNot":
        return ChainedNot(self)

    def __or__(self, other: "NCA_StoppingCriterion") -> "ChainedOr":
        assert isinstance(other, NCA_StoppingCriterion)

        return ChainedOr(self, other)

    def __and__(self, other: "NCA_StoppingCriterion") -> "ChainedAnd":
        assert isinstance(other, NCA_StoppingCriterion)

        return ChainedAnd(self, other)

    def __len__(self):
        return None

    @abc.abstractmethod
    def evaluate(self, trainer: "NCA_Trainer", sample: DataSample, state_progression: torch.Tensor,
                 loss: LossResult) -> bool:
        """
        :param trainer:
        :param sample: DataSample with at least .states[B x C x W x H], .targets[B x C' x W x H] and .num_steps[B]
        :param state_progression: Tensor[T x B x C x W x H]
        :param loss: LossResult
        :return: True if it should stop, False otherwise
        """
        pass


class ChainedOr(NCA_StoppingCriterion):
    def __init__(self, *criteria: NCA_StoppingCriterion):
        super().__init__()
        self.criteria = criteria

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.criteria}"

    def __add__(self, other) -> "ChainedOr":
        assert isinstance(other, NCA_StoppingCriterion)

        return ChainedOr(*self.criteria, other)

    def __len__(self) -> Optional[int]:
        values = list(filter(lambda s: s is not None, map(lambda s: s.__len__(), self.criteria)))
        if len(values) == 0:
            return None
        return min(values)

    def evaluate(self, trainer: "NCA_Trainer", sample: DataSample, state_progression: torch.Tensor,
                 loss: LossResult) -> bool:
        for criterion in self.criteria:
            if criterion(trainer, sample, state_progression, loss):
                self.is_fatal = criterion.is_fatal
                self.message = criterion.message
                return True

        self.is_fatal = False
        self.message = ""
        return False


class ChainedAnd(NCA_StoppingCriterion):
    def __init__(self, *criteria: NCA_StoppingCriterion):
        super().__init__()
        self.criteria = criteria
        self.is_fatal = any(criterion.is_fatal for criterion in criteria)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.criteria}"

    def __len__(self) -> Optional[int]:
        values = list(filter(lambda s: s is not None, map(lambda s: s.__len__(), self.criteria)))
        if len(values) == 0:
            return None
        return max(values)

    def __mul__(self, other) -> "ChainedAnd":
        assert isinstance(other, NCA_StoppingCriterion)

        return ChainedAnd(*self.criteria, other)

    def evaluate(self, trainer: "NCA_Trainer", sample: DataSample, state_progression: torch.Tensor,
                 loss: LossResult) -> bool:
        message = ""
        for criterion in self.criteria:
            if not criterion(trainer, sample, state_progression, loss):
                return False

            message += f"{criterion.message}\n"

        self.message = message
        return True


class ChainedNot(NCA_StoppingCriterion):
    def __init__(self, criterion: NCA_StoppingCriterion):
        super().__init__()
        self.criterion = criterion
        self.message = self.criterion.message
        self.is_fatal = self.criterion.is_fatal

    def __neg__(self) -> NCA_StoppingCriterion:
        return self.criterion

    def evaluate(self, trainer: "NCA_Trainer", sample: DataSample, state_progression: torch.Tensor,
                 loss: LossResult) -> bool:
        return not self.criterion(trainer, sample, state_progression, loss)
