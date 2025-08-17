import dataclasses
import math
from dataclasses import dataclass

import torch
from PIL import Image

from ncalib.utils.image import RGBAImage
from ncalib.utils.utils import full_class_name


def rgba_loader(path):
    with open(path, "rb") as f:
        img = Image.open(f)
        return img.convert("RGBA")

def rgba_loader_with_aux(path):
    image = rgba_loader(path)
    return image


class NoColorChannelSelectedException(Exception):
    pass


@dataclass(frozen=True)
class ColorClass:
    def __call__(self, rgba_image: RGBAImage) -> torch.Tensor:
        result_list = []
        for channel_name in self.__class__.__dataclass_fields__.keys():
            # channel_value can be either ColorClass or bool
            channel_value = getattr(self, channel_name)

            if isinstance(channel_value, ColorClass):  # Case recursive ColorClass
                try:
                    channels = channel_value(rgba_image)
                except NoColorChannelSelectedException:
                    continue

                for channel in channels:
                    result_list.append(channel)
            elif channel_value is True:  # Case True
                channel_conversion = getattr(self, f"_{channel_name}", None)
                if channel_conversion is None:
                    raise NotImplementedError(f"{self.__class__} has no converter for channel {channel_name}")
                channel = channel_conversion(rgba_image)
                result_list.append(channel)
            elif channel_value is not False:  # Unknown type
                raise TypeError(f"Cannot identify value {channel_value} for {channel_name}")

        if len(result_list) == 0:
            raise NoColorChannelSelectedException()
        return torch.stack(result_list)

    def __len__(self) -> int:
        return len(self.names)  # Shortcut... Might be more efficient if done properly

    @property
    def names(self) -> list[str]:
        names = []
        for channel_name in self.__class__.__dataclass_fields__.keys():
            # channel_value can be either ColorClass or bool
            channel_value = getattr(self, channel_name)

            if isinstance(channel_value, ColorClass):  # Case recursive ColorClass
                names += channel_value.names
            elif channel_value is True:  # Case True
                names.append(f"{self.__class__.__name__}.{channel_name}")
            elif channel_value is not False:  # Unknown type
                raise TypeError(f"Cannot identify value {channel_value} for {channel_name}")

        return names

    def to_config_dict(self):
        cfg = {
            "_target_": full_class_name(self)
        }
        cfg.update(dataclasses.asdict(self))
        return cfg


@dataclass(frozen=True)
class RGBA(ColorClass):
    red: bool = False
    green: bool = False
    blue: bool = False
    alpha: bool = False

    @classmethod
    def _red(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return rgba_image.rgba_red

    @classmethod
    def _green(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return rgba_image.rgba_green

    @classmethod
    def _blue(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return rgba_image.rgba_blue

    @classmethod
    def _alpha(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return rgba_image.rgba_alpha


@dataclass(frozen=True)
class HSV(ColorClass):
    """ https://en.wikipedia.org/wiki/HSL_and_HSV """
    hue: bool = False
    saturation: bool = False
    value: bool = False

    @classmethod
    def _hue(cls, rgba_image: RGBAImage) -> torch.Tensor:
        hue = torch.zeros((rgba_image.width, rgba_image.height))
        case_r = rgba_image.rgb_max == rgba_image.rgba_red
        case_g = rgba_image.rgb_max == rgba_image.rgba_green
        case_b = rgba_image.rgb_max == rgba_image.rgba_blue
        hue[case_r] = torch.remainder((rgba_image.rgba_green - rgba_image.rgba_blue) / rgba_image.rgb_delta, 6)[case_r]
        hue[case_g] = ((rgba_image.rgba_blue - rgba_image.rgba_red) / rgba_image.rgb_delta + 2)[case_g]
        hue[case_b] = ((rgba_image.rgba_red - rgba_image.rgba_green) / rgba_image.rgb_delta + 4)[case_b]
        return torch.nan_to_num(hue, 0) / 6

    @classmethod
    def _saturation(cls, rgba_image: RGBAImage) -> torch.Tensor:
        values = rgba_image.rgb_delta / HSV._value(rgba_image)
        return torch.clip(torch.nan_to_num(values, 0), min=0, max=1)

    @classmethod
    def _value(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return rgba_image.rgb_max


@dataclass(frozen=True)
class HSL(ColorClass):
    """ https://en.wikipedia.org/wiki/HSL_and_HSV """
    hue: bool = False
    saturation: bool = False
    luminance: bool = False

    @classmethod
    def _hue(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return HSV._hue(rgba_image)

    @classmethod
    def _saturation(cls, rgba_image: RGBAImage) -> torch.Tensor:
        values = rgba_image.rgb_delta / (1 - torch.abs(2 * HSL._luminance(rgba_image) - 1))
        return torch.clip(torch.nan_to_num(values, 0), min=0, max=1)

    @classmethod
    def _luminance(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return (rgba_image.rgb_max + rgba_image.rgb_min) / 2


@dataclass(frozen=True)
class HSI(ColorClass):
    hue: bool = False
    saturation: bool = False
    intensity: bool = False

    @classmethod
    def _hue(cls, rgba_image: RGBAImage) -> torch.Tensor:
        """ https://en.wikipedia.org/wiki/Hue#Defining_hue_in_terms_of_RGB """
        alpha = 2 * rgba_image.rgba_red - rgba_image.rgba_green - rgba_image.rgba_blue
        beta = math.sqrt(3) * (rgba_image.rgba_green - rgba_image.rgba_blue)
        values = torch.atan2(beta, alpha)

        # Normalize between 0..1
        return (values + math.pi) / (2 * math.pi)

    @classmethod
    def _saturation(cls, rgba_image: RGBAImage) -> torch.Tensor:
        res = 1 - rgba_image.rgb_min / cls._intensity(rgba_image)
        return torch.clip(torch.nan_to_num(res, 0), min=0)

    @classmethod
    def _intensity(cls, rgba_image: RGBAImage) -> torch.Tensor:
        """ Unweighted Gray """
        return torch.mean(rgba_image.img[:3], dim=0)  # "Gray"


@dataclass(frozen=True)
class CMYK(ColorClass):
    cyan: bool = False
    magenta: bool = False
    yellow: bool = False
    key: bool = False

    @classmethod
    def _key(cls, rgba_image: RGBAImage):
        return 1 - rgba_image.rgb_max

    @classmethod
    def _cyan(cls, rgba_image: RGBAImage) -> torch.Tensor:
        res = (rgba_image.rgb_max - rgba_image.rgba_red) / rgba_image.rgb_max
        return torch.nan_to_num(res, 0)

    @classmethod
    def _magenta(cls, rgba_image: RGBAImage) -> torch.Tensor:
        res = (rgba_image.rgb_max - rgba_image.rgba_green) / rgba_image.rgb_max
        return torch.nan_to_num(res, 0)

    @classmethod
    def _yellow(cls, rgba_image: RGBAImage) -> torch.Tensor:
        res = (rgba_image.rgb_max - rgba_image.rgba_blue) / rgba_image.rgb_max
        return torch.nan_to_num(res, 0)


@dataclass(frozen=True)
class YUV(ColorClass):
    """ https://en.wikipedia.org/wiki/YUV """
    _V_max = 0.615
    _U_max = 0.436
    y: bool = False
    u: bool = False
    v: bool = False

    @classmethod
    def _y(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return 0.299 * rgba_image.rgba_red + 0.587 * rgba_image.rgba_green + 0.114 * rgba_image.rgba_blue

    @classmethod
    def _u(cls, rgba_image: RGBAImage) -> torch.Tensor:
        values = -0.14713 * rgba_image.rgba_red + -0.28886 * rgba_image.rgba_green + 0.436 * rgba_image.rgba_blue
        return (values + cls._U_max) / (2 * cls._U_max)

    @classmethod
    def _v(cls, rgba_image: RGBAImage) -> torch.Tensor:
        values = 0.615 * rgba_image.rgba_red + -0.51499 * rgba_image.rgba_green + -0.10001 * rgba_image.rgba_blue
        return (values + cls._V_max) / (2 * cls._V_max)


@dataclass(frozen=True)
class RG_Chromaticity(ColorClass):
    """ https://en.wikipedia.org/wiki/Rg_chromaticity """
    red: bool = False
    green: bool = False
    blue: bool = False

    @classmethod
    def _red(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return torch.nan_to_num(rgba_image.rgba_red / torch.sum(rgba_image.img[:3], dim=0), 0)

    @classmethod
    def _green(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return torch.nan_to_num(rgba_image.rgba_green / torch.sum(rgba_image.img[:3], dim=0), 0)

    @classmethod
    def _blue(cls, rgba_image: RGBAImage) -> torch.Tensor:
        # Edge case: B' = 1 - R' - G' -> if R + G + B == 0 -> B' = 1
        return torch.nan_to_num(rgba_image.rgba_blue / torch.sum(rgba_image.img[:3], dim=0), 1)


@dataclass(frozen=True)
class TSL(ColorClass):
    """ https://en.wikipedia.org/wiki/TSL_color_space """
    tint: bool = False
    saturation: bool = False
    lightness: bool = False

    @classmethod
    def _tint(cls, rgba_image: RGBAImage) -> torch.Tensor:
        r_ = RG_Chromaticity._red(rgba_image) - 1 / 3
        g_ = RG_Chromaticity._green(rgba_image) - 1 / 3
        tint = torch.zeros((rgba_image.width, rgba_image.height))

        case_1 = g_ > 0
        case_2 = g_ < 0
        tint[case_1] = (torch.arctan(r_ / g_ + 1 / 4) / (2 * torch.pi))[case_1]
        tint[case_2] = (torch.arctan(r_ / g_ + 3 / 4) / (2 * torch.pi))[case_2]
        return (torch.nan_to_num(tint, 0) + 0.25) * 2  # / (2 * math.pi)

    @classmethod
    def _saturation(cls, rgba_image: RGBAImage) -> torch.Tensor:
        r_ = rgba_image.rgba_red - 1 / 3
        g_ = rgba_image.rgba_red - 1 / 3
        return torch.sqrt(9 / 5 * (r_ ** 2 + g_ ** 2)) / math.sqrt(1.6)

    @classmethod
    def _lightness(cls, rgba_image: RGBAImage) -> torch.Tensor:
        return 0.299 * rgba_image.rgba_red + 0.587 * rgba_image.rgba_green + 0.114 * rgba_image.rgba_blue


@dataclass(frozen=True)
class ColorSpace(ColorClass):
    rgba: RGBA = RGBA()
    hsv: HSV = HSV()
    hsl: HSL = HSL()
    hsi: HSI = HSI()
    cmyk: CMYK = CMYK()
    yuv: YUV = YUV()
    rg_chromaticity: RG_Chromaticity = RG_Chromaticity()
    tsl: TSL = TSL()
