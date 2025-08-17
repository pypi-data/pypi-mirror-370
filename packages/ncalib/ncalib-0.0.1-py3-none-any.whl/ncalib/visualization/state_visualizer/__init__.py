import abc

import numpy as np
import torch

from ncalib.utils.utils import NCA_Base


class StateVisualizer(NCA_Base, abc.ABC):
    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def __call__(self, state: torch.Tensor) -> dict[str, np.ndarray]:
        """
        :param state: Tensor[B x C x W x H]
        :return: dictionary of {name: np.ndarray[B x W x H x 1/3/4]}
        """
        pass

    def __add__(self, other: "StateVisualizer") -> "StateVisualizer":
        # Prepare each visualizer so that each is an iterable of simple visualizations
        if isinstance(self, CombinedVisualizer):
            vis1 = self.visualizer
        else:
            vis1 = [self]

        if isinstance(other, CombinedVisualizer):
            vis2 = other.visualizer
        else:
            vis2 = [other]

        # Combine Visualizer
        return CombinedVisualizer(*vis1, *vis2)


class CombinedVisualizer(StateVisualizer):
    def __init__(
            self,
            *visualizer: StateVisualizer,
    ):
        super().__init__()
        self.visualizer: tuple[StateVisualizer] = tuple(visualizer)

    def __call__(self, state: torch.Tensor) -> dict[str, np.ndarray]:
        res = {}
        for visualizer in self.visualizer:
            res.update(visualizer(state))
        return res


class BatchedStateVisualizer(StateVisualizer, abc.ABC):
    def __init__(
            self,
            name: str,
            batch_slice=slice(None, None, None),
    ):
        super().__init__()
        self.name = name
        self.batch_slice: slice = batch_slice

    def __call__(self, state: torch.Tensor) -> dict[str, np.ndarray]:
        """
        :param state: Tensor[B x C x W x H]
        :return: dictionary of {name: np.ndarray[B x W x H x 1/3/4]} with ints 0.255 for Gray, BGR, BGRA
        """
        batch = state[self.batch_slice].detach()
        batch_size = batch.shape[0]

        visualization = self._batch_to_visualization(batch)
        # visualization is dict with key=name and value either:
        #   -> torch.Tensor[B x 1/3/4 x W' x H'] with floats 0..1 for Gray, RGB, RGBA
        #   -> np.ndarray[B x W' x H' x 1/3/4] with ints 0..255 for Gray, BGR, BGRA

        result = {}
        for key, image in visualization.items():
            if isinstance(image, torch.Tensor):
                image = (torch.clip(image, 0, 1) * 255).cpu().numpy().astype("uint8")  # 0..1 -> 0.255
                image = image.transpose((0, 2, 3, 1))  # [B x C x W' x H'] -> [B x W' x H' x C]

            if not isinstance(image, np.ndarray):
                raise TypeError(f"Expects image to be np.ndarray (it is {type(image)})")

            if not image.shape[3] in [1, 3, 4]:
                raise ValueError(f"Expects number of color channels to be 1,3 or 4 (image has shape of {image.shape})")

            result[key] = image
        return result

    @abc.abstractmethod
    def _batch_to_visualization(self, batch: torch.Tensor) -> dict[str, torch.Tensor | np.ndarray]:
        """
        :param batch: batched Tensor [B x C x W x H]
        :return: dict[
            name ->
                torch.Tensor[B x 1/3/4 x W x H] with float ranges 0..1 in Gray, RGB, RGBA
                np.ndarray[B x W x H x 1/3/4] with int ranges 0..255 in Gray, BGR, BGRA
            ]
        """
        pass
