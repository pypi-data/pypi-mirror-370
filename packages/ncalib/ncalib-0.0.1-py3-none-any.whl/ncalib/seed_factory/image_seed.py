import torch
import torchvision.datasets

from ncalib.seed_factory import NCA_SeedFactory
from ncalib.utils.defaults import DEFAULT_DEVICE
from ncalib.utils.utils import endless_generator, slice_to_config


class DatasetSeedFactory(NCA_SeedFactory):
    def __init__(
            self,
            dataset: torchvision.datasets.VisionDataset,
            *,
            image_channels: slice,
            width=None,
            channels=16,
            height=None,
            num_workers=2
    ):
        super().__init__(width=width, channels=channels, height=height)
        self.dataset = dataset
        self.dataloader = endless_generator(torch.utils.data.DataLoader(
            self.dataset,
            batch_size=1,
            shuffle=True,
            num_workers=num_workers,
        ))

        self.image_channels = image_channels

    def __call__(self, n: int = 1, *, device=DEFAULT_DEVICE) -> torch.Tensor:
        images = []
        dimensions = torch.zeros((n, 3), dtype=int)
        for i in range(n):
            image, label = next(self.dataloader)
            image = image[0]
            images.append(image)
            dimensions[i] = torch.as_tensor(image.shape)

        max_dimension = torch.max(dimensions, dim=0).values
        if self.width is not None:
            if self.width < max_dimension[0]:
                raise OverflowError(f"Fixed width is too small for images! (needs at least w,h of {max_dimension})")
            max_w = self.width
        else:
            max_w = max_dimension[1]

        if self.height is not None:
            if self.height < max_dimension[1]:
                raise OverflowError(f"Fixed height is too small for images! (needs at least w,h of {max_dimension})")
            max_h = self.height
        else:
            max_h = max_dimension[2]

        result = torch.zeros((n, self.channels, max_w, max_h))
        for i, (image, (c, w, h)) in enumerate(zip(images, dimensions)):
            pad_x = int((max_w - w) // 2)
            pad_y = int((max_h - h) // 2)
            result[i, self.image_channels, pad_x:pad_x + w, pad_y:pad_y + h] = image

        return result.to(device)

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["image_channels"] = slice_to_config(self.image_channels)
        return cfg
