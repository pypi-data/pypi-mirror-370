from typing import Optional

import torch

from ncalib.seed_factory import NCA_SeedFactory
from ncalib.utils.defaults import DEFAULT_DEVICE
from ncalib.utils.utils import slice_to_config, to_binary_list


class GenomeSeedFactory(NCA_SeedFactory):
    def __init__(
            self,
            genome_channels: slice,
            width: int = 64,
            channels: int = 16,
            height: Optional[int] = None,
            visible_channels: slice = slice(0, 3),
            deterministic=False
    ):
        super().__init__(width=width, height=height, channels=channels)
        self.visible_channels = visible_channels
        self.genome_channels = genome_channels
        self.deterministic = deterministic

    def __call__(
            self,
            n: int = 1,
            *,
            device=DEFAULT_DEVICE,
            genome: Optional[torch.Tensor | list[float]] = None
    ) -> torch.Tensor:
        seed = torch.zeros([n, self.channels, self.width, self.height], dtype=torch.float32, device=device)
        seed[:, self.visible_channels, self.width // 2, self.height // 2] = 1.0
        genome_place = seed[:, self.genome_channels, self.width // 2, self.height // 2]
        if genome is None:
            if self.deterministic:
                genome = torch.zeros_like(genome_place)
                for i in range(len(genome)):
                    genome[i] = torch.as_tensor(to_binary_list(i, min_length=len(genome[i])))
            else:
                genome = torch.randint_like(genome_place, 0, 2)

        else:
            # Check shape
            B, G = genome_place.shape
            genome = torch.as_tensor(genome, dtype=torch.float32)
            if len(genome.shape) == 1:
                # Expects to have genome that is same for all batches
                if not genome.shape[0] == G:
                    raise ValueError(f"Invalid genome size. Expects genome of size {G}, but got shape {genome.shape}")

                genome = genome[None]
            elif len(genome.shape) == 2:
                if not genome.shape == genome_place.shape:
                    raise ValueError(
                        f"Invalid genome size. "
                        f"Expects genome of size {genome_place.shape}, but got shape {genome.shape}"
                    )
        seed[:, self.genome_channels, self.width // 2, self.height // 2] = torch.as_tensor(genome, dtype=torch.float32)
        return seed

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["genome_channels"] = slice_to_config(self.genome_channels)
        cfg["visible_channels"] = slice_to_config(self.visible_channels)
        return cfg
