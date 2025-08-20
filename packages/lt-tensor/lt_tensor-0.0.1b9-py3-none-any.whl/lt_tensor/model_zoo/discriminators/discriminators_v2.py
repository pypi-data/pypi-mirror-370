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
from lt_tensor.model_zoo.discriminators.discriminator_utils import C_TN, DiscriminatorBaseV2

# models for now
__all__ = ["PXDisc"]

class PXDisc(DiscriminatorBaseV2):
    def __init__(
        self,
        input_size: int = 8192,
        kernel_sizes: Tuple[int, int] = (3, 1),
        use_spectral_norm: bool = False,
        loss_fn: Callable[[Tensor, Tensor], Tensor] = nn.L1Loss(),
    ):
        super().__init__()
        assert input_size % 2 == 0, "Input size must be divisible by 2!"
        assert input_size >= 128, "Input size be >= 128"
        # merger to unify the audios
        self.input_size = input_size
        self.gate_size = input_size
        self.loss_fn = loss_fn
        norm_f = weight_norm if not use_spectral_norm else spectral_norm

        gp = lambda ks, dl: int((ks * dl - dl) / 2)

        initial_kwargs = dict(
            kernel_size=kernel_sizes,
            padding=(gp(kernel_sizes[0], 1), gp(kernel_sizes[-1], 1)),
        )
        self.encoder_conv: List[C_TN] = nn.ModuleList(
            [
                norm_f(nn.Conv2d(2, 8, **initial_kwargs)),
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
            self.hidden.append(nn.LeakyReLU(0.1))

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

        self.out_proj: C_TN = nn.Sequential(
            nn.LeakyReLU(0.1),
            norm_f(nn.Conv1d(5, 2, 7, padding=3, bias=True)),
            nn.LeakyReLU(0.1),
            norm_f(nn.Conv1d(2, 1, 3, padding=1, bias=False)),
            nn.LeakyReLU(0.1),
            nn.Linear(self.gate_size, 2),
        )
        self.total_layers = len(self.encoder_conv)
        self.init_weights()

    @torch.no_grad()
    def _get_label(
        self,
        diff: Tensor,
        reversed: bool = False,
        batch: int = 1,
    ):
        if batch == 1:
            tn = torch.ones((2,), device=self.device)
        else:
            tn = torch.ones((batch, 2), device=self.device)
        tn = (tn * diff).clamp(-1.0, 1.0)
        if reversed:
            tn[..., 1] = -tn[..., 1]
        else:
            tn[..., 0] = -tn[..., 0]
        return tn

    def _join_sources(self, src: Tensor, tgt: Tensor) -> Tuple[Tensor, bool]:
        src = src.view(-1, 1, 1, src.shape[-1])
        tgt = tgt.view(-1, 1, 1, tgt.shape[-1])
        if random.random() <= 0.5:
            return torch.cat([tgt, src], dim=1), True
        return torch.cat([src, tgt], dim=1), False

    def _get_sorted_features(self, x: Tensor, reversed: bool):
        parts = list(x.split(1, dim=-1))
        if reversed:
            parts.reverse()
        return parts

    @torch.no_grad()
    def get_label(
        self,
        diff: Tensor,
        reversed: bool = False,
        batch: int = 1,
    ):
        if batch == 1:
            tn = torch.ones((2,), device=self.device)
        else:
            tn = torch.ones((batch, 2), device=self.device)
        tn = (tn * diff).clamp(-1.0, 1.0)
        if reversed:
            tn[..., 1] = -tn[..., 1]
        else:
            tn[..., 0] = -tn[..., 0]
        return tn
    
    def _forward(self, x: Tensor, rev: bool, gen: bool):
        if gen:
            feat_losses = 0.0

        for en in self.encoder_conv:
            x = en(x)
            if gen:
                parts = self._get_sorted_features(x, rev)
                feat_losses += self.loss_fn(parts[0], parts[1])
        x = self.hidden(x)
        if gen:
            parts = self._get_sorted_features(x, rev)
            feat_losses += self.loss_fn(parts[0], parts[1])
        x = self.out_proj(x.squeeze(1)).squeeze().tanh()
        if gen:
            return x[..., int(rev)], feat_losses
        return x

    def generator_step(
        self, generated: Tensor, target: Tensor
    ) -> Tuple[Tensor, Tensor]:
        x, rev = self._join_sources(generated, target)
        return self._forward(x, rev, True)

    def discriminator_step(
        self, generated: Tensor, target: Tensor, diff: Tensor
    ) -> Tuple[Tensor, Tensor]:
        B = 1 if generated.ndim <= 1 else generated.shape[0]
        x, rev = self._join_sources(generated, target)
        x = self._forward(x, rev, False)
        return x, self.get_label(diff.detach(), rev, B)
