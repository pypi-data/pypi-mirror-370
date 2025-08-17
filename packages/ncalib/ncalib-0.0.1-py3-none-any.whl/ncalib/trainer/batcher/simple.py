from typing import Callable

import torch
from torch.utils.data import DataLoader

from ncalib.trainer.batcher import NCA_Batcher
from ncalib.trainer.dataset import NCA_Dataset, DataSample
from ncalib.utils.defaults import DEFAULT_DEVICE


class SimpleBatcher(NCA_Batcher):
    def __init__(
            self,
            dataset: NCA_Dataset,
            batch_size: int,
            num_workers: int = 0,
            collate_fn: Callable = DataSample.merge_batch,
            device: torch.device | str = DEFAULT_DEVICE
    ):
        super().__init__(dataset, batch_size, num_workers=num_workers, collate_fn=collate_fn, device=device)
        self.dataloader = iter(DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=False,  # Shuffling is done in Dataset
            num_workers=num_workers,
            drop_last=True,
            collate_fn=collate_fn
        ))

    def next_batch(self) -> DataSample:
        return next(self.dataloader).to(self.device)
