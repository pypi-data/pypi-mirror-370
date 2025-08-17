import warnings
from typing import Optional, Iterable, Literal, Callable

import cv2
import matplotlib.colors as mc
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image

from ncalib import NCA
from ncalib.utils.utils import length_of_slice
from ncalib.visualization.state_visualizer import StateVisualizer
from ncalib.visualization.state_visualizer.simple import RGBVisualizer

ColorType = str | tuple[float, float, float]


# Helper functions
def get_ax(ax: Optional[plt.Axes]) -> plt.Axes:
    """
    Return input axis. If it is None, return current axis instead (plt.gca())
    """
    if ax is None:
        ax = plt.gca()

    assert isinstance(ax, plt.Axes)
    return ax


def get_color(color: ColorType) -> tuple[float, float, float]:
    """
    Input can be either string (name or hex) or rgb-tuple (scale between 0..1).
    Output is always rgb-tuple scaled between 0..1
    """
    return mc.to_rgb(color)


def clean_state(state: torch.Tensor, *, clamp: bool = False) -> torch.Tensor:
    """
    :param state:  [W x H] or [C x W x H] or [B x C x W x H]
    :param clamp: if True, clamp values between 0..1
    :return: [C x W x H]
    """
    state = state.detach().cpu()
    if clamp:
        state = state.clamp(0, 1)

    if len(state.shape) == 2:  # [W x H]
        return torch.unsqueeze(state, 0)
    elif len(state.shape) == 3:  # [C x W X H]
        return state
    elif len(state.shape) == 4:  # [B x C x W x H]
        return state[0]
    raise ValueError(f"Cannot identify first state from tensor with shape {state.shape}")


def as_quadratic_shape_as_possible(n: int) -> tuple[int, int]:
    w = int(np.ceil(np.sqrt(n)))
    for h in range(1, w + 1):
        if h * w >= n:
            return w, h
    raise ValueError(f"Could not find valid w, h for {n} ({w=})")


# Visualization
def timeline_states_to_rgb_pillow(timeline_states: torch.Tensor, *, channels: slice = slice(0, 3)) -> list[list[Image]]:
    return [
        states_to_rgb_pillow(states, channels=channels)
        for states in timeline_states
    ]


def states_to_rgb_pillow(states: torch.Tensor, *, channels: slice = slice(0, 3)) -> list[Image]:
    """
    :param states: [B x C x W x H]
    :param channels: Used channels for image. Can have length of 1, 3 or 4
    """
    return [
        state_to_rgb_pillow(state, channels=channels)
        for state in states
    ]


def state_to_rgb_pillow(state: torch.Tensor, *, channels: slice = slice(0, 3)) -> Image:
    """
    :param state: [C x W x H] or [1 x C x W x H]
    :param channels: Used channels for image. Can have length of 1, 3 or 4
    """
    state = clean_state(state, clamp=True)[channels]
    C, W, H = state.shape
    processed_state = (state * 255).numpy().astype("uint8").transpose((1, 2, 0))
    if C == 1:
        return Image.fromarray(processed_state[:, :, 0], mode="L")
    elif C == 3:
        mode = "RGB"
    elif C == 4:
        mode = "RGBA"
    else:
        raise ValueError(f"No mode know for {C} channels ({channels=})")

    return Image.fromarray(processed_state, mode=mode)


def states_to_rgb_tensors(states: torch.Tensor, *, channels: slice = slice(0, 3)) -> torch.Tensor:
    """
    :param states: [B x C x W x H]
    :param channels: Used channels for image. Can have length of 1, 3 or 4
    :return [B x W x H x (3, 4)]
    """
    return states[:, channels].detach().clamp(0, 1).permute(0, 2, 3, 1).cpu()


def state_to_bgr_numpy(state: torch.Tensor, *, channels: slice = slice(0, 3)) -> np.ndarray:
    """
    :param state: [C x W x H] or [1 x C x W x H]
    :param channels: Used channels for image. Can have length of 1, 3 or 4
    :return: np.ndarray[W x H x (3 or 4)]
    """
    state = clean_state(state, clamp=True)[channels]
    img = (state * 255).numpy().astype("uint8")  # 0..1 -> 0.255
    img = img[::-1]
    return img.transpose((1, 2, 0))  # [C x W x H] -> [W x H x C]


def channel_to_image_pillow(
        channel: torch.Tensor,
        *,
        colormap: int = cv2.COLORMAP_SUMMER,
        normalization: Literal["arctan", "linear", "clip"] | Callable[[np.ndarray], np.ndarray] = "clip"
) -> Image:
    return Image.fromarray(channel_to_image_numpy(channel, colormap=colormap, normalization=normalization))


def channel_to_image_numpy(
        channel: torch.Tensor,
        *,
        colormap: int = cv2.COLORMAP_SUMMER,
        normalization: Literal["arctan", "linear", "clip"] | Callable[[np.ndarray], np.ndarray] = "clip"
) -> np.ndarray:
    """
    :param channel: [W x H]
    :param colormap: OpenCV-Colormap used for coloring
    :param normalization: "arctan" | "linear" | "clip" or function that maps to  a ndarray with values between [0..1]
    :return: ndarray[W x H x 3]
    """
    img: np.ndarray = channel.detach().cpu().numpy()  # img -> ndarray[W x H]
    if normalization == "arctan":  # Arctan-norm
        # Map [-inf, inf] to [-pi/2, pi/2] to [-1, 1] to [-0.5, 0.5] to [0, 1]
        img = (np.arctan(img) / (3.141592 / 2) / 2 + .5)
    elif normalization == "linear":  # Linear norm
        img = (img - np.min(img)) / (np.max(img) - np.min(img))
    elif normalization == "clip":
        img = np.clip(img, 0, 1)
    elif isinstance(normalization, callable):
        img = normalization(img)
    else:
        raise ValueError(f"Unexpected normalization. Got `{normalization}`.")

    img = (img * 255.0).astype("uint8")
    img = cv2.applyColorMap(img, colormap=colormap)
    return img


def separate_channel_numpy(
        channels: torch.Tensor,
        *,
        channel_plot_size=128,
        colormap=cv2.COLORMAP_SUMMER,
        normalization: Literal["arctan", "linear", "clip"] | Callable[[np.ndarray], np.ndarray] = "clip"
) -> np.ndarray:
    """
    Used for
        - State [C x W x H]
        - Metrics [M x W x H]
        - Target [C x W x H]
    :param channels: [N x W x H]
    :return: np.ndarray[W x H x N]
    """
    channels = clean_state(channels)
    c, w, h = channels.shape
    cviz_cols, cviz_rows = as_quadratic_shape_as_possible(c)
    cviz_w = cviz_cols * channel_plot_size
    cviz_h = cviz_rows * channel_plot_size

    channel_visualisation = np.zeros((cviz_h, cviz_w, 3), dtype=np.uint8)

    if normalization == "linear":
        # Normalize here to avoid local per channel normalization
        normalization = "clip"
        channels = (channels - torch.min(channels)) / (torch.max(channels) - torch.min(channels))

    for i in range(c):
        row = i // cviz_cols
        col = i % cviz_cols
        row_offset = row * channel_plot_size
        col_offset = col * channel_plot_size

        img = channel_to_image_numpy(channels[i], colormap=colormap, normalization=normalization)
        img = cv2.resize(img, (channel_plot_size, channel_plot_size))
        channel_visualisation[
        row_offset: row_offset + channel_plot_size,
        col_offset: col_offset + channel_plot_size
        ] = img
    return channel_visualisation


def separate_channel_pillow(
        channels: torch.Tensor,
        *,
        colormap=cv2.COLORMAP_SUMMER,
        normalization: Literal["arctan", "linear", "clip"] | Callable[[np.ndarray], np.ndarray] = "clip"
) -> list[Image]:
    """
    Used for
        - State [C x W x H]
        - Metrics [M x W x H]
        - Target [C x W x H]
    :param channels: [N x W x H]
    :return: np.ndarray[W x H x N]
    """
    c, w, h = channels.shape
    images = []
    for i in range(c):
        img = channel_to_image_numpy(channels[i], colormap=colormap, normalization=normalization)
        images.append(Image.fromarray(img))
    return images


def separate_channel_plot(
        channels: torch.Tensor,
        names: Optional[Iterable[str]] = None,
        *,
        dpi=200,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        colormap: Optional[mcolors.Colormap | str] = None
) -> plt.Figure:
    """
    Creates a new figure with specified dpi and plots all channels for first batch_no with a given colormap.
    Used for
        - State [(1 x) C x W x H]
        - Metrics [(1 x) M x W x H]
        - Target [(1 x) C x W x H]
    :param channels: [N x W x H]
    :param names: N strings used as caption
    :param dpi: dpi used
    :param colormap:
    :return: plt.Figure
    """
    # Parameter validation
    channels = clean_state(channels)
    if names is None:
        names = [None] * len(channels)
    if len(names) != len(channels):
        raise ValueError(f"Length of channels does not match length of names ({len(channels)} != {len(names)})")

    # Create figure
    n_channels = len(channels)
    w, h = as_quadratic_shape_as_possible(n_channels)

    # Plotting
    if min_val is None:
        min_val = channels.min()
    if max_val is None:
        max_val = channels.max()

    fig, axs = plt.subplots(h, w, squeeze=False, figsize=(w + 1, h + 1), dpi=dpi)

    # Remove ticks
    for ax1 in axs:
        for ax in ax1:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.axis("off")

    # Plot images
    for i in range(len(channels)):
        ax = axs[i // w, i % w]
        name = names[i]
        if i < len(channels):
            channel = channels[i]
            if name is None:
                ax.set_title(f"Channel {i}")
            else:
                ax.set_title(name)
            ax.imshow(channel, vmin=min_val, vmax=max_val, cmap=colormap)

    fig.tight_layout(pad=0)
    return fig


def to_bgr_image(image: np.ndarray):
    """
    Processes a Gray/BGR/BGRA image to BGR
    :param image: np.ndarray[B x W x H x 1/3/4]
    :return: np.ndarray[B x W x H x 3]
    """
    B, W, H, C = image.shape
    if C == 3:
        return image
    elif C == 4:
        return blend_alpha(image)
    elif C == 1:
        return image.repeat(3, axis=3)

    raise TypeError(f"Unknown type conversion from {C} channels to BGR (image.shape={image.shape})")


def generate_video_array(
        nca: NCA,
        state: torch.Tensor,
        *,
        visualizer: StateVisualizer = RGBVisualizer(),
        steps: int = 300,
) -> tuple[dict[str, np.ndarray], torch.Tensor]:
    """
    :param nca: callable that converts `state` to `next_state`
    :param state: tensor [B, C, W, H]
    :param steps: N steps
    :param visualizer: StateVisualizer that transform a state into images
    :return: dict[name, np.ndarray[N, W, H, 3]] (BGR), final_state Tensor: [B, C, W, H]
    """
    device = nca.device

    first_frame = visualizer(state)
    results = {name: [image] for name, image in first_frame.items()}

    # Simulate n steps
    with torch.no_grad():
        state = state.to(device)
        B, _, width, height = state.shape
        for i in range(steps):
            t_float = 1 - (i / steps)
            state = nca(state, t=torch.as_tensor([t_float] * B))
            visualization = visualizer(state)
            for name, image in visualization.items():
                results[name].append(image)

    for name, images in results.items():
        results[name] = np.stack(images, axis=0)

    return results, state


def run_inference(
        nca: NCA,
        state: torch.Tensor,
        *,
        steps: int = 300,
) -> tuple[dict[str, np.ndarray], torch.Tensor]:
    """
    :param nca: callable that converts `state` to `next_state`
    :param state: tensor [B, C, W, H]
    :param steps: N steps
    :return: final_state Tensor: [B, C, W, H]
    """
    device = nca.device

    # Simulate n steps
    with torch.no_grad():
        state = state.to(device)
        B, _, width, height = state.shape
        for i in range(steps):
            t_float = 1 - (i / steps)
            state = nca(state, t=torch.as_tensor([t_float] * B))

    return state


def video_timeline_preparation(batched_image_timeline: np.ndarray, padding=5) -> np.ndarray:
    """
    Applys to_bgr_image and np_make_grid to a batch of images
    :param batched_image_timeline: np.ndarray[T x B x W x H x 3]
    :return: np.ndarray[T x 3 x W x H]
    """
    T, B, W, H, C = batched_image_timeline.shape
    nrows = int(B ** 0.5 + 0.49)
    first_frame = np_make_grid(batched_image_timeline[0], nrow=nrows, padding=padding, pad_value=255)
    W_new, H_new, C_ = first_frame.shape
    result = np.zeros((T, W_new, H_new, C_), dtype=batched_image_timeline.dtype)
    result[0] = first_frame
    for i, frame in enumerate(batched_image_timeline[1:]):
        result[i + 1] = np_make_grid(frame, nrow=nrows, padding=padding, pad_value=255)

    bgr_videos = to_bgr_image(result)
    return bgr_videos.transpose((0, 3, 1, 2))  # Apparently wandb wants to have [T x C x W x H] for videos...


def _legacy_generate_video_array(
        nca: NCA,
        state: torch.Tensor,
        *,
        steps: int = 300,
        rgb_channels: slice = slice(0, 3)
) -> np.ndarray:
    """
    :param nca: callable that converts `state` to `next_state`
    :param state: tensor [1, C, W, H]
    :param steps: N steps
    :param rgb_channels: slice of channels which should be interpreted as rgb
    :return: [N, 3, W, H] (RGB)
    """
    device = nca.device
    warnings.warn("You are using an old version of generate_video_array!")

    # Simulate n steps
    with torch.no_grad():
        state = state.to(device)
        B, _, width, height = state.shape
        result = torch.zeros((steps + 1, length_of_slice(rgb_channels), width, height), device=device)
        result[0] = state[0, rgb_channels]
        for i in range(steps):
            t_float = 1 - (i / steps)
            state = nca(state, t=torch.as_tensor([t_float] * B))
            result[i + 1] = state[0, rgb_channels]

    # Post-processing:
    # 1. Clamp between 0 and 1
    # 2. Scale between 0 and 255
    # 3. Convert to numpy uint8 array
    result = (torch.clamp(result, 0, 1) * 255).cpu().numpy().astype("uint8")
    return result


def blend_alpha(images: torch.Tensor | np.ndarray):
    """
    Source: ChatGPT
    :param images: Tensor[(T) x B x 3/4 x W x H] | np.ndarray[(T) x B x W x H x 3/4]
    :return: Tensor[(T) x B x 3 x W x H] | np.ndarray[(T) x B x W x H x 3]
    """
    if isinstance(images, torch.Tensor):
        if len(images.shape) == 5:
            rgb = images[:, :, :3]
            alpha = images[:, :, 3:4]
        elif len(images.shape) == 4:
            rgb = images[:, :3]
            alpha = images[:, 3:4]
        else:
            raise ValueError(f"Invalid shape for tensor: {images.shape}")
    elif isinstance(images, np.ndarray):
        if len(images.shape) == 5:
            rgb = images[:, :, :, :, :3]
            alpha = images[:, :, :, :, 3:4]
        elif len(images.shape) == 4:
            rgb = images[:, :, :, :3]
            alpha = images[:, :, :, 3:4]
        else:
            raise ValueError(f"Invalid shape for ndarray: {images.shape}")
    else:
        raise TypeError("Expects either tensor or ndarray")

    # No alpha channel. E.g. Shape = [(T) x B x 0 x W x H]
    if np.prod(alpha.shape) == 0:
        return images

    # Normalize alpha channel values between 0 and 1
    alpha = alpha / 255.0

    # Apply alpha blending
    blended_image = rgb * alpha + (1 - alpha) * 255.0
    if isinstance(blended_image, np.ndarray):
        return blended_image.astype("uint8")
    return blended_image


import numpy as np


def np_make_grid(
        image,
        nrow=8,
        padding=2,
        normalize=False,
        value_range=None,
        scale_each=False,
        pad_value=0.0,
):
    """
    Make a grid of images.

    Args:
        image (ndarray or list): 4D mini-batch ndarray of shape (B x H x W x C)
            or a list of images all the same size.
        nrow (int, optional): Number of images displayed in each row of the grid.
            The final grid size is ``(B / nrow, nrow)``. Default: ``8``.
        padding (int, optional): amount of padding. Default: ``2``.
        normalize (bool, optional): If True, shift the image to the range (0, 1),
            by the min and max values specified by ``value_range``. Default: ``False``.
        value_range (tuple, optional): tuple (min, max) where min and max are numbers,
            then these numbers are used to normalize the image. By default, min and max
            are computed from the tensor.
        scale_each (bool, optional): If ``True``, scale each image in the batch of
            images separately rather than the (min, max) over all images. Default: ``False``.
        pad_value (float, optional): Value for the padded pixels. Default: ``0``.

    Returns:
        grid (ndarray): the ndarray containing grid of images.
    """
    # if list of tensors, convert to a 4D mini-batch ndarray
    if isinstance(image, list):
        image = np.stack(image, axis=0)

    if image.ndim == 2:  # single channel, single image H x W -> H x W x C
        image = np.expand_dims(image, axis=2)
    if image.ndim == 3:  # single image H x W x C -> B x H x W x C
        image = np.expand_dims(image, axis=0)

    if image.ndim == 4 and image.shape[3] == 1:  # single-channel images
        image = np.concatenate((image, image, image), axis=3)

    if normalize is True:
        image = image.copy()  # avoid modifying tensor in-place
        if value_range is not None and not isinstance(value_range, tuple):
            raise TypeError("value_range has to be a tuple (min, max) if specified. min and max are numbers")

        def norm_ip(img, low, high):
            img = np.clip(img, low, high)
            img = (img - low) / max(high - low, 1e-5)
            return img

        def norm_range(t, value_range):
            if value_range is not None:
                return norm_ip(t, value_range[0], value_range[1])
            else:
                return norm_ip(t, float(np.min(t)), float(np.max(t)))

        if scale_each is True:
            for i in range(len(image)):  # loop over mini-batch dimension
                image[i] = norm_range(image[i], value_range)
        else:
            image = norm_range(image, value_range)

    if not isinstance(image, np.ndarray):
        raise TypeError("image should be of type np.ndarray")
    if image.shape[0] == 1:
        return image.squeeze(0)

    # make the mini-batch of images into a grid
    nmaps = image.shape[0]
    xmaps = min(nrow, nmaps)
    ymaps = int(np.ceil(float(nmaps) / xmaps))
    height, width = int(image.shape[1] + padding), int(image.shape[2] + padding)
    num_channels = image.shape[3]
    grid = np.full((height * ymaps + padding, width * xmaps + padding, num_channels), pad_value, dtype=image.dtype)
    k = 0
    for y in range(ymaps):
        for x in range(xmaps):
            if k >= nmaps:
                break
            grid[y * height + padding: (y + 1) * height, x * width + padding: (x + 1) * width] = image[k]
            k += 1
    return grid
