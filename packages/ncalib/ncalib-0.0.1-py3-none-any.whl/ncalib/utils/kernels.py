from typing import Literal

import numpy as np
import torch
import torch.nn.functional as F


def simple_2d_convolution(image, kernel):
    """
    :param image:  Tensor[W x H]
    :param kernel: Tensor[W' x H']
    :return: Tensor[W - W'//2 x H - H'//2]
    """
    return F.conv2d(
        torch.unsqueeze(torch.unsqueeze(image, dim=0), dim=0).float(),
        kernel.repeat(1, 1, 1, 1).float(), groups=1, padding=0
    )[0, 0]


def batched_convolution_2D(
        source: torch.Tensor,
        kernel: torch.Tensor,
        padding_mode: Literal["constant", "reflect", "replicate", "circular"] = "replicate"
) -> torch.Tensor:
    """
    :param source: Tensor[B x N x W x H]
    :param kernel: Tensor[W' x H']
    :param padding_mode:
    :return: Tensor[B x N x W x H]
    """
    # Check input sizes
    if not len(kernel.shape) == 2:
        raise ValueError("Kernel has to be 2D (W x H)")

    if not len(source.shape) == 4:
        raise ValueError("Source has to be 4D (B x n x W x H)")

    n_metrics = source.shape[1]
    kernel_width, kernel_height = kernel.shape

    # Calculate padding
    top_pad = kernel_height // 2
    left_pad = kernel_width // 2
    bottom_pad = kernel_height - top_pad - 1
    right_pad = kernel_width - left_pad - 1

    # Convolution
    kernel = kernel.repeat(n_metrics, 1, 1, 1).float().to(source.device)
    padded = F.pad(source.float(), (top_pad, bottom_pad, left_pad, right_pad), mode=padding_mode)
    result = F.conv2d(padded, kernel, groups=n_metrics, padding=0)

    # Validate result
    if result.shape != source.shape:
        raise ArithmeticError(f"Something went wrong. Shape mismatch: src={source.shape}, res={result.shape}")

    return result


with torch.no_grad():
    # LaPlace
    # https://jblindsay.github.io/ghrg/Whitebox/Help/FilterLaplacian.html
    laplace_3x3_1 = torch.Tensor([[-1., -1., -1.], [-1., 8., -1.], [-1., -1., -1.]])
    laplace_3x3_2 = torch.Tensor([[0., -1., 0], [-1., 4., -1.], [0, -1., 0]])

    laplace_5x5 = torch.Tensor([
        [0., 0., -1., 0., 0.],
        [0., -1., -2., -1., 0.],
        [-1., -2., 17., -2., -1.],
        [0., -1., -2., -1., 0.],
        [0., 0., -1., 0., 0.],
    ])

    # Sobol
    sobol_x = torch.tensor([[1., 0, -1.], [2., 0, -2.], [1., 0, -1.]])
    sobol_y = torch.tensor([[1., 2., 1.], [0., 0., 0.], [-1., -2., -1.]])
    sobol_x5 = torch.tensor([
        [-1, -2, 0, 2, 1],
        [-4, -8, 0, 8, 4],
        [-6, -12, 0, 12, 6],
        [-4, -8, 0, 8, 4],
        [-1, -2, 0, 2, 1]
    ])
    sobol_y5 = torch.tensor([
        [-1, -4, -6, -4, -1],
        [-2, -8, -12, -8, -2],
        [0, 0, 0, 0, 0],
        [2, 8, 12, 8, 2],
        [1, 4, 6, 4, 1]
    ])

    zeros_3x3 = torch.zeros((3, 3))


# Gaussian Blur
def gaussian_blur(filter_size: int = 3, std: float = 3) -> torch.Tensor:
    if not (filter_size % 2) == 1:
        raise ValueError("Gaussian blur only works for odd filter sizes! (at least in this implementation...)")

    center = (filter_size - 1) / 2
    sigma2 = std ** 2
    i, j = np.indices((filter_size, filter_size), dtype=np.float64) - center

    filter_ = torch.as_tensor(np.exp(-(i ** 2 + j ** 2) / (2 * sigma2)) / (2 * np.pi * sigma2))
    return filter_.float() / torch.sum(filter_)


def block_kernel(size: int = 3) -> torch.Tensor:
    return torch.ones((size, size)).float()


# Surrounding mean
surrounding_mean_3x3 = torch.tensor([[2., 1., 2.], [1., 0., 1.], [2., 1., 2.]])
surrounding_mean_5x5 = torch.Tensor([
    [8., 4., 2., 4., 8.],
    [4., 2., 1., 2., 4.],
    [2., 1., 0., 1., 2.],
    [4., 2., 1., 2., 4.],
    [8., 4., 2., 4., 8.],
])

inward_mean_3x3 = torch.max(surrounding_mean_3x3) - surrounding_mean_3x3
inward_mean_5x5 = torch.max(surrounding_mean_5x5) - surrounding_mean_5x5

surrounding_mean_3x3 = surrounding_mean_3x3 / torch.sum(surrounding_mean_3x3)
surrounding_mean_5x5 = surrounding_mean_5x5 / torch.sum(surrounding_mean_5x5)
inward_mean_3x3 = inward_mean_3x3 / torch.sum(inward_mean_3x3)
inward_mean_5x5 = inward_mean_5x5 / torch.sum(inward_mean_5x5)
