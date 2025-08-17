import time
import warnings
from typing import Optional, Any

import torch
from torch.utils.checkpoint import checkpoint_sequential

from ncalib.nca.modular_nca import ModularNCA
from ncalib.trainer import NCA_Trainer, NCA_StoppingCriterion, MaxEpochs, NCA_Logger
from ncalib.trainer.batcher import NCA_Batcher
from ncalib.trainer.logger import NoOPLogger
from ncalib.trainer.loss_function import NCA_LossFunction
from ncalib.utils.utils import optimizer_to_config, scheduler_to_config


class CombinedTrainer(NCA_Trainer):
    def __init__(
            self,
            nca: ModularNCA,
            data_batcher: NCA_Batcher,
            loss_function: NCA_LossFunction,
            *,
            use_checkpointing: bool = False,
            clip_grad_norm: Optional[float] = None,
            normalize_gradients: bool = True,
            optimizer: Optional[torch.optim.Optimizer] = None,
            scheduler: Optional[Any] = None,  # Needs to be of type torch.optim._LRScheduler
    ):
        super().__init__(
            nca=nca,
            optimizer=optimizer,
            scheduler=scheduler,
        )

        self.data_batcher = data_batcher
        self.loss_function = loss_function
        self.use_checkpointing = use_checkpointing
        self.clip_grad_norm = clip_grad_norm
        self.normalize_gradients = normalize_gradients

    def train(
            self,
            stopping_criterion: NCA_StoppingCriterion = MaxEpochs(1000),
            *,
            loggers: NCA_Logger | None = None
    ):
        if loggers is None:
            loggers = NoOPLogger()
        self.nca.train()
        self.data_batcher.init()

        self.logger.info(f"Initializing loggers...")
        loggers.init_training(self, stopping_criterion)

        sample = None
        loss = None
        state_progression = None

        self._time_started = time.perf_counter()
        self._epoch = 0
        while not stopping_criterion(self, sample, state_progression, loss):
            self._epoch += 1

            # Get state and target
            with torch.no_grad():
                sample = self.data_batcher.next_batch()
                state = sample.states.detach()
                kwargs = sample.get_kwargs(self.nca.required_kwargs())

            # Go through NCA
            # First use checkpointing for first steps if enabled
            # Step through remaining steps manually
            current_step = 0
            state_progression = [state.clone().detach()]
            if self.use_checkpointing:
                warnings.warn("Checkpoint currently seems broken. Please do NOT use!")
                if len(sample.kwargs) > 0:
                    raise NotImplementedError("NCA kwargs currently not implemented with checkpointing. "
                                              f"Please set `use_checkpointing` to `False`. "
                                              f"(Existing keys: {kwargs.keys()})")
                current_step = sample.n_steps.min()
                state = checkpoint_sequential(
                    [self.nca] * current_step,
                    16,  # Segments.
                    state
                )

            for step in range(current_step, sample.n_steps.max().item()):
                with torch.no_grad():
                    state_mask = (sample.n_steps >= step)
                    this_kwargs = {key: value[step] for key, value in kwargs.items()}

                state[state_mask] = self.nca(state[state_mask], **this_kwargs)
                state_progression.append(state.clone())
                # cv2.imshow("Step", state_to_bgr_numpy(state, channels=slice(1,4)))
                # cv2.imshow("Angle", state[0,0].detach().cpu().numpy())
                # cv2.waitKey(50)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            state_progression = torch.stack(state_progression, dim=0)

            # Calculate Loss
            loss = self.loss_function(state_progression, sample.targets)

            # Backpropagation
            total_loss = loss.total_loss(ignore_inf=False)

            if not torch.isfinite(total_loss):
                self.logger.warn(f"Ignoring loss! {loss.loss_tensor.mean().item()}")
            else:
                self.optimizer.zero_grad(set_to_none=True)
                self.fabric.backward(total_loss)

                if self.normalize_gradients:
                    for p in self.nca.parameters():
                        p.grad /= p.grad.norm() + 1e-8

                if self.clip_grad_norm is not None:
                    torch.nn.utils.clip_grad_norm_(self.nca.parameters(), self.clip_grad_norm)

                self.optimizer.step()
                if self.scheduler is not None:
                    self.scheduler.step()

            sample.update_sample(new_state=state, loss=loss)
            self.data_batcher.feedback(sample, new_state=state, loss=loss)

            # Logging
            self.losses.append(total_loss.detach().cpu().item())
            loggers.log(sample, state_progression=state_progression, loss=loss)

        # Finish and clean up training
        loggers.close(sample, state_progression=state_progression, loss=loss)

        self._time_finished = time.perf_counter()
        self.logger.info(f"Training finished after {self.training_duration} seconds. "
                         f"Reason {stopping_criterion.message}")

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["nca"] = self.nca.to_config_dict()
        cfg["optimizer"] = optimizer_to_config(self.optimizer)
        cfg["scheduler"] = scheduler_to_config(self.scheduler)
        cfg["data_batcher"] = self.data_batcher.to_config_dict()
        cfg["loss_function"] = self.loss_function.to_config_dict()
        cfg["use_checkpointing"] = self.use_checkpointing
        cfg["clip_grad_norm"] = self.clip_grad_norm
        cfg["normalize_gradients"] = self.normalize_gradients
        return cfg
