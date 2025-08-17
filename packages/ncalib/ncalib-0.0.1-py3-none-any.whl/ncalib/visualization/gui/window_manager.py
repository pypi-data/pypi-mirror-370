import abc
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import torch

from ncalib import NCA_Base
from ncalib.visualization import np_make_grid
from ncalib.visualization.gui.brushes import GuiBrush
from ncalib.visualization.state_visualizer import StateVisualizer


@dataclass
class MouseState:
    _original_x: float = 0
    _original_y: float = 0
    x: float = 0
    y: float = 0
    batch: int = 0
    left_down: bool = False
    right_down: bool = False


class GUIWindow(NCA_Base, abc.ABC):
    def __init__(self):
        super().__init__()
        self.cv2_windows = {}

    def __add__(self, other):
        # Prepare each state updater so that each is an iterable of simple state updaters
        if isinstance(self, MultipleWindows):
            windows1 = self.windows
        else:
            windows1 = [self]

        if isinstance(other, MultipleWindows):
            windows2 = other.windows
        else:
            windows2 = [other]

        # Combine State Updaters
        return MultipleWindows(*windows1, *windows2)

    @abc.abstractmethod
    def update_windows(self):
        pass

    @abc.abstractmethod
    def update_state(self, state: torch.Tensor, step: int):
        pass

    def init_state(self, state: torch.Tensor):
        self.update_state(state, step=0)

    def handle_key(self, key: int):
        pass

    def modify_state(self, state: torch.Tensor) -> torch.Tensor:
        return state


class VisualizingWindow(GUIWindow, abc.ABC):
    def __init__(self, visualizer: StateVisualizer, *, brush: Optional[GuiBrush] = None):
        super().__init__()
        self.visualizer = visualizer
        self.brush = brush
        self.step = 0

        # name -> np.ndarray[B x 3 x W x H]
        self.last_visualization: dict[str, np.ndarray] = {}
        self.mouse_state: dict[str, MouseState] = {}

    def update_state(self, state: torch.Tensor, step: int):
        self.step = step
        for name, images in self.visualizer(state).items():
            B, W, H, C = images.shape
            self.last_visualization[name] = images
            if C == 3 or C == 4:  # SWAP RGB to BGR
                self.last_visualization[name][:, :, :, [0, 2]] = images[:, :, :, [2, 0]]

    def _initialize_window(self, window_name: str):
        try:
            # Destroy old window if it exists
            cv2.destroyWindow(window_name)
        except cv2.error:
            pass

        self.mouse_state[window_name] = MouseState()
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, partial(self.mouse_callback, window_name=window_name))

    def mouse_callback(self, event, x, y, flags, param, *, window_name):
        self.mouse_state[window_name]._original_x = x
        self.mouse_state[window_name]._original_y = y
        image_x, image_y, batch = self.parse_mouse_position(x, y, window_name)
        self.mouse_state[window_name].x = image_x
        self.mouse_state[window_name].y = image_y
        self.mouse_state[window_name].batch = batch
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_state[window_name].left_down = True
        elif event == cv2.EVENT_LBUTTONUP:
            self.mouse_state[window_name].left_down = False
        # elif event == cv2.EVENT_RBUTTONDown:
        #     self.mouse[batch].right_down = True
        # elif event == cv2.EVENT_RBUTTONUP:
        #     self.mouse[batch].right_down = False

    def modify_state(self, state: torch.Tensor) -> torch.Tensor:
        if self.brush is None:
            return state

        for mouse in self.mouse_state.values():
            state = self.brush.modify_state(state, mouse=mouse)
        return state

    def parse_mouse_position(
            self,
            x: float,
            y: float,
            window_name: str
    ) -> tuple[Optional[float], Optional[float], Optional[int]]:
        """
        :return: image_x, image_y, batch
        """
        return None, None, None


class MultipleWindows(GUIWindow):
    def __init__(self, *windows: GUIWindow):
        super().__init__()
        self.windows = tuple(windows)

    def update_windows(self):
        for window in self.windows:
            window.update_windows()

    def init_state(self, state: torch.Tensor):
        for window in self.windows:
            window.init_state(state)

    def handle_key(self, key: int):
        for window in self.windows:
            window.handle_key(key)

    def update_state(self, state: torch.Tensor, step: int):
        for window in self.windows:
            window.update_state(state, step=step)

    def modify_state(self, state: torch.Tensor) -> torch.Tensor:
        for window in self.windows:
            state = window.modify_state(state)
        return state


class SliderBatchWindow(VisualizingWindow):
    def __init__(self, visualizer: StateVisualizer, *, brush: Optional[GuiBrush] = None):
        super().__init__(visualizer, brush=brush)
        self.batch_selected = 0

    def init_state(self, state: torch.Tensor):
        super().init_state(state)
        for window_name, images in self.last_visualization.items():
            batch_size = len(images)
            self._initialize_window(window_name)
            if batch_size > 1:
                cv2.createTrackbar("Batch", window_name, 0, batch_size - 1, self._batch_slider_changed)

    def _batch_slider_changed(self, value):
        self.batch_selected = value - 1

    def update_windows(self):
        for name, images in self.last_visualization.items():
            cv2.imshow(name, images[self.batch_selected])

    def parse_mouse_position(
            self,
            x: float,
            y: float,
            window_name: str
    ) -> tuple[Optional[float], Optional[float], Optional[int]]:
        """
        :return: image_x, image_y, batch
        """
        return x, y, self.batch_selected


class MergeBatchWindow(VisualizingWindow):
    def __init__(
            self,
            visualizer: StateVisualizer,
            *,
            brush: Optional[GuiBrush] = None,
            padding: int = 2,
            batch_width: Optional[int] = None,
            save_image_folder: Optional[Path | str] = None
    ):
        super().__init__(visualizer, brush=brush)
        self.nrow = batch_width
        self.batch_selected = 0
        self.padding = padding
        self.save_image_folder = Path(save_image_folder) if save_image_folder is not None else None

    def init_state(self, state: torch.Tensor):
        super().init_state(state)
        for window_name, images in self.last_visualization.items():
            batch_size = len(images)
            self._initialize_window(window_name)
            if self.nrow is None:
                self.nrow = int(batch_size ** 0.5 + 0.49)
        self.update_windows()

    def update_windows(self):
        for name, images in self.last_visualization.items():
            merged_image = np_make_grid(
                images,
                nrow=self.nrow,
                pad_value=255,
                padding=self.padding
            )
            cv2.imshow(name, merged_image)

            if self.save_image_folder is not None:
                self.save_image_folder.mkdir(exist_ok=True, parents=True)
                cv2.imwrite(str(self.save_image_folder / f"{name}_{self.step}.png"), merged_image)

    def parse_mouse_position(
            self,
            x: float,
            y: float,
            window_name: str
    ) -> tuple[Optional[float], Optional[float], Optional[int]]:
        """
        :return: image_x, image_y, batch
        """
        B, W, H, C = self.last_visualization[window_name].shape
        xmaps = min(self.nrow, B)
        height, width = int(H + self.padding), int(W + self.padding)
        batch = max(min(int((y // height) * xmaps + x // width), B - 1), 0)
        return x % width, y % height, batch


class SeparateWindows(VisualizingWindow):
    def __init__(self, visualizer: StateVisualizer, *, brush: Optional[GuiBrush] = None):
        super().__init__(visualizer, brush=brush)
        self.batch_selected = 0

    def init_state(self, state: torch.Tensor):
        super().init_state(state)
        for single_window_name, images in self.last_visualization.items():
            batch_size = len(images)
            if batch_size == 1:
                window_names = [single_window_name]
            else:
                window_names = [self.window_name(single_window_name, i) for i in range(batch_size)]
            for name in window_names:
                self._initialize_window(name)

    def update_windows(self):
        for name, images in self.last_visualization:
            for i, image in enumerate(images):
                cv2.imshow(self.window_name(name, i), image)

    @staticmethod
    def window_name(name: str, i: int) -> str:
        return f"{name}-{i}"

    def parse_mouse_position(
            self,
            x: float,
            y: float,
            window_name: str
    ) -> tuple[Optional[float], Optional[float], Optional[int]]:
        """
        :return: image_x, image_y, batch
        """
        batch = int(window_name.split("-")[1])
        return x, y, batch
