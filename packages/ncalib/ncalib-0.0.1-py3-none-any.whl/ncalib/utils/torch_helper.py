import math
from pathlib import Path
from typing import Callable, Any, Optional, Iterable

import torch
import torch.nn as nn
from torch.utils.data import Dataset, IterableDataset, DataLoader
from torchvision.datasets import VisionDataset
from torchvision.datasets.folder import default_loader


def weight_init(m):
    """Custom weight init for Conv2D and Linear layers."""
    if isinstance(m, nn.Linear):
        nn.init.orthogonal_(m.weight.data)
        if hasattr(m.bias, "data"):
            m.bias.data.fill_(0.0)
    elif isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d):
        gain = nn.init.calculate_gain("relu")
        nn.init.orthogonal_(m.weight.data, gain * 1e-2)
        if hasattr(m.bias, "data"):
            m.bias.data.fill_(0.0)


def reset_conv2d(layer):
    n = layer.in_channels
    for k in layer.kernel_size:
        n *= k
    stdv = 1. / math.sqrt(n)
    layer.weight.data.uniform_(-stdv, stdv)
    if layer.bias is not None:
        layer.bias.data.uniform_(-stdv, stdv)


def cleanup_state_dict(state_dict) -> dict[str, torch.Tensor]:
    """
    Removes _orig_mod. which is introduced by torch.compile()
    :param state_dict:
    :return:
    """
    new_state_dict = dict()
    for key in state_dict:
        new_state_dict[key.replace("_orig_mod.", "")] = state_dict[key]

    return new_state_dict


def update_part_of_state(state: torch.Tensor, new_state: torch.Tensor, channels: slice) -> torch.Tensor:
    """
    Replaces a part of a state in a Torch-friendly manner so that gradients can be back propagated.
    :param state: original state that should be modified Tensor[B x C x W x H]
    :param new_state: new state only for the range that should be replaced [B x C' x W x H]
    :param channels: slice with the respective channels. Covers C' channels
    :return: Tensor[B x C x W x H]
    """
    device = state.device
    B, C, W, H = state.shape

    # Avoid replacements and circumvent by multiplying by 0 and adding new state
    with torch.no_grad():
        ones_output = torch.zeros((1, C, 1, 1), device=device)
        ones_output[:, channels] = 1
        zeros_output = 1 - ones_output

        expanded_new_state = torch.zeros_like(state, device=device)

    expanded_new_state[:, channels] = new_state

    return state * zeros_output + expanded_new_state * ones_output


class SimpleImageDataset(VisionDataset):
    def __init__(
            self,
            *paths: Path | str,
            transform: Optional[Callable] = None,
            loader: Callable[[str], Any] = default_loader,
            use_cache: bool = True
    ):
        super().__init__(Path().root, transform=transform)
        self.loader = loader
        self.paths = SimpleImageDataset.parse_paths(paths)
        self.use_cache = use_cache
        self._cache = {}

    def __getitem__(self, index) -> torch.Tensor:
        if index in self._cache and self.use_cache:
            return self._cache[index]

        path = self.paths[index]
        sample = self.loader(str(path))
        if self.transform is not None:
            sample = self.transform(sample)
        if self.use_cache:
            self._cache[index] = sample
        return sample

    def __len__(self):
        return len(self.paths)

    @classmethod
    def parse_paths(cls, paths: Iterable[Path | str]) -> list[Path]:
        result = []
        for path in paths:
            path = Path(path)
            if path.is_dir():
                result += [p for p in path.iterdir() if p.is_file()]
            else:
                result.append(path)

        return result


class EmitTargetsVisionDataset(VisionDataset):
    def __init__(self, dataset: VisionDataset):
        super().__init__("")
        self.dataset = dataset

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, item):
        image, target = self.dataset.__getitem__(item)
        return image

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.dataset.__repr__()})"


class EndlessIterableDataset(IterableDataset):
    def __init__(self, dataset: Dataset, *, generator: torch.Generator = None, shuffle=False):
        self.dataset = dataset
        if generator is None:
            self.rng = torch.Generator()
        else:
            self.rng = generator
        self.shuffle = shuffle

    def __iter__(self):
        dataloader = DataLoader(self.dataset, batch_size=None, shuffle=self.shuffle, generator=self.rng)
        while True:
            for item in dataloader:
                yield item
