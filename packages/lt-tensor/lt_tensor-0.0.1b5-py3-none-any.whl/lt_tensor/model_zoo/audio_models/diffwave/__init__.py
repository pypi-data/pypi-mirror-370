__all__ = ["DiffWave", "DiffWaveConfig", "SpectrogramUpsampler", "DiffusionEmbedding"]

import numpy as np
import torch
from torch import nn, Tensor
from typing import Union, Optional
from lt_tensor.model_base import ModelConfig

from lt_tensor.model_zoo.convs import ConvEXT
from lt_tensor.model_base import Model
from math import sqrt
from lt_utils.common import *


class DiffWaveConfig(ModelConfig):
    # Model params
    n_mels = 80
    hop_samples = 256
    residual_layers = 30
    residual_channels = 64
    dilation_cycle_length = 10
    unconditional = False
    apply_norm: Optional[Literal["weight", "spectral"]] = None
    apply_norm_resblock: Optional[Literal["weight", "spectral"]] = None
    noise_schedule: list[int] = np.linspace(1e-4, 0.05, 25).tolist()
    # settings for auto-fixes

    def __init__(
        self,
        n_mels=80,
        hop_samples=256,
        residual_layers=30,
        residual_channels=64,
        dilation_cycle_length=10,
        unconditional=False,
        noise_schedule: list[int] = np.linspace(1e-4, 0.05, 50).tolist(),
        apply_norm: Optional[Literal["weight", "spectral"]] = None,
        apply_norm_resblock: Optional[Literal["weight", "spectral"]] = None,
    ):
        settings = {
            "n_mels": n_mels,
            "hop_samples": hop_samples,
            "residual_layers": residual_layers,
            "dilation_cycle_length": dilation_cycle_length,
            "residual_channels": residual_channels,
            "unconditional": unconditional,
            "noise_schedule": noise_schedule,
            "apply_norm": apply_norm,
            "apply_norm_resblock": apply_norm_resblock,
        }
        super().__init__(**settings)


class DiffusionEmbedding(Model):
    def __init__(self, max_steps: int):
        super().__init__()
        self.register_buffer(
            "embedding", self._build_embedding(max_steps), persistent=False
        )
        self.projection1 = nn.Linear(128, 512)
        self.projection2 = nn.Linear(512, 512)
        self.activation = nn.SiLU()

    def forward(self, diffusion_step):
        if diffusion_step.dtype in [torch.int32, torch.int64]:
            x = self.embedding[diffusion_step]
        else:
            x = self._lerp_embedding(diffusion_step)
        x = self.projection1(x)
        x = self.activation(x)
        x = self.projection2(x)
        x = self.activation(x)
        return x

    def _lerp_embedding(self, t):
        low_idx = torch.floor(t).long()
        high_idx = torch.ceil(t).long()
        low = self.embedding[low_idx]
        high = self.embedding[high_idx]
        return low + (high - low) * (t - low_idx)

    def _build_embedding(self, max_steps):
        steps = torch.arange(max_steps).unsqueeze(1)  # [T,1]
        dims = torch.arange(64).unsqueeze(0)  # [1,64]
        table = steps * 10.0 ** (dims * 4.0 / 63.0)  # [T,64]
        table = torch.cat([torch.sin(table), torch.cos(table)], dim=1)
        return table


class SpectrogramUpsampler(Model):
    def __init__(self):
        super().__init__()
        self.conv_net = nn.Sequential(
            ConvEXT(
                1,
                1,
                [3, 32],
                stride=[1, 16],
                padding=[1, 8],
                module_type="2d",
                transpose=True,
            ),
            nn.LeakyReLU(0.1),
            ConvEXT(
                1,
                1,
                [3, 32],
                stride=[1, 16],
                padding=[1, 8],
                module_type="2d",
                transpose=True,
            ),
            nn.LeakyReLU(0.1),
        )

    def forward(self, x: Tensor):
        return self.conv_net(x.unsqueeze(0)).squeeze(1)


class ResidualBlock(Model):
    def __init__(
        self,
        n_mels,
        residual_channels,
        dilation,
        uncond=False,
        apply_norm: Optional[Literal["weight", "spectral"]] = None,
    ):
        """
        :param n_mels: inplanes of conv1x1 for spectrogram conditional
        :param residual_channels: audio conv
        :param dilation: audio conv dilation
        :param uncond: disable spectrogram conditional
        """
        super().__init__()
        self.dilated_conv = ConvEXT(
            residual_channels,
            2 * residual_channels,
            3,
            padding=dilation,
            dilation=dilation,
            apply_norm=apply_norm,
        )
        self.diffusion_projection = nn.Linear(512, residual_channels)
        self.uncoditional = uncond
        self.conditioner_projection = None
        if not uncond:
            self.conditioner_projection = ConvEXT(
                n_mels,
                2 * residual_channels,
                1,
                apply_norm=apply_norm,
            )

        self.output_projection = ConvEXT(
            residual_channels, 2 * residual_channels, 1, apply_norm=apply_norm
        )

    def forward(
        self,
        x: Tensor,
        diffusion_step: Tensor,
        conditioner: Optional[Tensor] = None,
    ):

        diffusion_step = self.diffusion_projection(diffusion_step).unsqueeze(-1)
        y = (x + diffusion_step).squeeze(1)
        y = self.dilated_conv(y)
        if not self.uncoditional and conditioner is not None:
            y = y + self.conditioner_projection(conditioner)

        gate, _filter = y.chunk(2, dim=1)
        y = gate.sigmoid() * _filter.tanh()
        y = self.output_projection(y)
        residual, skip = y.chunk(2, dim=1)
        return (x + residual) / sqrt(2.0), skip


class DiffWave(Model):
    def __init__(
        self, cfg: Union[DiffWaveConfig, dict[str, object]] = DiffWaveConfig()
    ):
        super().__init__()
        cfg = cfg if isinstance(cfg, DiffWaveConfig) else DiffWaveConfig(**cfg)
        self.cfg = cfg
        self.n_hop = self.cfg.hop_samples
        self.input_projection = ConvEXT(
            in_channels=1,
            out_channels=cfg.residual_channels,
            kernel_size=1,
            apply_norm=self.cfg.apply_norm,
            activation_out=nn.LeakyReLU(0.1),
        )
        self.diffusion_embedding = DiffusionEmbedding(len(cfg.noise_schedule))
        self.spectrogram_upsampler = (
            SpectrogramUpsampler() if not self.cfg.unconditional else None
        )

        self.residual_layers = nn.ModuleList(
            [
                ResidualBlock(
                    cfg.n_mels,
                    cfg.residual_channels,
                    2 ** (i % cfg.dilation_cycle_length),
                    uncond=cfg.unconditional,
                    apply_norm=self.cfg.apply_norm_resblock,
                )
                for i in range(cfg.residual_layers)
            ]
        )
        self.skip_projection = ConvEXT(
            in_channels=cfg.residual_channels,
            out_channels=cfg.residual_channels,
            kernel_size=1,
            apply_norm=self.cfg.apply_norm,
            activation_out=nn.LeakyReLU(0.1),
        )
        self.output_projection = ConvEXT(
            cfg.residual_channels,
            1,
            1,
            apply_norm=self.cfg.apply_norm,
            init_weights=True,
        )
        self.activation = nn.LeakyReLU(0.1)
        self._res_d = sqrt(len(self.residual_layers))

    def forward(
        self,
        audio: Tensor,
        diffusion_step: Tensor,
        spectrogram: Optional[Tensor] = None,
    ):
        if not self.cfg.unconditional:
            assert spectrogram is not None
        if audio.ndim < 3:
            if audio.ndim == 2:
                audio = audio.unsqueeze(1)
            else:
                audio = audio.unsqueeze(0).unsqueeze(0)

        x = self.input_projection(audio)
        diffusion_step = self.diffusion_embedding(diffusion_step)
        if not self.cfg.unconditional:  # use conditional model
            spectrogram = self.spectrogram_upsampler(spectrogram)

        skip = torch.zeros_like(x, device=x.device)
        for i, layer in enumerate(self.residual_layers):
            x, skip_connection = layer(x, diffusion_step, spectrogram)
            skip += skip_connection

        x = skip / self._res_d
        x = self.skip_projection(x)
        x = self.output_projection(x)
        return x
