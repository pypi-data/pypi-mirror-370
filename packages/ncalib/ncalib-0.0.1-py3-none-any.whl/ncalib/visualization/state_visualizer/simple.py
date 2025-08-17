from typing import Optional

import numpy as np
import torch
import torchvision.utils
from jaxtyping import Integer, Float
import matplotlib.pyplot as plt

from ncalib.visualization.state_visualizer import BatchedStateVisualizer


class RGBVisualizer(BatchedStateVisualizer):
    def __init__(
            self,
            *,
            red_channel: int = 0,
            green_channel: int = 1,
            blue_channel: int = 2,
            alpha_channel: Optional[int] = None,
            batch_slice=slice(None, None, None),
            name: str = "RGB"
    ):
        super().__init__(name=name, batch_slice=batch_slice)
        self.red_channel = red_channel
        self.green_channel = green_channel
        self.blue_channel = blue_channel
        self.alpha_channel = alpha_channel

    def _batch_to_visualization(self, batch: torch.Tensor) -> dict[str, torch.Tensor]:
        """
        :param batch: Tensor[B x C x W x H]
        :return: dict[name -> Tensor[B x 3/4 x W x H] with float ranges 0..1 in RGB, RGBA
        """
        channels = [self.red_channel, self.green_channel, self.blue_channel]
        if self.alpha_channel is not None:
            channels += [self.alpha_channel]
        rgb_channels = batch[:, channels]
        return {
            self.name: rgb_channels
        }


class SeparateChannelVisualizer(BatchedStateVisualizer):
    def __init__(
            self,
            channels: slice = slice(None, None, None),
            *,
            cmap: Optional[str] = 'viridis',
            vmin: Optional[float] = None,
            vmax: Optional[float] = None,
            name: str = "Channels",
            batch_slice=slice(None, None, None),
    ):
        super().__init__(name=name, batch_slice=batch_slice)

        self.channels = channels
        self.cmap = cmap
        self.vmin = vmin
        self.vmax = vmax

    def _batch_to_visualization(
            self,
            batch: Float[torch.Tensor, "B C W H"]
    ) -> dict[str, Integer[np.ndarray, "B 3 W' H'"] | Float[torch.Tensor, "B 1 W' H'"]]:
        """
        :param batch: Tensor[B x C x W x H]
        :return: dict[name -> Tensor[B x 1 x W' x H'] with float ranges 0..1 in Gray
        """
        batched_results = []
        channels = batch.shape[1]
        n_rows = int(channels ** 0.5)
        for image in batch[:, self.channels]:
            # image: Tensor[C x W x H]
            image_unsqueezed = image.unsqueeze(1)
            # image_unsqueezed: Tensor [C x 1 x W x H]
            grid_image = torchvision.utils.make_grid(image_unsqueezed, nrow=n_rows)[:1]  # Helper creates RGB image
            # grid_image: Tensor[1 x W' x H']
            batched_results.append(grid_image)
        return {self.name: self._apply_cmap(torch.stack(batched_results, dim=0))}

    def _apply_cmap(self, batched_results: Float[torch.Tensor, "B 1 W H"]) -> Integer[np.ndarray, "B 3 W H"] | Float[
        torch.Tensor, "B 1 W H"]:
        if self.cmap is None:
            return batched_results

        # Normalize the tensor values
        vmin = batched_results.min() if self.vmin is None else self.vmin
        vmax = batched_results.max() if self.vmax is None else self.vmax
        batched_results_normalized = (batched_results - vmin) / (vmax - vmin)

        # Get the colormap
        cmap = plt.get_cmap(self.cmap)

        # Apply the colormap
        tensor_colored = []
        for t in batched_results_normalized:
            # Convert to numpy and apply colormap
            t_np = t.squeeze().detach().cpu().numpy()
            t_colored_np = cmap(t_np)[:, :, :3]  # Get RGB channels

            tensor_colored.append(t_colored_np)

        tensor_colored = np.stack(tensor_colored)
        return (tensor_colored * 255).astype(np.uint8)


class DeltaMagnitudeVisualizer(BatchedStateVisualizer):
    def __init__(
            self,
            *,
            channels: slice = slice(None, None, None),
            batch_slice=slice(None, None, None),
            normalize: bool = True,
            name: str = "Delta Magnitude"
    ):
        super().__init__(name=name, batch_slice=batch_slice)
        self.channels = channels

        self.normalize = normalize
        self._old_batch = None

    def _batch_to_visualization(self, batch: torch.Tensor) -> dict[str, torch.Tensor]:
        """
        :param batch: Tensor[B x C x W x H]
        :return: dict[name -> Tensor[B x 1 x W x H] with float ranges 0..1 in Gray

        """
        if self._old_batch is None:
            self._old_batch = torch.zeros_like(batch)

        magnitudes = torch.sqrt(torch.sum((batch[:, self.channels] - self._old_batch) ** 2, dim=1, keepdim=True))
        if self.normalize:
            magnitudes = (magnitudes - magnitudes.min()) / (magnitudes.max() - magnitudes.min())
        self._old_batch = batch
        return {self.name: magnitudes}
