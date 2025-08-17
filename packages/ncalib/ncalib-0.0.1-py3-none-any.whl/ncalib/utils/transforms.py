from functools import wraps
from typing import Sequence

import torch


def discretize(bins: Sequence[float] = (1.5 / 255, 2.5 / 255, 3.5 / 255)):
    this_bins = bins

    @wraps(discretize)
    def wrapped(image: torch.Tensor):
        bins = torch.Tensor(this_bins)
        binned_labels = torch.bucketize(image, bins).squeeze()
        return binned_labels

    return wrapped
