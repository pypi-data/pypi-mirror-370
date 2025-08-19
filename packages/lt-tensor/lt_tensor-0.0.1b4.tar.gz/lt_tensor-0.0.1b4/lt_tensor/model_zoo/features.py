__all__ = [
    "Downsample1D",
    "Upsample1D",
    "DiffusionUNet",
    "UNetConvBlock1D",
    "UNetUpBlock1D",
    "NoisePredictor1D",
    "AdaINFeaturesBlock1D",
    "UpSampleConv1D",
]
import math
import torch
from torch import nn, Tensor
from torch.nn.utils.parametrizations import weight_norm
from lt_tensor.model_base import Model
from lt_tensor.model_zoo.residual import ResBlock1D
from lt_tensor.model_zoo.fusion import AdaIN1D, CrossAttentionFusion
import torch.nn.functional as F
from lt_tensor.misc_utils import get_activated_conv
from lt_utils.common import *


class FeatureExtractor(Model):
    def __init__(
        self,
        in_channels: int = 1,
        out_channels: int = 32,
        hidden: int = 128,
        groups: tuple[int] = [1, 1, 1, 1, 1],
        kernels: tuple[int, int, int, int, int] = (5, 3, 3, 3, 3),
        padding: tuple[int, int, int, int, int] = (2, 1, 1, 1, 1),
        stride: tuple[int, int, int, int, int] = (2, 2, 2, 1, 1),
        network: Literal[
            "Conv1d",
            "Conv2d",
            "Conv3d",
            "ConvTranspose1d",
            "ConvTranspose2d",
            "ConvTranspose3d",
        ] = "conv1d",
    ):
        super().__init__()
        self.pre_nt = get_activated_conv(
            in_channels,
            hidden,
            kernels[0],
            stride[0],
            padding[0],
            groups[0],
            conv_type=network,
        )

        self.net = nn.Sequential(
            [
                get_activated_conv(
                    hidden,
                    hidden,
                    kernels[i],
                    stride[i],
                    padding[i],
                    groups[i],
                    conv_type=network,
                )
                for i in range(1, 4)
            ],
        )
        self.post = get_activated_conv(
            hidden,
            out_channels,
            kernels[4],
            stride[4],
            padding[4],
            groups[4],
            conv_type=network,
        )

    def forward(self, x: Tensor):
        x = self.pre_nt(x)
        x = self.net(x)
        return self.post(x)


class Downsample1D(Model):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
    ):
        super().__init__()
        self.pool = nn.Conv1d(in_channels, out_channels, 4, stride=2, padding=1)

    def forward(self, x):
        return self.pool(x)


class Upsample1D(Model):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        activation=nn.ReLU(inplace=True),
    ):
        super().__init__()
        self.up = nn.Sequential(
            nn.ConvTranspose1d(
                in_channels, out_channels, kernel_size=4, stride=2, padding=1
            ),
            nn.BatchNorm1d(out_channels),
            activation,
        )

    def forward(self, x):
        return self.up(x)


class DiffusionUNet(Model):
    def __init__(self, in_channels=1, base_channels=64, out_channels=1, depth=4):
        super().__init__()

        self.depth = depth
        self.encoder_blocks = nn.ModuleList()
        self.downsamples = nn.ModuleList()
        self.upsamples = nn.ModuleList()
        self.decoder_blocks = nn.ModuleList()
        # Keep track of channel sizes per layer for skip connections
        self.channels = [in_channels]  # starting input channel
        for i in range(depth):
            enc_in = self.channels[-1]
            enc_out = base_channels * (2**i)
            # Encoder block and downsample
            self.encoder_blocks.append(ResBlock1D(enc_in, enc_out))
            self.downsamples.append(
                Downsample1D(enc_out, enc_out)
            )  # halve time, keep channels
            self.channels.append(enc_out)
        # Bottleneck
        bottleneck_ch = self.channels[-1]
        self.bottleneck = ResBlock1D(bottleneck_ch, bottleneck_ch)
        # Decoder blocks (reverse channel flow)
        for i in reversed(range(depth)):
            skip_ch = self.channels[i + 1]  # from encoder
            dec_out = self.channels[i]  # match earlier stage's output
            self.upsamples.append(Upsample1D(skip_ch, skip_ch))
            self.decoder_blocks.append(ResBlock1D(skip_ch * 2, dec_out))
        # Final output projection (out_channels)
        self.final = nn.Conv1d(in_channels, out_channels, kernel_size=1)

    def forward(self, x: Tensor):
        skips = []

        # Encoder
        for enc, down in zip(self.encoder_blocks, self.downsamples):
            # log_tensor(x, "before enc")
            x = enc(x)
            skips.append(x)
            x = down(x)

        # Bottleneck
        x = self.bottleneck(x)

        # Decoder
        for up, dec, skip in zip(self.upsamples, self.decoder_blocks, reversed(skips)):
            x = up(x)

            # Match lengths via trimming or padding
            if x.shape[-1] > skip.shape[-1]:
                x = x[..., : skip.shape[-1]]
            elif x.shape[-1] < skip.shape[-1]:
                diff = skip.shape[-1] - x.shape[-1]
                x = F.pad(x, (0, diff))

            x = torch.cat([x, skip], dim=1)  # concat on channels
            x = dec(x)

        # Final 1x1 conv
        return self.final(x)


class UNetConvBlock1D(Model):
    def __init__(self, in_channels: int, out_channels: int, down: bool = True):
        super().__init__()
        self.down = down
        self.conv = nn.Sequential(
            nn.Conv1d(
                in_channels,
                out_channels,
                kernel_size=3,
                stride=2 if down else 1,
                padding=1,
            ),
            nn.BatchNorm1d(out_channels),
            nn.LeakyReLU(0.2),
            nn.Conv1d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm1d(out_channels),
            nn.LeakyReLU(0.2),
        )
        self.downsample = (
            nn.Conv1d(in_channels, out_channels, kernel_size=1, stride=2 if down else 1)
            if in_channels != out_channels
            else nn.Identity()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, C, T]
        residual = self.downsample(x)
        return self.conv(x) + residual


class UNetUpBlock1D(Model):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm1d(out_channels),
            nn.LeakyReLU(0.2),
            nn.Conv1d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm1d(out_channels),
            nn.LeakyReLU(0.2),
        )
        self.upsample = nn.Upsample(scale_factor=2, mode="nearest")

    def forward(self, x: torch.Tensor, skip: torch.Tensor) -> torch.Tensor:
        x = self.upsample(x)
        x = torch.cat([x, skip], dim=1)  # skip connection
        return self.conv(x)


class NoisePredictor1D(Model):
    def __init__(self, in_channels: int, cond_dim: int = 0, hidden: int = 128):
        """
        Args:
            in_channels: channels of the noisy input [B, C, T]
            cond_dim: optional condition vector [B, cond_dim]
        """
        super().__init__()
        self.proj = nn.Linear(cond_dim, hidden) if cond_dim > 0 else None
        self.net = nn.Sequential(
            nn.Conv1d(in_channels, hidden, kernel_size=3, padding=1),
            nn.SiLU(),
            nn.Conv1d(hidden, in_channels, kernel_size=3, padding=1),
        )

    def forward(self, x: torch.Tensor, cond: Optional[torch.Tensor] = None):
        # x: [B, C, T], cond: [B, cond_dim]
        if cond is not None:
            cond_proj = self.proj(cond).unsqueeze(-1)  # [B, hidden, 1]
            x = x + cond_proj  # simple conditioning
        return self.net(x)  # [B, C, T]


class UpSampleConv1D(nn.Module):
    def __init__(self, upsample: bool = False, dim_in: int = 0, dim_out: int = 0):
        super().__init__()
        if upsample:
            self.upsample = lambda x: F.interpolate(x, scale_factor=2, mode="nearest")
        else:
            self.upsample = nn.Identity()

        if dim_in == dim_out:
            self.learned = nn.Identity()
        else:
            self.learned = weight_norm(nn.Conv1d(dim_in, dim_out, 1, 1, 0, bias=False))

    def forward(self, x):
        x = self.upsample(x)
        return self.learned(x)


class AdaINFeaturesBlock1D(Model):
    def __init__(
        self,
        dim_in: int,
        dim_out: int,
        style_dim: int = 64,
        actv=nn.LeakyReLU(0.2),
        upsample: bool = False,
        dropout_p=0.0,
    ):
        super().__init__()
        self.upsample = UpSampleConv1D(upsample, dim_in, dim_out)
        self.res_net = nn.ModuleDict(
            dict(
                norm_1=AdaIN1D(style_dim, dim_in),
                sq1=nn.Sequential(
                    actv,
                    (
                        nn.Identity()
                        if not upsample
                        else weight_norm(
                            nn.ConvTranspose1d(
                                dim_in,
                                dim_in,
                                kernel_size=3,
                                stride=2,
                                groups=dim_in,
                                padding=1,
                                output_padding=1,
                            )
                        )
                    ),
                    weight_norm(nn.Conv1d(dim_in, dim_out, 3, 1, 1)),
                    nn.Dropout(dropout_p),
                ),
                norm_2=AdaIN1D(style_dim, dim_out),
                sq2=nn.Sequential(
                    actv,
                    weight_norm(nn.Conv1d(dim_out, dim_out, 3, 1, 1)),
                    nn.Dropout(dropout_p),
                ),
            )
        )
        self.sq2 = math.sqrt(2)

    def forward(self, x: Tensor, y: Tensor):
        u = self.res_net["norm_1"](x, y)
        u = self.res_net["sq1"](u)
        u = self.res_net["norm_2"](u, y)
        u = self.res_net["sq2"]
        return (u + self.upsample(x)) / self.sq2


class AudioEncoder(Model):
    """Untested, hypothetical item"""

    def __init__(
        self,
        channels: int,
        alpha: float = 4.0,
        feat_channels: int = 64,
        out_features: Optional[int] = None,
        out_channels: int = 1,
        interp_mode: Literal[
            "nearest",
            "linear",
            "bilinear",
            "bicubic",
            "trilinear",
        ] = "nearest",
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()

        self.net = nn.Sequential(
            nn.Conv1d(
                channels, feat_channels, kernel_size=3, stride=1, padding=5, groups=1
            ),
            nn.LeakyReLU(0.1),
            nn.Conv1d(
                feat_channels,
                feat_channels,
                kernel_size=3,
                stride=2,
                padding=1,
                groups=feat_channels,
            ),
            nn.LeakyReLU(0.1),
            nn.Conv1d(
                feat_channels,
                feat_channels,
                kernel_size=3,
                stride=1,
                padding=1,
                groups=feat_channels // 8,
            ),
            nn.LeakyReLU(0.1),
            nn.Conv1d(
                feat_channels,
                feat_channels,
                kernel_size=7,
                stride=1,
                padding=1,
                groups=1,
            ),
        )
        self.fc = nn.Linear(feat_channels, channels)
        self.feat_channels = feat_channels
        self.activation = activation
        self.channels = channels
        self.mode = interp_mode
        self.alpha = alpha
        self.post_conv = nn.Conv1d(
            channels,
            out_channels,
            kernel_size=1,
            stride=1,
            padding=0,
            dilation=1,
            groups=1,
            bias=True,
        )
        if out_features is not None:
            self.format_out = lambda tensor: F.interpolate(
                tensor,
                size=out_features,
                mode=interp_mode,
            )
        else:
            self.format_out = nn.Identity()

    def forward(self, mels: Tensor, cr_audio: Tensor):
        sin = torch.asin(cr_audio)
        cos = torch.acos(cr_audio)
        mod = (sin * cos) / self.alpha
        mod = (mod - mod.median(dim=-1, keepdim=True).values) / (
            mod.std(dim=-1, keepdim=True) + 1e-5
        )
        x = self.net(mod)
        x = (
            F.interpolate(
                x,
                size=mels.shape[-1],
                mode=self.mode,
            )
            .transpose(-1, -2)
            .contiguous()
        )
        x = self.activation(x)

        xt = self.fc(x).transpose(-1, -2)
        out = self.post_conv(xt)
        return self.format_out(out)


class AudioEncoderAttn(Model):
    def __init__(
        self,
        channels: int,
        feat_channels: int = 64,
        alpha: float = 4.0,
        out_channels: Optional[int] = None,
        out_features: int = 1,
        interp_mode: Literal[
            "nearest",
            "linear",
            "bilinear",
            "bicubic",
            "trilinear",
        ] = "nearest",
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()

        self.net = nn.Sequential(
            nn.Conv1d(
                channels, feat_channels, kernel_size=3, stride=1, padding=1, groups=1
            ),
            nn.LeakyReLU(0.1),
            nn.Conv1d(
                feat_channels,
                feat_channels,
                kernel_size=3,
                stride=2,
                padding=5,
                groups=feat_channels,
            ),
            nn.LeakyReLU(0.1),
            nn.Conv1d(
                feat_channels,
                feat_channels,
                kernel_size=3,
                stride=1,
                padding=1,
                groups=feat_channels // 8,
            ),
            nn.LeakyReLU(0.1),
            nn.Conv1d(
                feat_channels, channels, kernel_size=7, stride=1, padding=1, groups=1
            ),
        )
        self.fusion = CrossAttentionFusion(channels, channels, 2, d_model=channels)
        self.channels = channels
        self.mode = interp_mode
        self.alpha = alpha
        self.activation = activation
        self.post_conv = nn.Conv1d(
            channels,
            out_channels,
            kernel_size=1,
            stride=1,
            padding=0,
            dilation=1,
            groups=1,
            bias=True,
        )
        if out_features is not None:
            self.format_out = lambda tensor: F.interpolate(
                tensor,
                size=out_features,
                mode=interp_mode,
            )
        else:
            self.format_out = nn.Identity()

    def forward(self, mels: Tensor, cr_audio: Tensor):
        sin = torch.asin(cr_audio)
        cos = torch.acos(cr_audio)
        mod = (sin * cos) / self.alpha
        mod = (mod - mod.median(dim=-1, keepdim=True).values) / (
            mod.std(dim=-1, keepdim=True) + 1e-5
        )
        x = self.activation(self.net(mod))
        x = F.interpolate(x, size=mels.shape[-1], mode=self.mode)
        x_t = x.transpose(-2, -1).contiguous()
        mels_t = mels.transpose(-2, -1).contiguous()

        xt = self.fusion(x_t, mels_t).transpose(-2, -1)
        out = self.post_conv(xt)
        return self.format_out(out)
