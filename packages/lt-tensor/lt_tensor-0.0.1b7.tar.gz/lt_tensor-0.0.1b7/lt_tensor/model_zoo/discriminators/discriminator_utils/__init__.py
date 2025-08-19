from lt_utils.common import *
import torch
import inspect
from torch import nn, optim, Tensor
from lt_tensor.model_base import Model
import random
from abc import abstractmethod, ABC

C_TN: TypeAlias = Callable[[Tensor], Tensor]


class DiscriminatorBaseV2(Model, ABC):
    def init_weights(
        self,
        negative_slope: float = 0.1,
        mean: float = 0.0,
        std: Optional[float] = 0.2,
        mode: Literal["fan_in", "fan_out"] = "fan_in",
    ):
        """
        mode: Literal['fan_in', 'fan_out']: Choosing 'fan_in' preserves the magnitude of the variance of the weights in the forward pass.
                                            Choosing 'fan_out' preserves the magnitudes in the backwards pass.
        """
        for param in self.parameters():
            if param.data.ndim < 2:  # biasses
                nn.init.normal_(param, mean=mean, std=std)
            else:
                nn.init.kaiming_normal_(param, a=negative_slope, mode=mode)

    def forward(
        self,
        generated: Tensor,
        target: Tensor,
        diff: Optional[Tensor] = None,
        *,
        step_type: Literal["discriminator", "generator"] = "discriminator",
    ):
        assert (
            step_type == "generator" or diff is not None
        ), "For a discriminator step the 'diff' value is required."
        # merging the source and target and leaving the order randomized
        if step_type == "generator":
            return self.generator_step(generated, target)
        return self.discriminator_step(generated.detach(), target, diff.detach())

    def inference(
        self,
        generated: Tensor,
        target: Tensor,
        diff: Optional[Tensor] = None,
        *,
        step_type: Literal["discriminator", "generator"] = "discriminator",
    ):
        return super().inference(
            generated=generated, target=target, diff=diff, step_type=step_type
        )

    def train_step(
        self,
        generated: Tensor,
        target: Tensor,
        diff: Optional[Tensor] = None,
        *,
        step_type: Literal["discriminator", "generator"] = "discriminator",
    ):
        return super().train_step(
            generated=generated, target=target, diff=diff, step_type=step_type
        )

    # required
    @abstractmethod
    def generator_step(
        self, generated: Tensor, target: Tensor
    ) -> Tuple[Tensor, Tensor]:
        # feature_loss = 0.0
        # score = 0.0
        pass

    def discriminator_step(
        self, generated: Tensor, target: Tensor, diff: Tensor
    ) -> Tuple[Tensor, Tensor]:
        raise NotImplementedError("discriminator step not implemented!")

    def get_optimizer(
        self,
        lr: float = 2e-4,
        weight_decay: float = 5e-2,
        betas: Tuple = (0.9, 0.999),
        verbose: bool = False,
    ):
        decay = []  # 2 or more n-dims
        no_decay = []  # less than 2 (biases) do not decay
        for param in self.parameters():
            if not param.requires_grad:
                continue  # no grad = out
            if param.ndim >= 2:
                decay.append(param)
            else:
                no_decay.append(param)

        optim_groups = [
            {"params": decay, "weight_decay": weight_decay},
            {"params": no_decay, "weight_decay": 0.0},
        ]

        use_fused = (
            "fused" in inspect.signature(optim.AdamW).parameters
        ) and self.device.type == "cuda"
        optimizer = torch.optim.AdamW(
            optim_groups, lr=lr, betas=betas, fused=use_fused or None
        )
        if verbose:
            print(f"Learning rate set to: {lr}")
            print(f"using fused AdamW: {use_fused}")
            self.print_trainable_parameters()
            self.print_non_trainable_parameters()
        return optimizer


class MultiDiscriminatorBase(DiscriminatorBaseV2):
    """TODO: Find a use-case for this"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def forward(
        self,
        generated: Tensor,
        target: Tensor,
        step_type: Literal["discriminator", "generator"] = "discriminator",
    ) -> Tuple[Tensor, Tensor]:
        pass


class MultiDiscriminatorWrapper(Model):
    """TODO: Find a use-case for this"""

    def __init__(
        self,
        list_discriminator: Union[
            List[Union[DiscriminatorBaseV2, MultiDiscriminatorBase]], nn.ModuleList
        ],
    ):
        self.disc: Sequence[Callable[[Tensor, Tensor, str], Tuple[Tensor, Tensor]]] = (
            nn.ModuleList(list_discriminator)
            if isinstance(list_discriminator, (list, tuple, set))
            else list_discriminator
        )
        self.total = len(self.disc)
