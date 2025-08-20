from __future__ import annotations

"""
All the content here is purely experimental, can be functional, unstable, not useful or broken.
Those are focused in audio, but can be tested in other domains.

"""

import torch
import random
from torch import nn, Tensor
from lt_utils.common import *
from torch.nn import functional as F
from torch.nn.utils.parametrizations import weight_norm, spectral_norm
from lt_tensor.model_zoo.discriminators.discriminator_utils import (
    C_TN,
    DiscriminatorBaseV2,
)

# models for now
__all__ = ["PXDisc"]


class PXDisc(DiscriminatorBaseV2):
    def __init__(
        self,
        input_size: int = 8192,
        kernel_sizes: Tuple[int, int] = (3, 1),
        use_spectral_norm: bool = False,
        loss_fn: Callable[[Tensor, Tensor], Tensor] = nn.L1Loss(),
        feature_sz: float = 1.0,
        generator_sz: float = 2.0,
        disc_gen_sz: float = 2.0,
        disc_real_sz: float = 1.0,
    ):
        super().__init__()
        assert input_size % 2 == 0, "Input size must be divisible by 2!"
        assert input_size >= 128, "Input size be >= 128"
        self.loss_fn = loss_fn
        self.feat_sz = feature_sz
        self.disc_gen_sz = disc_gen_sz
        self.disc_real_sz = disc_real_sz
        self.gen_sz = generator_sz
        self.input_size = input_size
        self.gate_size = input_size
        norm_f = weight_norm if not use_spectral_norm else spectral_norm

        gp = lambda ks, dl: int((ks * dl - dl) / 2)

        initial_kwargs = dict(
            kernel_size=kernel_sizes,
            padding=(gp(kernel_sizes[0], 1), gp(kernel_sizes[-1], 1)),
        )
        self.encoder_conv: List[C_TN] = nn.ModuleList(
            [
                norm_f(nn.Conv2d(1, 8, **initial_kwargs)),
                norm_f(nn.Conv2d(8, 16, stride=(1, 2), **initial_kwargs, groups=2)),
                norm_f(nn.Conv2d(16, 64, **initial_kwargs)),
                norm_f(nn.Conv2d(64, 256, stride=(1, 2), **initial_kwargs, groups=4)),
                norm_f(nn.Conv2d(256, 512, **initial_kwargs)),
                norm_f(nn.Conv2d(512, 768, stride=(1, 2), **initial_kwargs, groups=4)),
            ]
        )
        self.gate_size = int(self.gate_size / 2 / 2 / 2)
        # ---
        hidden_kernel_sizes = [(3, 1), (5, 1), (7, 1), (3, 1)]
        hidden_stride: List[int] = [1, 2, 2, 2]
        hidden_groups: List[int] = [2, 4, 2, 1]
        hidden_dilations: List[int] = [(1, 1), (2, 1), (2, 1), (1, 1)]

        self.hidden: C_TN = nn.Sequential()
        for i, (k, s, g, d) in enumerate(
            zip(hidden_kernel_sizes, hidden_stride, hidden_groups, hidden_dilations)
        ):
            p = (gp(k[0], d[0]), gp(k[-1], d[1]))

            out = 768 if i < 3 else 1

            self.hidden.append(
                norm_f(
                    nn.Conv2d(
                        768,
                        out,
                        kernel_size=k,
                        stride=1,
                        padding=p,
                        groups=g if out > 1 else 1,
                    )
                )
            )
            if s > 1:
                self.gate_size = int(self.gate_size / s)
                self.hidden.append(
                    nn.MaxPool2d(kernel_size=3, stride=(1, s), padding=(0, 1))
                )
            self.hidden.append(nn.LeakyReLU(0.1))

        self.out_proj: C_TN = nn.Sequential(
            norm_f(nn.Conv1d(5, 2, 7, padding=3, bias=True)),
            nn.LeakyReLU(0.1),
            norm_f(nn.Conv1d(2, 1, 3, padding=1, bias=False)),
            nn.LeakyReLU(0.1),
            nn.Linear(self.gate_size, 1),
        )
        self.total_layers = len(self.encoder_conv)
        self.activation = nn.LeakyReLU(0.1)
        self.init_weights()

    @torch.no_grad()
    def get_label(
        self,
        diff: Tensor,
        for_real: bool = True,
        batch: int = 1,
    ):
        tn = torch.ones((batch, 1), device=self.device)
        if for_real:
            tn = tn * diff
        else:
            tn = -(tn * diff)
        return tn

    def _forward(
        self,
        x: Tensor,
        gen: bool,
        *args,
        **kwargs,
    ) -> Union[Tensor, Tuple[Tensor, List[Tensor]]]:
        if gen:
            feat_maps = []

        for en in self.encoder_conv:
            x = en(x)
            if gen:
                feat_maps.append(x)
            x = self.activation(x)

        x = self.hidden(x)
        if gen:
            feat_maps.append(x)
            return feat_maps
        x = self.out_proj(x.squeeze(1)).squeeze().tanh()
        return x

    def expand_channels(self, x: Tensor):
        T = x.shape[-1]
        return x.view(-1, 1, 1, T)

    def generator_step(
        self,
        generated: Tensor,
        target: Tensor,
        change_train_state: bool = True,
        *args,
        **kwargs,
    ) -> Tuple[Tensor, Tensor]:
        if change_train_state and (not self.training):
            self.eval()
        T = target.shape[-1]
        with torch.no_grad():
            target_maps = self._forward(self.expand_channels(target), True)
        gen_maps = self._forward(self.expand_channels(generated), True)
        feat_loss = 0.0
        for xg, xt in zip(gen_maps, target_maps):
            feat_loss += self.loss_fn(xg.squeeze(), xt.squeeze())
        return feat_loss * self.feat_sz

    def _disc_pass_fake(self, gen: Tensor, diff: Tensor):
        B = 1 if gen.ndim < 2 else gen.shape[0]
        res = self._forward(self.expand_channels(gen), False)
        return self.loss_fn(res.squeeze(), self.get_label(diff, False, B).squeeze())

    def _disc_pass_real(self, target: Tensor, diff: Tensor):
        B = 1 if target.ndim < 2 else target.shape[0]
        res = self._forward(self.expand_channels(target), False)
        return self.loss_fn(res.squeeze(), self.get_label(diff, True, B).squeeze())

    def discriminator_step(
        self,
        generated: Tensor,
        target: Tensor,
        diff: Optional[Tensor] = None,
        change_train_state: bool = True,
        *args,
        **kwargs,
    ) -> Tuple[Tensor, Tensor]:
        if change_train_state and (not self.training):
            self.train()
        if diff is None:
            with torch.no_grad():
                diff = self.loss_fn(generated.squeeze(), target.squeeze())
        loss_fake = self._disc_pass_fake(generated, diff)
        loss_real = self._disc_pass_real(target, diff)
        return loss_fake + loss_real