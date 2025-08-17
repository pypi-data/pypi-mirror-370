import random
from pathlib import Path
from typing import Optional, Callable, Any

import torch

from ncalib.seed_factory.genome import GenomeSeedFactory
from ncalib.trainer.dataset import DataSample, NCA_SteppedDataset
from ncalib.utils.color_space import rgba_loader
from ncalib.utils.utils import to_binary_list


def load_targets(folder: Path, loader, transform, *, choose_k: Optional[int] = None) -> dict[int, torch.Tensor]:
    res = {}
    for image_path in folder.iterdir():
        if not image_path.is_file():
            continue

        image_id = int(image_path.stem)
        image = loader(image_path)
        image = transform(image)
        res[image_id] = image

    if choose_k is not None:
        keys = list(res.keys())
        random.shuffle(keys)
        for key in keys[choose_k:]:
            res.pop(key)
        assert len(res) == choose_k

    return res


class GenomeDataset(NCA_SteppedDataset):
    def __init__(
            self,
            target_folder: Path | str,
            step_range: tuple[int, int],
            nca_channels: int,
            *,
            seed: Optional[int] = None,
            transform: Optional[Callable] = None,
            loader: Callable[[str], Any] = rgba_loader,
            choose_k: Optional[int] = None,
            deterministic: bool = False,
    ):
        super().__init__(step_range, seed=seed)
        self.target_folder = Path(target_folder)
        self.targets = load_targets(self.target_folder, loader, transform, choose_k=choose_k)
        self.choose_k = choose_k
        self.nca_channels = nca_channels

        # Properties
        self.target_keys = list(self.targets.keys())
        self.n_targets = len(self.targets)
        self.genome_size = len(f"{max(self.target_keys):b}")

        # Seed factory
        self.seed_factory = self.create_seed_factory(deterministic=deterministic)

    def __str__(self):
        return f"{self.__class__.__name__}({self.target_folder.name}, n_targets={self.n_targets}, genome_size={self.genome_size})"

    def create_seed_factory(self, *, deterministic=False) -> GenomeSeedFactory:
        single_target = list(self.targets.values())[0]
        C, W, H = single_target.shape

        return GenomeSeedFactory(
            visible_channels=slice(0, C),
            genome_channels=slice(C, C + self.genome_size),
            channels=self.nca_channels,
            width=W,
            height=H,
            deterministic=deterministic
        )

    def __call__(self) -> DataSample:
        num_step = self.generate_n_steps()

        idx = torch.randint(low=0, high=self.n_targets, size=(1,), generator=self.rng)
        key = self.target_keys[idx]
        target = self.targets[key]
        genome = to_binary_list(key, min_length=self.genome_size)

        state = self.seed_factory(1, genome=genome, device=target.device)

        return DataSample(state, target[None], num_step, training_regenerate=True, batch_size=[1])

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["target_folder"] = str(self.target_folder)
        cfg["choose_k"] = self.choose_k
        return cfg
