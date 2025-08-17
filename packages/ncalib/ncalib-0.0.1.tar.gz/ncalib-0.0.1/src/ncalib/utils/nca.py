import logging
from typing import Literal

import torch
from omegaconf import DictConfig

from ncalib import ChainedPerception, NCA_Perception, NCA
from ncalib.nca.models.basic import BasicNCAModel
from ncalib.nca.modular_nca import ModularNCA
from ncalib.nca.perception.filter import IdentityPerception, SobelXPerception, SobelYPerception, LaPlace1Perception, \
    LaPlace2Perception
from ncalib.utils.defaults import DEFAULT_DEVICE

logger = logging.getLogger("utils.nca")


def build_perception(
        *,
        channels=16,
        identity=True,
        sobel_x=True,
        sobel_y=True,
        laplace1=False,
        laplace2=False,
        padding_mode: Literal["constant", "reflect", "replicate", "circular"] = "replicate"
):
    logger.debug(f"Perception: Build chained perception for {channels} channels")
    perception = ChainedPerception(channels)
    if identity:
        logger.debug(f"Perception: Add identity")
        perception += IdentityPerception(channels)
    if sobel_x:
        logger.debug(f"Perception: Add Sobel X")
        perception += SobelXPerception(channels, padding_mode=padding_mode)
    if sobel_y:
        logger.debug(f"Perception: Add Sobel Y")
        perception += SobelYPerception(channels, padding_mode=padding_mode)
    if laplace1:
        logger.debug(f"Perception: Add LaPlace (v1)")
        perception += LaPlace1Perception(channels, padding_mode=padding_mode)
    if laplace2:
        logger.debug(f"Perception: Add LaPlace (v2)")
        perception += LaPlace2Perception(channels, padding_mode=padding_mode)

    return perception


def build_modular_nca(
        channels: int,
        perception: NCA_Perception,
        model: DictConfig,
        update_probability: float = 0.5,
        device: torch.device | str = DEFAULT_DEVICE,

) -> NCA:
    logger.debug(f"NCA: Build NCA with {channels} channels and {update_probability=} for device {device}")
    nca_model = BasicNCAModel(
        perception.output_size_for_n_channels(channels),
        channels,
        hidden_channels=model["hidden_channels"]
    )
    nca = ModularNCA(
        channels,
        perception,
        nca_model,
        device=device
    )

    # Load state dict
    if model.state_dict:
        logger.debug(f"Load state_dict")
        nca.load_state_dict(torch.load(model.state_dict, map_location=device))
    else:
        logger.debug(f"No state_dict found for model")
    return nca
