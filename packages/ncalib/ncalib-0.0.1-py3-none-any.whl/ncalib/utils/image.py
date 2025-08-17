import logging
from functools import cached_property
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import torch
from PIL.Image import Image
from torchvision import transforms


class RGBAImage:
    def __init__(self, rgba_target: torch.Tensor):
        """
        :param rgba_target: Tensor[4 x W x H]
        """
        if len(rgba_target.shape) != 3:
            raise ValueError("Target tensor has to have 3 dimensions")
        if rgba_target.shape[0] != 4:
            raise ValueError(f"Target tensor has to have 4 channels (rgba) (has {rgba_target.shape[0]} channels)")

        self.img = rgba_target

    # Constructors
    @classmethod
    def from_numpy(cls, image: np.ndarray) -> "RGBAImage":
        pass

    @classmethod
    def from_pillow(cls, image: np.ndarray) -> "RGBAImage":
        pass

    @classmethod
    def from_path(cls, path: Path | str) -> "RGBAImage":
        full_path = str(Path(path).absolute())
        logger = logging.getLogger(cls.__name__)
        logger.info(f"Attempting to load `{full_path}`")
        img_bgr = cv2.imread(full_path, cv2.IMREAD_UNCHANGED)

        if img_bgr is None:
            raise FileNotFoundError(full_path)

        if len(img_bgr.shape) == 2:  # Grayscale
            tensor = torch.unsqueeze(torch.from_numpy(img_bgr), dim=0)
            tensor = tensor.repeat([3, 1, 1])
        elif len(img_bgr.shape) == 3:  # RGB / RGBA
            img_rgb = np.copy(img_bgr)
            img_rgb[:, :, 0] = img_bgr[:, :, 2]
            img_rgb[:, :, 2] = img_bgr[:, :, 0]
            tensor = torch.from_numpy(img_rgb.transpose((2, 0, 1)))
        else:
            raise RuntimeError(f"Unknown format for img with shape {img_bgr.shape} -> `{img_bgr}`")

        # Add artificial alpha channel if needed
        if tensor.shape[0] == 3:
            logger.info("Adding artificial alpha channel")
            rgba_tensor = torch.ones((4, tensor.shape[1], tensor.shape[2])) * 255
            rgba_tensor[:3] = tensor
            tensor = rgba_tensor

        return RGBAImage(tensor / 255)

    # Basic properties
    @property
    def width(self):
        return self.img.shape[1]

    @property
    def height(self):
        return self.img.shape[2]

    # Image type conversions
    def as_numpy(self) -> np.ndarray:
        """
        :return: ndarray[W x H x 4] as BGRA
        """
        # TODO: Image orientation not correct
        return np.rot90(self.img.cpu().numpy().transpose((2, 1, 0))[::-1, ::-1, :3])[:, ::-1]

    def as_pillow(self) -> Image:
        return transforms.ToPILImage()(self.img)

    # == Single channels ==
    # RGBA
    @property
    def rgba_red(self) -> torch.Tensor:
        return self.img[0]

    @property
    def rgba_green(self) -> torch.Tensor:
        return self.img[1]

    @property
    def rgba_blue(self) -> torch.Tensor:
        return self.img[2]

    @property
    def rgba_alpha(self) -> torch.Tensor:
        return self.img[3]

    @cached_property
    def rgb_max(self) -> torch.Tensor:
        return torch.max(self.img[:3], dim=0).values

    @cached_property
    def rgb_min(self) -> torch.Tensor:
        return torch.min(self.img[:3], dim=0).values

    @cached_property
    def rgb_delta(self) -> torch.Tensor:
        return self.rgb_max - self.rgb_min

    # Modification
    def pad(
            self,
            padding: int,
    ) -> "RGBAImage":
        new_img = torch.zeros((4, self.width + padding * 2, self.height + padding * 2))
        new_img[:, padding:-padding, padding:-padding] = self.img

        return RGBAImage(new_img)

    def resize(
            self,
            width: int,
            height: Optional[int] = None,
    ) -> "RGBAImage":
        if height is None:
            aspect = self.width / self.height
            height = int(width / aspect)

        if width == self.width and height == self.height:
            new_img = self.img
        else:
            new_img = transforms.ToTensor()(self.as_pillow().resize((width, height)))

        return RGBAImage(new_img)

    def scale(
            self,
            scale: float,
    ) -> "RGBAImage":
        pil_image = self.as_pillow()
        new_width = int(pil_image.width * scale)
        new_height = int(pil_image.height * scale)

        return self.resize(new_width, new_height)


def gt_anomaly_percentage(ground_truth: torch.Tensor) -> float:
    return (torch.sum(ground_truth) / (ground_truth.shape[0] * ground_truth.shape[1])).item()


def target_id_from_path(path: str | Path) -> str:
    return Path(path).stem
