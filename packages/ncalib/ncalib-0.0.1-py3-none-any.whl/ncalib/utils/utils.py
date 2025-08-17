import logging
import math
import random
import warnings
from dataclasses import is_dataclass, asdict
from pathlib import Path
from typing import Any, Literal, Callable, Optional, Iterable, Iterator

import git
import numpy as np
import torch
import torchvision
from flatten_dict import flatten
from git import InvalidGitRepositoryError
from omegaconf import OmegaConf, DictConfig
from torch.backends import cudnn
from torch.utils.data import Dataset

from ncalib.utils.torch_helper import SimpleImageDataset


class NCA_Base:
    LOG_LEVEL = logging.DEBUG

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.level = NCA_Base.LOG_LEVEL

    def __repr__(self):
        init_code = self.__init__.__code__
        args = ", ".join([
            f"{k}={getattr(self, k, '???')}"
            for k in init_code.co_varnames[1:init_code.co_argcount]
        ])
        return f"{self.__class__.__name__}({args})"

    def reset(self):
        pass

    def to_config_dict(self) -> dict[str, Any]:
        return {"_target_": full_class_name(self)}


def add_prefix_to_keys(obj: dict[str, Any], prefix: str) -> dict[str, Any]:
    return {prefix + key: value for key, value in obj.items()}


def config_as_flat_dict(
        cfg: Any,
        *,
        reducer: Literal["underscore", "tuple", "dot", "path"] | Callable[[Any, Any], str] = "underscore"
) -> dict[str, Any]:
    # Make dict
    if is_dataclass(cfg):
        cfg_dict = asdict(cfg)
    elif isinstance(cfg, (OmegaConf, DictConfig)):
        cfg_dict = OmegaConf.to_container(cfg, resolve=True, enum_to_str=True)
    else:
        cfg_dict = dict(cfg)

    # Flatten
    return flatten(cfg_dict, reducer=reducer)


def own_logspace(start: float, end: float, steps: int) -> torch.Tensor:
    return torch.logspace(math.log10(start), math.log10(end), steps)


def fix_seed(seed: Optional[int], *, deterministic=True):
    logger = logging.getLogger("Seed")
    if seed is None:
        logger.warning(f"No seed provided!")
        return

    logger.info(f"Fix seed to {seed}.")
    torch.manual_seed(seed)
    np.random.seed(seed + 1)
    random.seed(seed + 2)

    if deterministic:
        cudnn.deterministic = True
        logger.warning("You have chosen to seed training. "
                       "This will turn on the CUDNN deterministic setting, "
                       "which can slow down your training considerably! "
                       "You may see unexpected behavior when restarting "
                       "from checkpoints.")


def endless_generator(iterable: Iterable) -> Iterator:
    while True:
        for element in iterable:
            yield element


def length_of_slice(s: slice) -> int:
    if not s.stop:
        raise ValueError(f"Cannot get length of indefinite slice: {s}")
    n = s.stop
    if s.start:
        n -= s.start
    if s.step:
        n = int(n // s.step)

    return n


def full_class_name(o: object) -> str:
    # https://stackoverflow.com/a/13653312
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:  # Check for __builtin__
        return o.__class__.__name__
    return f'{module}.{o.__class__.__name__}'


def slice_to_config(s: slice) -> Optional[dict[str, Any]]:
    if s is None:
        return None
    return {
        "_target_": f"{to_slice.__module__}.{to_slice.__name__}",
        "start": s.start,
        "stop": s.stop,
        "step": s.step,
    }


def optimizer_to_config(optimizer: torch.optim.Optimizer) -> dict[str, Any]:
    cfg = {
        "_target_": full_class_name(optimizer),

    }
    cfg.update(optimizer.defaults)
    return cfg


def scheduler_to_config(scheduler: torch.optim.lr_scheduler.LRScheduler) -> Optional[dict[str, Any]]:
    if scheduler is None:
        return None

    cfg = {
        "_target_": full_class_name(scheduler),
    }
    for var in vars(scheduler.__class__):  # Needs to get var names from scheduler.__class__, but values from scheduler
        cfg[var] = getattr(scheduler, var)
    return cfg


def dataset_to_config(dataset: Dataset) -> dict[str, Any]:
    cfg = {
        "_target_": full_class_name(dataset)
    }
    if hasattr(dataset, "transforms"):
        cfg["transforms"] = transforms_to_config(dataset.transforms)

    if isinstance(dataset, SimpleImageDataset):
        cfg["paths"] = dataset.paths

    return cfg


def transforms_to_config(transform) -> dict[str, Any]:
    cfg = {
        "_target_": full_class_name(transform)
    }
    if isinstance(transform, (torchvision.transforms.Compose,)):
        cfg["transforms"] = [transforms_to_config(t) for t in transform.transforms]
    if isinstance(transform, (torch.nn.ModuleList, torch.nn.Sequential)):
        cfg["transforms"] = [transforms_to_config(t) for t in transform.modules()]

    return cfg


def to_slice(start, stop, step):
    return slice(start, stop, step)


def get_git_state(path: Optional[Path | str] = None) -> dict[str, str]:
    if path is None:
        path = __file__
    path = Path(path)
    repo = None
    while path.parent != path:
        try:
            repo = git.Repo(path)
            break
        except InvalidGitRepositoryError:
            path = path.parent

    if repo is None:
        warnings.warn("No Git Repository found!")
        return {}

    name = Path(repo.working_dir).name
    commit = repo.head.commit

    return {
        "repository": name,
        "commit": commit.hexsha,
        "is_dirty": repo.is_dirty()

    }


def add_to_dict_key(data: dict[str, Any], *, prefix: str = "", suffix: str = "") -> dict[str, Any]:
    """Adds a prefix and a suffix to every key in a dictionary"""
    return {f"{prefix}{key}{suffix}": value for key, value in data.items()}


def to_binary_list(n: int, *, min_length=0) -> list[int]:
    """ Converts an integer into its binary representation as a list of 1 or 0 (MSB first) """
    result = list(map(int, list(f"{n:b}")))
    return [0] * max(min_length - len(result), 0) + result


def make_circle_masks(b, w, h) -> torch.Tensor:
    """
    Adapted from https://github.com/jstovold/ALIFE2023/blob/master/InternalSignals.ipynb

    :returns: Tensor[B, W, H]
    """
    # TODO: RNG is not seeded in this function.
    # TODO: Check W,H in correct order. Doesnt matter with square shapes
    x = torch.linspace(-1.0, 1.0, w).unsqueeze(0).unsqueeze(0)
    y = torch.linspace(-1.0, 1.0, h).unsqueeze(1).unsqueeze(0)
    center = torch.rand(2, b, 1, 1) * 0.9 + 0.05  # random between 0.05,...,0.95
    r = torch.rand(b, 1, 1) * 0.3 + 0.1
    x, y = (x - center[0]) / r, (y - center[1]) / r
    mask = (x * x + y * y < 1.0).float()
    return mask
