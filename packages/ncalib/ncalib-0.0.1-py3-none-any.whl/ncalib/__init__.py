import abc
import datetime
import logging
import sys
import warnings
from pathlib import Path
from typing import Optional, Any

import torch
import torch.nn as nn
from hydra.utils import instantiate
from importlib_metadata import version, PackageNotFoundError

from ncalib.nca.perception import NCA_Perception, ChainedPerception
from ncalib.utils.torch_helper import cleanup_state_dict
from ncalib.utils.utils import full_class_name, get_git_state, NCA_Base
from ncalib.utils.wandb import get_wandb_model


class NCA(nn.Module, NCA_Base, abc.ABC):
    def __init__(
            self,
            *,
            device: torch.device | str = torch.device('cpu')
    ):
        super().__init__()
        NCA_Base.__init__(self)
        self._last_delta_state: Optional[torch.Tensor] = None

        self.device = torch.device(device)

    @property
    @abc.abstractmethod
    def channels(self) -> int:
        pass

    def reset(self):
        raise NotImplementedError(f"reset missing in {self.__class__.__name__}")

    @property
    def last_delta_state(self) -> torch.Tensor:
        """
        :return: torch.Tensor[B x C x W x H]
        """
        if self._last_delta_state is None:
            raise RuntimeError("No delta state calculated yet")
        return self._last_delta_state

    def required_kwargs(self) -> set[str]:
        return set()

    def save_as(self, filepath: Path | str) -> dict[str, Any]:
        cfg = self.as_full_config_dict()
        torch.save(cfg, filepath)
        return cfg

    def as_full_config_dict(self) -> dict[str, Any]:
        """
        Returns a complete config dict including the architecture, the state dict and some additional metadata
        """
        state_dict = self.state_dict()
        architecture = self.to_config_dict()
        cfg = {
            "architecture": architecture,
            "state_dict": state_dict,
            "required_kwargs": self.required_kwargs(),
            "meta": self.generate_meta_data()
        }
        return cfg

    @classmethod
    def load_from_path(cls, filepath: Path | str) -> "NCA":
        logging.getLogger("NCA_LOAD").info(f"Loading from path {Path(filepath).absolute()}")
        full_config_dict = torch.load(filepath, weights_only=False)
        return cls.load_from(full_config_dict)

    @classmethod
    def load_from_wandb(cls, entity: str, project: str, run_id: str, model_epoch: Optional[Any] = None) -> "NCA":
        import wandb
        api = wandb.Api()
        run = api.run(f"{entity}/{project}/{run_id}")
        assert isinstance(run, wandb.apis.public.Run)
        config = run.config
        config["state_dict"] = get_wandb_model(run, model_epoch=model_epoch)

        return cls.load_from(config)

    @classmethod
    def load_from(cls, full_config_dict: dict[str, Any]) -> "NCA":
        logger = logging.getLogger("NCA_LOAD")
        # Access Meta
        meta = full_config_dict["meta"]

        # Check versions
        for package, _version in meta["packages"].items():
            try:
                current_version = version(package)
            except PackageNotFoundError:
                current_version = None
            if current_version != _version:
                warnings.warn(
                    f'Package version mismatch! '
                    f'"{package}" has version "{current_version}", but you loaded model used version "{_version}". '
                    f'This might not work!'
                )

        logger.info(
            f"Loading NCA from {meta['date']}. Required kwargs: {list(full_config_dict.get('required_kwargs', []))}")

        # Load NCA
        if "trainer" in full_config_dict:
            architecture = full_config_dict["trainer"]["nca"]
        elif "architecture" in full_config_dict:
            architecture = full_config_dict["architecture"]
        else:
            raise ValueError("Could not find architecture in config dict")

        nca = instantiate(architecture)
        if "state_dict" in full_config_dict and full_config_dict["state_dict"] is not None:
            state_dict = cleanup_state_dict(full_config_dict["state_dict"])
            nca.load_state_dict(state_dict)

        return nca

    def generate_meta_data(self) -> dict[str, Any]:
        package_versions = {}
        for package in ["ncalib", "torch", "numpy"]:
            try:
                v = version(package)
            except:
                v = "UNKNOWN"
            package_versions[package] = v

        return {
            "date": datetime.datetime.now(),
            "git": get_git_state(),
            "python_version": sys.version,
            "num_params": self.num_params,
            "packages": package_versions
        }

    @property
    def num_params(self):
        return sum(p.numel() for p in self.parameters())
