from pathlib import Path
from typing import Optional, Any

import torch

from ncalib.trainer.target import NCA_Target
from ncalib.utils.color_space import RGBA, ColorClass
from ncalib.utils.defaults import DEFAULT_DEVICE
from ncalib.utils.image import RGBAImage


class TensorTarget(NCA_Target):
    def __init__(
            self,
            image: RGBAImage,
            *,
            device: torch.device | str = DEFAULT_DEVICE,
            source: Optional[str] = None,
            color_space: ColorClass = RGBA(True, True, True)
    ):
        super().__init__(device=device)
        if not isinstance(image, RGBAImage):
            raise TypeError(f"Expected RGBAImage. Got {type(image)} instead.")
        self.image: RGBAImage = image
        self.source: Optional[str] = source
        self.color_space = color_space

        self._target: Optional[torch.Tensor] = None

    def __call__(self, n=1) -> torch.Tensor:
        """ :return Tensor [n x C x W x H] """
        return self.target.repeat([n, 1, 1, 1])

    def __repr__(self) -> str:
        if self.source is None:
            return f"{self.__class__.__name__}({self.channels}x{self.width}x{self.height})"
        return f"{self.__class__.__name__}({self.channels}x{self.width}x{self.height}, source={self.source})"

    @property
    def target(self) -> torch.Tensor:
        if self._target is None:
            self._target: torch.Tensor = self.color_space(self.image).to(self.device)
        return self._target

    @property
    def channels(self) -> int:
        return self.target.shape[0]

    @property
    def width(self) -> int:
        return self.image.width

    @property
    def height(self) -> int:
        return self.image.height

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["color_space"] = self.color_space.to_config_dict()

        return cfg

    @classmethod
    def load_from_path(
            cls,
            *,
            path: Path | str,
            width: int = None,
            height: int = None,
            padding: int = 0,
            color_space: Optional[ColorClass] = None,  # Default RGBA, if alpha is used, otherwise RGB
            device: str | torch.device = DEFAULT_DEVICE,
    ) -> NCA_Target:
        # Load target
        path = Path(path)
        image = RGBAImage.from_path(path)

        # Use default colorspace=RGBA, if alpha channel is used, otherwise RGB
        if color_space is None:
            use_alpha = not torch.all(image.rgba_alpha == 1)  # If all values are 1, we can omit the alpha channel
            color_space = RGBA(True, True, True, alpha=use_alpha)

        # Resize
        image = image.resize(width, height)

        # Padding
        if padding > 0:
            image = image.pad(padding)

        target = TensorTarget(
            image=image,
            color_space=color_space,
            device=device,
            source=str(path)
        )
        return target
