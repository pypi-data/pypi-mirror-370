import torch
from jaxtyping import Float

from ncalib import NCA_Perception


class SteerablePerception(NCA_Perception):
    def __init__(
            self,
            perception: NCA_Perception,
            channel_id: int,
            *,
            channel_slice:slice=slice(None,None,None),
    ):
        super().__init__(channel_slice=channel_slice)
        self.channel_id = channel_id
        self.perception = perception

    def forward(self, state: Float[torch.Tensor, "B C W H"], **kwargs) -> list[Float[torch.Tensor, "B C W H"]]:
        # TODO: Can we just remove this or implement in every perception?
        channel_mask = torch.arange(state.shape[1]) != self.channel_id

        # Calculate original perception
        perceptions = self.perception(state[:, channel_mask])
        if len(perceptions) != 2:
            raise RuntimeError("Internal perception needs to return a list of 2 Perception matrices")

        p1, p2 = perceptions
        angle = state[:, self.channel_id]
        cos_angle, sin_angle = torch.cos(angle)[:, None], torch.sin(angle)[:, None]
        return [p1 * cos_angle + p2 * sin_angle, p2 * cos_angle - p1 * sin_angle]

    def to_config_dict(self):
        cfg = super().to_config_dict()
        cfg["perception"] = self.perception.to_config_dict()
        cfg["channel_id"] = self.channel_id
        return cfg
