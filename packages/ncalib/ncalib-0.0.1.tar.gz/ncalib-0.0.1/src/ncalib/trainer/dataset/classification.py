from typing import Optional, Any

import torch
from torch.nn import functional as F
from torch.utils.data import Dataset, DataLoader

from ncalib.seed_factory import NCA_SeedFactory
from ncalib.trainer.dataset import NCA_SteppedDataset, DataSample
from ncalib.utils.torch_helper import EndlessIterableDataset


class ClassificationDataset(NCA_SteppedDataset):
    def __init__(
            self,
            dataset: Dataset,  # Expect to yield tuple[image, label], where label is number of class
            num_classes: int,
            seed_factory: NCA_SeedFactory,
            *,
            step_range: tuple[int, int],
            use_one_hot_encoding: bool = False,
            dataset_channel_offset: int = 0,
            seed: Optional[int] = None,
            data_sample_base_class = DataSample,
    ):
        super().__init__(step_range, seed=seed)
        self.dataset = dataset
        self.dataset_dataloader = iter(
            DataLoader(
                EndlessIterableDataset(dataset, generator=self.rng, shuffle=True),
            )
        )
        self.dataset_channel_offset = dataset_channel_offset
        self.num_classes = num_classes
        self.seed_factory = seed_factory
        self.use_one_hot_encoding = use_one_hot_encoding
        self.data_sample_base_class = data_sample_base_class

    def __call__(self) -> DataSample:
        num_step = self.generate_n_steps()

        image, original_label = next(self.dataset_dataloader)
        B, C, W, H = image.shape
        # image: [B=1 x C x W x H]; label: [B] or [B x W x H]
        state = self.seed_factory(1, device="cpu")
        state[:, self.dataset_channel_offset:self.dataset_channel_offset + C] = image

        if len(original_label.shape) == 1:  # Only a single class per batch -> Reshape to image dimensions
            label = original_label[:, None, None].repeat(B, W, H)
        elif len(original_label.shape) == 4 and original_label.shape[1] == 1:  # Label has a squeezable dimension
            label = original_label[:, 0]
        else:
            label = original_label

        if not ((B, W, H) == label.shape):
            raise ValueError(
                f"Invalid shapes. "
                f"Image shape: {image.shape}, "
                f"Label shape: {label.shape} "
                f"(original: {original_label.shape})"
            )

        if B != 1:
            raise RuntimeError(f"Batch size should be 1. (is {B}; Shape: {image.shape})")

        # label: [B x W x H]
        if self.use_one_hot_encoding:
            target = F.one_hot(label.to(torch.int64), num_classes=self.num_classes)
            # target: Tensor[1 x W x H x N]
            target = target.permute(0, 3, 1, 2)
            # target: Tensor[1 x N x W x H]
        else:
            target = label

        return self.data_sample_base_class(
            state,
            torch.as_tensor(target, dtype=torch.float),
            num_step,
            batch_size=[B],
            training_regenerate=torch.as_tensor([False]*B)
        )

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["dataset"] = self.dataset.__class__.__name__
        cfg["num_classes"] = self.num_classes
        cfg["use_one_hot_encoding"] = self.use_one_hot_encoding
        cfg["seed_factory"] = self.seed_factory.to_config_dict()
        cfg["dataset_channel_offset"] = self.dataset_channel_offset
        return cfg


class GlobalClassificationDataset(NCA_SteppedDataset):
    def __init__(
            self,
            dataset: Dataset,  # Expect to yield tuple[image, label], where label is number of class
            num_classes: int,
            seed_factory: NCA_SeedFactory,
            *,
            step_range: tuple[int, int],
            use_one_hot_encoding: bool = False,

            seed: Optional[int] = None,
    ):
        super().__init__(step_range, seed=seed)
        self.dataset = dataset
        self.dataset_dataloader = iter(
            DataLoader(
                EndlessIterableDataset(dataset, generator=self.rng, shuffle=True),
            )
        )
        self.num_classes = num_classes
        self.seed_factory = seed_factory
        self.use_one_hot_encoding = use_one_hot_encoding

    def __call__(self) -> DataSample:
        num_step = self.generate_n_steps()

        image, original_label = next(self.dataset_dataloader)
        B, C, W, H = image.shape
        # image: [B=1 x C x W x H]; label: [B] or [B x W x H]
        state = self.seed_factory(1, device="cpu")
        state[:, :C] = image

        if len(original_label.shape) == 1:  # Only a single class per batch -> Reshape to image dimensions
            label = original_label[:, None, None].repeat(B, W, H)
        elif len(original_label.shape) == 4 and original_label.shape[1] == 1:  # Label has a squeezable dimension
            label = original_label[:, 0]
        else:
            label = original_label

        if not ((B, W, H) == label.shape):
            raise ValueError(
                f"Invalid shapes. "
                f"Image shape: {image.shape}, "
                f"Label shape: {label.shape} "
                f"(original: {original_label.shape})"
            )

        if B != 1:
            raise RuntimeError(f"Batch size should be 1. (is {B}; Shape: {image.shape})")

        # label: [B x W x H]
        if self.use_one_hot_encoding:
            target = F.one_hot(label.to(torch.int64), num_classes=self.num_classes)
            # target: Tensor[1 x W x H x N]
            target = target.permute(0, 3, 1, 2)
            # target: Tensor[1 x N x W x H]
        else:
            target = label

        return DataSample(
            state,
            torch.as_tensor(target, dtype=torch.float),
            num_step,
            batch_size=[B],
            training_regenerate=False
        )
