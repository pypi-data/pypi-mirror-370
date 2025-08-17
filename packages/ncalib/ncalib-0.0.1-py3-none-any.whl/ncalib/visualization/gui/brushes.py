import abc
from typing import Callable, Literal

import cv2
import numpy as np
import torch


class GuiBrush(abc.ABC):
    def __init__(
            self,
            *,
            value: float | Callable[[int, int, int], np.ndarray | float] | Literal["random"] = 1,
            channels: slice = slice(None, None, None)
    ):
        super().__init__()
        if isinstance(value, float | int):
            self.value_factory = lambda c, w, h: value
        elif value == "random":
            self.value_factory = lambda c, w, h: torch.rand((c, w, h))
        else:
            self.value_factory = value
        self.channels = channels

    def modify_state(self, state: torch.Tensor, mouse: "MouseState") -> torch.Tensor:
        # Mouse event not parsed
        if mouse.batch is None:
            return state

        C, W, H = state[mouse.batch, self.channels].shape
        mask = np.zeros((W, H))

        if mouse.left_down:
            self._draw(mask, mouse)

        mask = torch.from_numpy(mask).to(state.device)
        state[mouse.batch, self.channels] = (
                state[mouse.batch, self.channels] * (mask == 0) +
                self.value_factory(C, W, H) * (mask != 0)
        )
        return state

    @abc.abstractmethod
    def _draw(self, mask: np.ndarray, mouse: "MouseState"):
        pass


class CircleBrush(GuiBrush):
    def __init__(self, *, value: float = 1, size=5, channels: slice = slice(None, None, None)):
        super().__init__(value=value, channels=channels)
        self.size = size

    def _draw(self, mask: np.ndarray, mouse: "MouseState"):
        cv2.circle(mask, (int(mouse.x), int(mouse.y)), self.size, 1, -1)
