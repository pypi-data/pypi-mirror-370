from typing import Callable, Any

import torch
from torch.utils.data import DataLoader

from ncalib.trainer.batcher import NCA_Batcher
from ncalib.trainer.batcher.pool.eviction_policies import PoolEvictionPolicy
from ncalib.trainer.batcher.pool.eviction_policies.loss_policies import LossSortEvictionPolicy
from ncalib.trainer.dataset import NCA_Dataset, DataSample
from ncalib.trainer.loss_function import LossResult
from ncalib.utils.defaults import DEFAULT_DEVICE


class PooledBatcher(NCA_Batcher):
    def __init__(
            self,
            dataset: NCA_Dataset,
            batch_size: int,
            pool_size: int,
            eviction_policy: PoolEvictionPolicy = LossSortEvictionPolicy(),
            replace_n_worst: int = 1,
            num_workers: int = 0,
            warmup: int = 0,
            collate_fn: Callable = DataSample.merge_batch,
            device: torch.device | str = DEFAULT_DEVICE,
    ):
        super().__init__(dataset, batch_size, num_workers=num_workers, collate_fn=collate_fn, device=device)
        self.dataloader = iter(
            DataLoader(
                self.dataset,
                batch_size=replace_n_worst if replace_n_worst >= 1 else 1,
                shuffle=False,  # Shuffling is done in dataset
                num_workers=self.num_workers,
                drop_last=True,
                collate_fn=self.collate_fn,
            )
        )

        self.eviction_policy = eviction_policy
        self.pool_size = pool_size
        self.replace_worst_n = replace_n_worst
        self.pool = None
        self._losses = None
        self.warmup = warmup

        self._current_replaces = 0

    def init(self):
        init_dataloader = iter(DataLoader(
            dataset=self.dataset,
            batch_size=self.pool_size,
            shuffle=False,  # Shuffling is done in dataset
            num_workers=self.num_workers,
            collate_fn=self.collate_fn
        ))
        self.pool = next(init_dataloader)
        self._losses = torch.ones(self.pool_size) * torch.inf

    def next_batch(self) -> DataSample:
        idx = torch.randint(high=self.pool_size, size=(self.batch_size,))
        sample = self.pool[idx]
        self._last_idx = idx

        # Replace worst
        self._current_replaces += self.replace_worst_n
        if self._current_replaces > 0:
            scores = self.eviction_policy(sample, self._losses[idx])
            sorted_idx = torch.argsort(scores, descending=True)
            sample[sorted_idx[:int(self._current_replaces)]] = next(self.dataloader)
            self._current_replaces -= int(self._current_replaces)

        return sample.clone().to(self.device)


    def feedback(self, data_sample: DataSample, new_state: torch.Tensor, loss: LossResult):
        if self.warmup > 0:
            self.warmup -= 1
            return
        idx = self._last_idx
        self._losses[idx] = loss.batchwise_loss().detach().to("cpu")
        self.pool[idx] = data_sample.to("cpu")

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["pool_size"] = self.pool_size
        cfg["replace_worst_n"] = self.replace_worst_n
        cfg["eviction_policy"] = self.eviction_policy.to_config_dict()
        cfg["warmup"] = self.warmup

        return cfg
