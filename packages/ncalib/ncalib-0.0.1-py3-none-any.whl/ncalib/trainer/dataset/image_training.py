from typing import Optional, Any

from torch.utils.data import Dataset, DataLoader

from ncalib.seed_factory import NCA_SeedFactory
from ncalib.trainer.dataset import DataSample, NCA_SteppedDataset
from ncalib.utils.torch_helper import EndlessIterableDataset
from ncalib.utils.utils import dataset_to_config


class ImageTrainingDataset(NCA_SteppedDataset):
    def __init__(
            self,
            seed_factory: NCA_SeedFactory,
            target: Dataset,
            *,
            step_range: tuple[int, int],
            training_regenerate=False,
            seed: Optional[int] = None,
    ):
        super().__init__(step_range, seed=seed)
        self.seed_factory = seed_factory
        self.target = target
        self.target_dataloader = iter(
            DataLoader(
                EndlessIterableDataset(target, generator=self.rng, shuffle=True),
            )
        )
        self.training_regenerate = training_regenerate

    def __call__(self) -> DataSample:
        num_step = self.generate_n_steps()

        state = self.seed_factory(1, device="cpu")
        target = next(self.target_dataloader)

        return DataSample(state, target, num_step, training_regenerate=[self.training_regenerate], batch_size=[1])

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["seed_factory"] = self.seed_factory.to_config_dict()
        cfg["target"] = dataset_to_config(self.target)
        cfg["training_regenerate"] = self.training_regenerate
        return cfg


