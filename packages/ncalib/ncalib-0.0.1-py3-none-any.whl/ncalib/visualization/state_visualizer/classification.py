import cv2
import torch

from ncalib.utils.utils import length_of_slice
from ncalib.visualization.state_visualizer import BatchedStateVisualizer
import colorsys

def get_colormap(n, device="cpu"):
    # Evenly space n hues over [0,1), full saturation and brightness.
    colormap = [colorsys.hsv_to_rgb(i / n, 1.0, 1.0) for i in range(n)]
    # Return tensor with shape [3, n] so that indexing with labels gives [3, W, H]
    return torch.tensor(colormap, device=device, dtype=torch.float32)

class ClassificationVisualizer(BatchedStateVisualizer):
    def __init__(
            self,
            channels: slice,
            *,
            colormap: int = cv2.COLORMAP_SUMMER,
            name: str = "Classification",
            batch_slice=slice(None, None, None),
            mask_channels: slice | int = 0
    ):
        super().__init__(name=name, batch_slice=batch_slice)

        self.channels = channels
        if isinstance(mask_channels, int):
            mask_channels = slice(mask_channels, mask_channels + 1)
        self.mask_channels = mask_channels
        self.num_classes = length_of_slice(self.channels)

        self.colormap = get_colormap(self.num_classes).T

    def _batch_to_visualization(self, batch: torch.Tensor) -> dict[str, torch.Tensor]:
        """
        :param batch: Tensor[B x C x W x H]
        :return: dict[name -> Tensor[B x 1 x W x H] with float ranges 0..1 in Gray
        """
        batched_results = []
        batched_channels = batch[:, self.channels]
        masked_channels = batch[:, self.mask_channels]

        B, C, W, H = batch.shape

        self.colormap = self.colormap.to(batch.device)

        for channels, mask in zip(batched_channels, masked_channels):
            # softmax = torch.softmax(channels, dim=0)
            arg_max = torch.argmax(channels, dim=0)
            result = torch.zeros((3, W, H), device=batch.device)
            result += self.colormap[:, arg_max]
            # result = torch.einsum("sij, sc-> cij", softmax, colors)
            result *= torch.mean(mask, dim=0)
            batched_results.append(result)

        return {self.name: torch.stack(batched_results, dim=0)}
