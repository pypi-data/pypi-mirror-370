import abc
from typing import Optional, Any

import torch
from tensordict import tensorclass, TensorDict
from torch.utils.data import IterableDataset

from ncalib.trainer.loss_function import LossResult
from ncalib.utils.utils import NCA_Base, make_circle_masks


@tensorclass
class DataSample:
    states: torch.Tensor
    targets: torch.Tensor
    n_steps: torch.Tensor
    training_regenerate: bool

    def get_kwargs(self, required_kwargs) -> TensorDict:
        result = {}
        for kwarg in required_kwargs:
            if kwarg == "original_state":
                # This is provided by nca itself
                continue
            try:
                result[kwarg] = getattr(self, kwarg)
            except KeyError:
                raise KeyError(f"Could not find {kwarg} in {self.__class__.__name__} but is required kwarg!")

        return TensorDict(result, batch_size=self.batch_size)

    def update_sample(self, new_state: torch.Tensor, loss: LossResult):
        self.states = new_state.detach()
        # if self.training_regenerate:
        #     B, C, W, H = new_state.shape
        #     circle_mask = make_circle_masks(B, W, H)
        #     self.states *= (1 - circle_mask.to(new_state.device))[:, None]

    @classmethod
    def merge_batch(cls, samples: list["DataSample"]) -> "DataSample":
        return torch.cat(samples, dim=0)


class NCA_Dataset(NCA_Base, IterableDataset, abc.ABC):
    def __init__(
            self,
            *,
            seed: Optional[int] = None,
    ):
        super().__init__()

        # rng is always for cpu
        self.rng = torch.Generator(device="cpu")
        if seed is not None:
            self.rng.manual_seed(seed)
        else:
            self.rng.seed()

    def __iter__(self):
        while True:
            yield self()

    @abc.abstractmethod
    def __call__(self) -> DataSample:
        """
        :return:
        DataSample consisting of at least:
            - state: Tensor[B x C x W x H]
            - target: Tensor[B x C' x W x H]
            - number_of_steps: Tensor[B]
        """
        pass


class NCA_SteppedDataset(NCA_Dataset):
    def __init__(self, step_range: tuple[int, int], *, seed: Optional[int]):
        super().__init__(seed=seed)
        self.step_range_min, self.step_range_max = step_range

    def generate_n_steps(self):
        return torch.randint(
            low=self.step_range_min,
            high=self.step_range_max + 1,
            size=(1,),
            generator=self.rng,
        )

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["step_range"] = (self.step_range_min, self.step_range_max)
        return cfg
