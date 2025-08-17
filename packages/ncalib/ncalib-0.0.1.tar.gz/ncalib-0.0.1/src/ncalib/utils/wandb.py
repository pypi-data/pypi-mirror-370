import datetime
import json
import logging
import re
import tempfile
import warnings
from pathlib import Path
from typing import Optional, Any

import torch
import wandb
from omegaconf import DictConfig
from wandb.apis.public import Files, File, Run
from wandb.util import download_file_from_url

from ncalib.utils.defaults import DEFAULT_DEVICE


def get_latest_model_from_wandb(files: Files) -> Optional[File]:
    logger = logging.getLogger("utils:.wandb:get_latest_model_from_wandb")
    model_files = []
    for file in files:
        assert isinstance(file, File)
        if not file.name.startswith("models"):
            continue

        model_files.append(file)

    logger.debug(f"Found {len(model_files)} models out of {len(files)} files")
    if len(model_files) == 0:
        return None

    return sorted(model_files, key=lambda f: f.name)[-1]


def get_wandb_model(run: Run, *, model_epoch=Optional[int]) -> Optional[dict]:
    pattern = re.compile("model-(\\d+)\\.(state_dict|nca)")

    matched_model_file = None
    current_highest_model = 0

    for file in run.files():
        assert isinstance(file, File)

        result = pattern.findall(file.name)
        if len(result) == 0:
            continue
        epoch_str, file_extension = result[0]
        epoch = int(epoch_str)
        if epoch == model_epoch:
            matched_model_file = file
            break
        elif model_epoch is None and epoch > current_highest_model:
            current_highest_model = epoch
            matched_model_file = file

    if matched_model_file is None:
        warnings.warn(f"No model found (model_epoch={model_epoch})!")
        return None

    tmp_path = Path(tempfile.gettempdir()) / f"{tempfile.gettempprefix()}.{file_extension}"
    download_file_from_url(str(tmp_path), matched_model_file.url, api_key=wandb.Api().api_key)

    full_config = torch.load(tmp_path)
    tmp_path.unlink()  # Delete temp file
    return full_config["state_dict"]


def get_target_file(files: Files) -> Optional[File]:
    logger = logging.getLogger("utils:.wandb:get_target_file")
    for file in files:
        assert isinstance(file, File)
        if file.name.startswith("media/images/target"):
            return file
    logger.error("Could not find a target!")
    return None



def _get_run(run: Optional[Run]) -> Run:
    if run is None:
        if wandb.run is None:
            raise ValueError("No run provided and no run initialized")
        run = wandb.run
    return run


def load_model_from_wandb_run(run: Run = None, *, device=DEFAULT_DEVICE) -> "NCA":
    from hydra.utils import instantiate
    # Take currently logged in run, if run is None
    logger = logging.getLogger("utils:.wandb:load_model_from_wandb_run")
    run = _get_run(run)

    logger.info(f"Loading NCA for run {run}")
    # Build NCA
    wandb_config = load_wandb_hydra_config(run)

    nca = instantiate(wandb_config.algorithm.nca, device=device)
    logger.debug(f"NCA: {nca}")

    # Load model
    files = run.files()
    latest_model = get_latest_model_from_wandb(files)
    if latest_model is None:
        logger.warning(f"No model found for Run {run.id}!")
    else:
        model_path = f"tmp_model_{datetime.datetime.now():%Y%m%d_%H%M%S_%f}.state_dict"
        logger.debug(f"Download {latest_model.id} to {model_path} (Size: {latest_model.size})")
        download_file_from_url(model_path, latest_model.url, api_key=wandb.Api().api_key)

        logger.debug(f"Download complete. Load model.")
        nca.load_state_dict(torch.load(model_path))
        Path(model_path).unlink()  # Delete temp file
    return nca


def get_wandb_values(cfg: Any) -> Any:
    """
    Wandb Config structure:
        key: {"value": value, "desc": ...}

    :return dict with key: value
    """
    if not isinstance(cfg, dict):
        return cfg

    new_cfg = {}
    for key in cfg:
        new_cfg[key] = cfg[key]["value"]

    return new_cfg


def load_wandb_hydra_config(run: Run, prefix="hydra_") -> DictConfig:
    """
    1. Remove prefix from keys
    2. Set value of cfg to "value". Wandb-Configs has structure key: {"value": value, "...": ...}
    """
    cfg = json.loads(run.json_config)

    new_cfg = {}
    for key, value in get_wandb_values(cfg).items():
        if key.startswith(prefix):
            new_cfg[key.replace(prefix, "", 1)] = value

    return DictConfig(new_cfg)


def load_wandb_config(run: Run) -> dict[str, Any]:
    return get_wandb_values(json.loads(run.json_config))
