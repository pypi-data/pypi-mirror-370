import abc
from typing import Iterable, Any, Optional

import torch
from jaxtyping import Float

from ncalib.utils.utils import NCA_Base


class LossResult:
    def __init__(
            self,
            loss_tensor: torch.Tensor,
            *,
            names: Iterable[str] = ("Loss",),
            weights: Optional[torch.Tensor | Iterable[float] | float] = None
    ):
        """
        :param loss_tensor: torch.Tensor[B x L] or torch.Tensor[B], assuming a single loss
        :param names: list[str] of length L
        """
        if len(loss_tensor.shape) == 1:
            loss_tensor = loss_tensor[:, None]
            # Should now be shape [B x 1]

        if len(loss_tensor.shape) != 2:
            raise ValueError(f"Loss-Tensor has invalid shape. Should be [B x L], but is {loss_tensor.shape}")

        self.loss_tensor = loss_tensor  # Shape [B x L]
        self.names = tuple(names)
        if weights is None:
            weights = torch.ones(len(self.names))
        elif isinstance(weights, (int, float)):
            weights = (weights,)
        self.weights: torch.Tensor = torch.as_tensor(weights)  # Shape[L]

        if len(self.names) != self.loss_tensor.shape[1]:
            raise ValueError(f"Invalid lengths for loss: names has {len(self.names)} values, "
                             f"but loss-tensor has shape {loss_tensor.shape}")
        if len(self.weights) != self.loss_tensor.shape[1]:
            raise ValueError(f"Invalid lengths for loss: weights has {len(self.weights)} values, "
                             f"but loss-tensor has shape {loss_tensor.shape}")

    def __add__(self, other: "LossResult") -> "LossResult":
        if not isinstance(other, LossResult):
            raise TypeError(f"Expects other to also be a {self.__class__.__name__} when adding (it is {type(other)}).")

        all_names = list(self.names)
        for original_name in other.names:
            name = original_name
            i = 0
            while name in all_names:
                i += 1
                name = f"{original_name}_{i}"

            all_names.append(name)

        loss_tensor = torch.cat([self.loss_tensor, other.loss_tensor], dim=1)
        return LossResult(loss_tensor, names=all_names, weights=torch.cat([self.weights, other.weights]))

    def __mul__(self, value: float) -> "LossResult":
        self.loss_tensor *= value
        return self

    def __truediv__(self, other: float) -> "LossResult":
        return self.__mul__(1 / other)

    def __rmul__(self, value: float) -> "LossResult":
        return self.__mul__(value)

    def __repr__(self):
        return f"{self.__class__.__name__}(shape={self.loss_tensor.shape}, total_loss={self.total_loss()})"

    def __getitem__(self, item) -> torch.Tensor:
        idx = self.names.index(item)
        return self.loss_tensor[:, idx] * self.weights[idx]

    @classmethod
    def from_dict(
            cls,
            data: dict[str, Float[torch.Tensor, "B"]],
            weights: Optional[Iterable[float] | float] = None
    ) -> "LossResult":
        """
        :param data: dict[str, Tensor[B]]
        :return: LossResult
        """
        stacked_data = torch.stack(list(data.values()), dim=1)
        return LossResult(stacked_data, names=data.keys(), weights=weights)

    def total_loss(self, *, ignore_inf=False) -> Float[torch.Tensor, "1"]:
        """
        :return: Tensor(1)
        """
        batchwise_loss = self.batchwise_loss()
        if ignore_inf:
            return torch.mean(batchwise_loss[torch.isfinite(batchwise_loss)])
        return torch.mean(batchwise_loss)

    def batchwise_loss(self) -> Float[torch.Tensor, "B"]:
        """
        :return: Tensor[B]
        """
        return torch.sum(self.loss_tensor * self.weights[None].to(self.loss_tensor.device), dim=1)

    def detailed_loss(self, include_total=False) -> dict[str, tuple[float, float]]:
        """
        :return: dict[name, [loss_value, weight]]
        """
        detailed_loss = {
            name: (torch.mean(batch_loss).item(), weight.item())
            for name, weight, batch_loss in
            zip(self.names, self.weights, self.loss_tensor.detach().cpu().transpose(0, 1))
        }
        if include_total and len(detailed_loss) > 1:
            detailed_loss["total"] = self.total_loss().detach().cpu().item(), 1
        return detailed_loss

    def as_unweighted(self):
        return LossResult(self.loss_tensor, names=self.names, weights=None)


class NCA_LossFunction(NCA_Base, abc.ABC):
    def __init__(self, *, weight: float = 1.):
        super().__init__()
        self.weight = weight

    @abc.abstractmethod
    def __call__(
            self,
            state_progression: Float[torch.Tensor, "N B C W H"],
            target: Float[torch.Tensor, "B ..."],
            **kwargs
    ) -> LossResult:
        pass

    def __add__(self, other: "NCA_LossFunction") -> "CombinedLossFunction":
        # Prepare each loss function so that each is an iterable of simple loss functions
        if isinstance(self, CombinedLossFunction):
            losses1 = tuple(self.loss_functions)
        else:
            losses1 = (self,)

        if isinstance(other, CombinedLossFunction):
            losses2 = tuple(other.loss_functions)
        else:
            losses2 = (other,)

        # Combine Loss function
        return CombinedLossFunction(losses1 + losses2)

    def __mul__(self, value: float) -> "NCA_LossFunction":
        if not isinstance(value, (float, int)):
            raise TypeError(f"value has to be a number (it is {type(value)})")

        self.weight *= value
        return self

    def __truediv__(self, other: float) -> "NCA_LossFunction":
        return self.__mul__(1 / other)

    def __rmul__(self, value: float) -> "NCA_LossFunction":
        return self.__mul__(value)

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["weight"] = self.weight
        return cfg


class NamedLossFunction(NCA_LossFunction, abc.ABC):
    def __init__(self, loss_name, *, weight=1):
        super().__init__(weight=weight)
        self.loss_name = loss_name

    def __call__(
            self,
            state_progression: Float[torch.Tensor, "N B C W H"],
            target: Float[torch.Tensor, "B ..."],
            **kwargs
    ) -> LossResult:
        return LossResult.from_dict({
            self.loss_name: self._calculate_loss(state_progression, target, **kwargs)
        }, weights=self.weight)

    @abc.abstractmethod
    def _calculate_loss(
            self,
            state_progression: Float[torch.Tensor, "N B C W H"],
            target: Float[torch.Tensor, "B ..."],
            **kwargs
    ) -> Float[torch.Tensor, "B"]:
        pass

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["loss_name"] = self.loss_name
        return cfg


class CombinedLossFunction(NCA_LossFunction):
    def __init__(self, loss_functions):
        super().__init__()
        self.loss_functions = loss_functions

    def __call__(
            self,
            state_progression: Float[torch.Tensor, "N B C W H"],
            target: Float[torch.Tensor, "B ..."],
            **kwargs
    ) -> LossResult:
        result = self.loss_functions[0](state_progression, target, **kwargs)
        for loss_function in self.loss_functions[1:]:
            result += loss_function(state_progression, target, **kwargs)

        return result

    def __mul__(self, value: float):
        for loss_function in self.loss_functions:
            loss_function *= value
        return self

    def to_config_dict(self) -> dict[str, Any]:
        cfg = super().to_config_dict()
        cfg["loss_functions"] = [loss_function.to_config_dict() for loss_function in self.loss_functions]
        return cfg
