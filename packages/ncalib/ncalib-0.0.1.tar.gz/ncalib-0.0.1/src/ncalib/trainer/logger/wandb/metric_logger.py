import abc
import queue
import warnings
from dataclasses import dataclass, field
from enum import Enum
from threading import Thread
from typing import Any, Optional, Iterable, Callable

import numpy as np
import torch
import wandb
from wandb.sdk.data_types.base_types.media import Media

from ncalib.seed_factory import NCA_SeedFactory
from ncalib.trainer import NCA_Trainer, NCA_StoppingCriterion
from ncalib.trainer.batcher.simple import SimpleBatcher
from ncalib.trainer.dataset import DataSample, NCA_Dataset
from ncalib.trainer.logger.wandb import WandBLogger
from ncalib.trainer.loss_function import LossResult, NCA_LossFunction
from ncalib.visualization import np_make_grid, states_to_rgb_pillow, generate_video_array, blend_alpha, \
    _legacy_generate_video_array, as_quadratic_shape_as_possible, video_timeline_preparation, run_inference
from ncalib.visualization.state_visualizer import StateVisualizer
from ncalib.visualization.state_visualizer.simple import RGBVisualizer

WANDB_LOG_QUEUE: Optional[queue.Queue] = None


class WandbPlaceholder(abc.ABC):
    def replace(self) -> Media | list[Media]:
        pass


class WandBImagePlaceholder(WandbPlaceholder):
    def __init__(self, image_data: np.ndarray, caption: Optional[str] = None, **kwargs):
        self.image_data = image_data
        self.caption = caption
        self.kwargs = kwargs

    def replace(self) -> Media:
        return wandb.Image(self.image_data, caption=self.caption, **self.kwargs)


class WandBImageListPlaceholder(WandbPlaceholder):
    def __init__(self, images_data: list[np.ndarray], **kwargs):
        self.images_data = images_data
        self.kwargs = kwargs

    def replace(self) -> list[Media]:
        return [wandb.Image(image_data, **self.kwargs) for image_data in self.images_data]


class WandBVideoPlaceholder(WandbPlaceholder):
    def __init__(self, video_data: np.ndarray, fps: int, format: str = "gif", caption: Optional[str] = None):
        self.video_data = video_data
        self.fps = fps
        self.format = format
        self.caption = caption

    def replace(self) -> wandb.Video:
        return wandb.Video(self.video_data, caption=self.caption, fps=self.fps, format=self.format)


def handle_wandb_logging_queue():
    step = 0
    log_data = {}

    def log_now():
        nonlocal log_data
        if len(log_data) > 0:
            wandb.log(
                log_data,
                step=step,
            )
            log_data = {}

    while True:
        try:
            item = WANDB_LOG_QUEUE.get(timeout=2)
        except queue.Empty:
            log_now()
            continue

        # Escape WandB Log Queue
        if item is False:
            break

        this_step, this_log_data = item
        if this_step != step:
            # Log all aggregated data
            log_now()

            # Reset for next step
            step = this_step

        # Add new data
        for name in this_log_data:
            value = this_log_data[name]
            if isinstance(value, WandbPlaceholder):
                value = value.replace()
            log_data[name] = value

            if len(log_data) >= 10:
                log_now()  # Clear buffer

    log_now()


class WandBMetricLogger(WandBLogger, abc.ABC):
    """
    Creates an interface which has to implement a get_log_data function that returns a dict[name -> Any] that will
    get logged for the current epoch.
    """

    def __init__(
            self,
            *,
            epoch_interval: int = 1000,
            log_final: bool = False,
            prefix: Optional[str] = None
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final)
        self.prefix = prefix
        global WANDB_LOG_QUEUE
        self.wandb_log_queue_thread = None
        if WANDB_LOG_QUEUE is None:  # Make sure the wandb log queue is only initialized once
            WANDB_LOG_QUEUE = queue.Queue()
            self.wandb_log_queue_thread = Thread(target=handle_wandb_logging_queue, daemon=True)
            self.wandb_log_queue_thread.start()

    def __del__(self):
        if WANDB_LOG_QUEUE is not None:
            WANDB_LOG_QUEUE.put(False)

    def _log(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        log_data = self.get_log_data(data_sample, state_progression, loss)
        if self.prefix is not None:
            log_data = {f"{self.prefix}/{k}": v for k, v in log_data.items()}
        WANDB_LOG_QUEUE.put((self.trainer.epoch, log_data))

    @abc.abstractmethod
    def get_log_data(
            self,
            data_sample: DataSample,
            state_progression: torch.Tensor,
            loss: LossResult
    ) -> dict[str, Any]:
        pass


class WandBLossLogger(WandBMetricLogger):
    def init_training(self, trainer: NCA_Trainer, stopping_criterion: NCA_StoppingCriterion):
        super().init_training(trainer, stopping_criterion)

    def get_log_data(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        detailed_loss = loss.detailed_loss(include_total=True)
        log_data = {f"loss/{name}": loss for name, (loss, weight) in detailed_loss.items()}
        log_data.update({f"loss_weighted/{name}": loss * weight for name, (loss, weight) in detailed_loss.items() if
                         name != "total"})

        return log_data


class BatchMode(Enum):
    MERGED_QUADRATIC = 1
    MERGED_ROW = 2
    MERGED_COLUMN = 3
    SEPARATE = 4


class WandBBatchLogger(WandBMetricLogger):
    def __init__(
            self,
            visualizer: StateVisualizer = RGBVisualizer(),
            *,
            log_name: str = "batch",
            epoch_interval: int = 100,
            log_final: bool = False,
            target_visualizer: bool | StateVisualizer = True,
            batch_mode: BatchMode = BatchMode.MERGED_COLUMN,
            prefix: Optional[str] = None,
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final, prefix=prefix)
        self.batch_mode = batch_mode
        self.log_name = log_name
        self.visualizer = visualizer
        if target_visualizer is True:
            target_visualizer = visualizer
        self.target_visualizer: StateVisualizer | bool = target_visualizer

    def get_log_data(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        log_data = {}
        log_data.update(self._create_visualizations(state_progression[-1], "state", visualizer=self.visualizer))
        log_data.update(self._create_visualizations(state_progression[0], "seeds", visualizer=self.visualizer))
        log_data.update(self._create_visualizations(data_sample.targets, "targets", visualizer=self.target_visualizer))

        return log_data

    def _create_visualizations(
            self,
            state: torch.Tensor,
            name: str,
            visualizer: StateVisualizer | bool
    ) -> dict[str, WandBImagePlaceholder | WandBImageListPlaceholder]:
        if visualizer is False:
            return {}
        result = {}
        visualization = visualizer(state)

        for visualization_name, images in visualization.items():
            if self.batch_mode == BatchMode.MERGED_QUADRATIC:
                log_item = WandBImagePlaceholder(np_make_grid(
                    images,
                    nrow=int(len(images) ** 0.5 + 0.49),
                    pad_value=255,
                    padding=5
                ))
            elif self.batch_mode == BatchMode.MERGED_ROW:
                log_item = WandBImagePlaceholder(np_make_grid(
                    images,
                    nrow=len(images),
                    pad_value=255,
                    padding=5
                ))
            elif self.batch_mode == BatchMode.MERGED_COLUMN:
                grid = np_make_grid(images, nrow=1, pad_value=255, padding=5)
                log_item = WandBImagePlaceholder(grid)
            elif self.batch_mode == BatchMode.SEPARATE:
                log_item = WandBImageListPlaceholder([image for image in images])
            else:
                raise ValueError(f"Unknown BatchMode: {self.batch_mode}")
            result[f"{self.log_name}_{name}_{visualization_name}"] = log_item

        return result


class WandBImageLogger(WandBMetricLogger):
    def __init__(
            self,
            *,
            log_name: str = "batch",
            epoch_interval: int = 100,
            log_final: bool = False,
            channels: slice = slice(0, 3),
            target_channels: slice = slice(None, None),
            prefix: Optional[str] = None,
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final, prefix=prefix)
        self.log_name = log_name
        self.channels = channels
        self.target_channels = target_channels
        warnings.warn("This logger is deprecated. Please use WandBBatchLogger instead!")

    def get_log_data(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        log_data = {
            f"{self.log_name}_state": [wandb.Image(img, mode=img.mode) for img in
                                       states_to_rgb_pillow(state_progression[-1], channels=self.channels)],
            f"{self.log_name}_seeds": [wandb.Image(img, mode=img.mode) for img in
                                       states_to_rgb_pillow(state_progression[0], channels=self.channels)],
            f"{self.log_name}_targets": [wandb.Image(img, mode=img.mode) for img in
                                         states_to_rgb_pillow(data_sample.targets, channels=self.target_channels)],
        }

        return log_data


@dataclass
class VideoParameter:
    image_slice: slice = field(default_factory=lambda: slice(None, None))
    fps: int = 24
    name: str = "video"
    batch_padding: int = 5

    def to_video_name(self, visualization_name: str) -> tuple[str, str]:
        """
        :param visualization_name:
        :return: tuple[log_name, caption]
        """
        caption_start = ""
        caption_end = ""
        caption_speedup = ""
        log_start = ""
        log_end = ""
        log_speedup = ""
        if self.image_slice.start is not None:
            caption_start = f" from {self.image_slice.start}"
            log_start = self.image_slice.start
        if self.image_slice.stop is not None:
            caption_end = f" until {self.image_slice.stop}"
            log_end = self.image_slice.stop
        if self.image_slice.step is not None and self.image_slice.step != 1:
            caption_speedup = f" (::{self.image_slice.step})"
            log_speedup = self.image_slice.step

        log_name = f"{self.name}_[{log_start}:{log_end}:{log_speedup}]_{visualization_name}"
        caption = f"{self.name}{caption_start}{caption_end}{caption_speedup} {visualization_name}"
        return log_name, caption


ProgressionParameter = slice | Iterable[int]


class WandBInferenceLogger(WandBMetricLogger):
    def __init__(
            self,
            seed_factory: NCA_SeedFactory,
            visualizer: StateVisualizer,
            *,
            epoch_interval: int = 1000,
            batch_size=1,
            video_parameters: Optional[VideoParameter | Iterable[VideoParameter]] = VideoParameter(slice(None, 1000)),
            progression_parameters: Optional[ProgressionParameter | Iterable[ProgressionParameter]] = None,
            static_image_parameters: Optional[int | Iterable[int]] = -1,
            max_steps: Optional[int] = None,
            log_final: bool = False,
            prefix: Optional[str] = None,
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final, prefix=prefix)
        # General
        self.batch_size = batch_size
        self.seed_factory = seed_factory
        self.visualizer = visualizer

        # Video parameter
        self.video_parameters, video_steps = self._initialize_video_parameters(video_parameters)

        # Progression images
        self.progression_parameters, prog_steps = self._initialize_progression_parameters(progression_parameters)

        # Static images
        self.static_image_parameters, image_steps = self._initialize_static_image_parameters(static_image_parameters)

        if len(self.video_parameters) + len(self.progression_parameters) + len(self.static_image_parameters) > 0:
            self._requires_images = True
        else:
            self._requires_images = False

        required_max_steps = max(video_steps, prog_steps, image_steps)
        if max_steps is not None:
            if max_steps < required_max_steps:
                self.logger.warn(f"max steps is set to {max_steps}, "
                                 f"but {required_max_steps} steps required according to parameters. "
                                 f"Steps greater than {max_steps} will be ignored!")
            self.steps = max_steps
        elif required_max_steps == 0:
            raise ValueError("max_steps is not given, but cannot be inferred from other parameters!")
        else:
            # Case: max_steps is None -> Take from required_max_steps
            self.steps = required_max_steps

    @staticmethod
    def _initialize_video_parameters(
            video_parameters: Optional[VideoParameter | Iterable[VideoParameter]]
    ) -> tuple[list[VideoParameter], int]:
        # Bring to correct shape
        if video_parameters is None:
            video_parameters = []
        elif isinstance(video_parameters, VideoParameter):
            video_parameters = [video_parameters]

        # Count max steps and validate VideoParameter
        max_steps = 0
        for video_parameter in video_parameters:
            if not isinstance(video_parameter, VideoParameter):
                raise TypeError(f"Expects type VideoParameter but got {type(video_parameter)}")

            video_stop = video_parameter.image_slice.stop
            if video_stop is not None:
                max_steps = max(video_stop, max_steps)

        return list(video_parameters), max_steps

    @staticmethod
    def _initialize_progression_parameters(
            progression_parameters: Optional[ProgressionParameter | Iterable[ProgressionParameter]]
    ) -> tuple[list[ProgressionParameter], int]:
        # Bring to correct shape
        if progression_parameters is None:
            progression_parameters = []
        elif isinstance(progression_parameters, slice):
            progression_parameters = [progression_parameters]
        if len(progression_parameters) > 0 and isinstance(progression_parameters[0], int):
            # Converting list of idx to list of list of idx, so we have a list of ProgressionParameter
            progression_parameters = [progression_parameters]

        # Count max steps and validate Progression Parameter
        max_steps = 0
        for progression_parameter in progression_parameters:
            if isinstance(progression_parameter, slice):
                progression_stop = progression_parameter.stop
                if progression_stop is not None:
                    max_steps = max(progression_stop, max_steps)
                continue

            # Expects an Iterable of ints here
            for idx in progression_parameter:
                if not isinstance(idx, int):
                    raise TypeError(f"Expects iterable of ints at this place for Progression Parameter, "
                                    f"but got {idx} ({progression_parameter})")
                max_steps = max(max_steps, idx)

        return list(progression_parameters), max_steps

    @staticmethod
    def _initialize_static_image_parameters(
            static_image_parameters: Optional[int | Iterable[int]]
    ) -> tuple[list[int], int]:
        # Bring to correct shape
        if static_image_parameters is None:
            static_image_parameters = []
        elif isinstance(static_image_parameters, int):
            static_image_parameters = [static_image_parameters]

        # Count max steps and validate static image parameters
        max_steps = 0
        for pos, idx in enumerate(static_image_parameters):
            if not isinstance(idx, int):
                raise TypeError(f"Expects ints at this place for static images, "
                                f"but got {idx} on position {pos} in {static_image_parameters}")

            max_steps = max(max_steps, idx)

        return static_image_parameters, max_steps

    def get_log_data(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        """ Do not use data_sample, state_progression or loss here, as these are not wanted in Inference Logger"""
        log_data = {}
        nca = self.trainer.nca
        seed_state = self.seed_factory(self.batch_size, device=nca.device)
        if self._requires_images:
            image_timelines, final_state = generate_video_array(
                nca,
                seed_state,
                steps=self.steps,
                visualizer=self.visualizer
            )
            log_data.update(self.create_videos(image_timelines))
            log_data.update(self.create_progression_images(image_timelines))
            log_data.update(self.create_static_images(image_timelines))
        else:
            final_state = run_inference(nca, seed_state, steps=self.steps)

        return log_data

    def create_videos(self, image_timelines: dict[str, np.ndarray]) -> dict[str, WandBVideoPlaceholder]:
        """
        :param image_timelines: dict[name, np.ndarray[T x B x W x H x 3]]
        :return: dict[str, wandb-video-placeholder]
        """
        log_data = {}
        for visualization_name, image_timeline in image_timelines.items():
            for video_parameter in self.video_parameters:
                log_name, caption = video_parameter.to_video_name(visualization_name)
                video = video_timeline_preparation(
                    image_timeline[video_parameter.image_slice],
                    padding=video_parameter.batch_padding
                )
                log_data[log_name] = WandBVideoPlaceholder(
                    video,
                    caption=caption,
                    format="gif",
                    fps=video_parameter.fps
                )

        return log_data

    def create_progression_images(self, image_timelines: dict[str, np.ndarray]) -> dict[str, WandBImageListPlaceholder]:
        """
        :param image_timelines: dict[name, np.ndarray[T x B x W x H x 3]]
        :return: dict[str, wandb-image-list-placeholder]. Creates per Batch one Progression
        """
        log_data = {}
        for visualization_name, image_timeline in image_timelines.items():
            for i, progression_parameter in enumerate(self.progression_parameters):
                # Get name for this progression_parameter
                progression_name = i
                if isinstance(progression_parameter, slice):
                    progression_name = str(progression_parameter)

                # Process progression
                progression_images = image_timeline[progression_parameter]
                # progression_images: np.ndarray[T' x B x W x H x 3]
                row, _ = as_quadratic_shape_as_possible(len(progression_images))
                merged_progression_images = [
                    np_make_grid(images, nrow=row, pad_value=255)
                    for images in progression_images.transpose((1, 0, 2, 3, 4))
                ]
                # merged_progression_images: list[np.ndarray[W x H x 3]] with length B

                log_data[f"progression_{progression_name}_{visualization_name}"] = WandBImageListPlaceholder(
                    merged_progression_images
                )

        return log_data

    def create_static_images(self, image_timelines: dict[str, np.ndarray]) -> dict[str, WandBImagePlaceholder]:
        """
        :param image_timelines: dict[name, np.ndarray[T x B x W x H x 3]]
        :return: dict[str, wandb-image-placeholder]
        """
        log_data = {}
        for visualization_name, image_timeline in image_timelines.items():
            nrow, _ = as_quadratic_shape_as_possible(image_timeline.shape[1])
            for static_image_idx in self.static_image_parameters:
                images = image_timeline[static_image_idx]
                # images: np.ndarray[B x W x H x 3]
                log_data[f"image_{static_image_idx}_{visualization_name}"] = WandBImagePlaceholder(
                    np_make_grid(
                        images, nrow=nrow, pad_value=255
                    )
                )

        return log_data


class WandBTrainingParameterLogger(WandBMetricLogger):
    def __init__(
            self,
            *,
            epoch_interval: int = 25,
            log_final: bool = True,
            prefix: Optional[str] = None,
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final, prefix=prefix)

    def get_log_data(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        log_data = {
            "learning_rate": self.trainer.optimizer.param_groups[-1]['lr']
        }
        return log_data


class WandBVideoLogger(WandBMetricLogger):
    def __init__(
            self,
            seed_factory: NCA_SeedFactory,
            *,
            fps: int = 24,
            steps: int = 300,
            log_name: str = "video",
            epoch_interval: int = 1000,
            log_final: bool = False,
            take_every: int = 1,
            rgb_channels: slice = slice(0, 3),
            has_alpha: bool = False,
            log_image=True,
            prefix: Optional[str] = None,
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final, prefix=prefix)
        warnings.warn("This logger is deprecated. Please use WandBInferenceLogger instead!")
        self.seed_factory = seed_factory

        self.fps = fps
        self.steps = steps
        self.take_every = take_every
        self.log_name = log_name
        self.log_image = log_image

        self.rgb_channels = rgb_channels
        self.has_alpha = has_alpha

    def init_training(self, trainer: NCA_Trainer, stopping_criterion: NCA_StoppingCriterion):
        super().init_training(trainer, stopping_criterion)
        wandb.watch(self.trainer.nca, log_freq=self.epoch_interval)

    def get_log_data(self, data_sample: DataSample, state_progression: torch.Tensor, loss: LossResult):
        result = _legacy_generate_video_array(
            self.trainer.nca,
            self.seed_factory(),
            steps=self.steps,
            rgb_channels=self.rgb_channels
        )

        if result.shape[1] == 1:
            result = np.repeat(result, 3, axis=1)

        log_data = {
            self.log_name: wandb.Video(
                blend_alpha(result[::self.take_every]).astype("uint8") if self.has_alpha else result[::self.take_every],
                caption=f"Sample video ({self.steps} steps)",
                format="gif",
                fps=self.fps
            )
        }

        # Add final image
        if self.log_image:
            log_data[f"{self.log_name} (Image)"] = wandb.Image(
                result[-1].transpose(1, 2, 0),
                caption=f"Sample Image ({self.steps} steps)",
                mode="RGBA" if self.has_alpha else "RGB"
            )

        return log_data


class WandBValidationLogger(WandBMetricLogger):
    def __init__(
            self,
            dataset: NCA_Dataset,
            loss_function: NCA_LossFunction,
            *,
            epoch_interval: int = 1000,
            batch_size=1,
            log_final: bool = False,
            prefix: Optional[str] = None,
            eval_steps=(0, 300, 1000, 2000)
    ):
        super().__init__(epoch_interval=epoch_interval, log_final=log_final, prefix=prefix)
        self.dataset = dataset
        self.loss_function = loss_function
        self.steps = max(eval_steps)
        self.batch_size = batch_size
        self.eval_steps = list(eval_steps)
        self.batcher = SimpleBatcher(self.dataset, self.batch_size)

    def get_log_data(
            self,
            data_sample: DataSample,
            state_progression: torch.Tensor,
            loss: LossResult
    ) -> dict[str, Any]:
        log_data = {}
        with torch.no_grad():
            sample = self.batcher.next_batch()
            state = sample.states.detach()
            nca = self.trainer.nca
            kwargs = sample.get_kwargs(nca.required_kwargs())
            for step in range(self.steps):
                this_kwargs = {key: value[step] for key, value in kwargs.items()}

                state = nca(state, **this_kwargs)

                if (step + 1) in self.eval_steps:
                    loss = self.loss_function(state[None], sample.targets)
                    log_data[f"validation_{step + 1}"] = loss.total_loss(ignore_inf=False)

        return log_data
