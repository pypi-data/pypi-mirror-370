import abc
from typing import Callable, Any

import torch

from ncalib.trainer.dataset import NCA_Dataset, DataSample
from ncalib.trainer.loss_function import LossResult
from ncalib.utils.defaults import DEFAULT_DEVICE
from ncalib.utils.utils import NCA_Base


class NCA_Batcher(NCA_Base, abc.ABC):
    def __init__(
            self,
            dataset: NCA_Dataset,
            batch_size: int,
            num_workers: int = 0,
            collate_fn: Callable = DataSample.merge_batch,
            device: torch.device | str = DEFAULT_DEVICE
    ):
        super().__init__()
        self.collate_fn = collate_fn
        self.batch_size = batch_size
        self.dataset = dataset
        self.num_workers = num_workers
        self.device = device

    @abc.abstractmethod
    def next_batch(self) -> DataSample:
        pass

    def init(self):
        pass

    def feedback(self, data_sample: DataSample, new_state: torch.Tensor, loss: LossResult):
        pass

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["dataset"] = self.dataset.to_config_dict()
        cfg["batch_size"] = self.batch_size
        cfg["num_workers"] = self.num_workers
        return cfg
