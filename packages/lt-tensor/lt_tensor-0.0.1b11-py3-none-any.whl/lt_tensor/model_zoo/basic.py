__all__ = [
    "FeedForward",
    "MLP",
    "TimestepEmbedder",
    "GRUEncoder",
    "ConvBlock1D",
    "TemporalPredictor",
    "StyleEncoder",
    "PatchEmbed1D",
    "MultiScaleEncoder1D",
    "UpSampleConv1D",
]
import torch.nn.functional as F
import torch
from torch.nn.utils.parametrizations import weight_norm
from torch import nn, Tensor
from lt_tensor.model_base import Model
from lt_tensor.transform import get_sinusoidal_embedding
from lt_utils.common import *
import math
from einops import repeat


class FeedForward(Model):
    def __init__(
        self,
        d_model: int,
        ff_dim: int,
        dropout: float = 0.01,
        activation: nn.Module = nn.LeakyReLU(0.1),
        normalizer: nn.Module = nn.Identity(),
    ):
        """Creates a Feed-Forward Layer, with the chosen activation function and the normalizer."""
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, ff_dim),
            activation,
            nn.Dropout(dropout),
            nn.Linear(ff_dim, ff_dim),
            activation,
            nn.Dropout(dropout),
            nn.Linear(ff_dim, d_model),
            normalizer,
        )

    def forward(self, x: Tensor):
        return self.net(x)


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


class MLP(Model):
    def __init__(
        self,
        d_model: int,
        ff_dim: int,
        n_classes: int,
        dropout: float = 0.01,
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        """Creates a MLP block, with the chosen activation function and the normalizer."""
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, ff_dim),
            activation,
            nn.Dropout(dropout),
            nn.Linear(ff_dim, n_classes),
        )

    def forward(self, x: Tensor):
        return self.net(x)


class TimestepEmbedder(Model):
    def __init__(self, dim_emb: int, proj_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim_emb, proj_dim),
            nn.SiLU(),
            nn.Linear(proj_dim, proj_dim),
        )

    def forward(self, t: torch.Tensor) -> torch.Tensor:
        # t: [B] (long)
        emb = get_sinusoidal_embedding(t, self.net[0].in_features)  # [B, dim_emb]
        return self.net(emb)  # [B, proj_dim]


class GRUEncoder(Model):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        num_layers: int = 1,
        bidirectional: bool = False,
    ):
        super().__init__()
        self.gru = nn.GRU(
            input_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional,
        )
        self.output_dim = hidden_dim * (2 if bidirectional else 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, input_dim]
        output, _ = self.gru(x)  # output: [B, T, hidden_dim*D]
        return output


class ConvBlock1D(Model):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        norm: bool = True,
        residual: bool = False,
    ):
        super().__init__()
        padding = (kernel_size - 1) // 2
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size, stride, padding)
        self.norm = nn.BatchNorm1d(out_channels) if norm else nn.Identity()
        self.act = nn.LeakyReLU(0.1)
        self.residual = residual and in_channels == out_channels

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.act(self.norm(self.conv(x)))
        return x + y if self.residual else y


class TemporalPredictor(Model):
    def __init__(
        self,
        d_model: int,
        hidden_dim: int = 128,
        n_layers: int = 2,
        dropout: float = 0.1,
    ):
        super().__init__()
        layers = []
        for _ in range(n_layers):
            layers.append(nn.Conv1d(d_model, hidden_dim, kernel_size=3, padding=1))
            layers.append(nn.LeakyReLU(0.1))
            layers.append(nn.LayerNorm(hidden_dim))
            layers.append(nn.Dropout(dropout))
            d_model = hidden_dim
        self.network = nn.Sequential(*layers)
        self.proj = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, D]
        x = x.transpose(1, 2)  # [B, D, T]
        x = self.network(x)  # [B, H, T]
        x = x.transpose(1, 2)  # [B, T, H]
        return self.proj(x).squeeze(-1)  # [B, T]


class StyleEncoder(Model):
    def __init__(self, in_channels: int = 80, hidden: int = 128, out_dim: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(in_channels, hidden, kernel_size=3, stride=2, padding=1),
            nn.LeakyReLU(0.1),
            nn.Conv1d(hidden, hidden, kernel_size=3, stride=2, padding=1),
            nn.LeakyReLU(0.1),
            nn.AdaptiveAvgPool1d(1),
        )
        self.linear = nn.Linear(hidden, out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.net(x).squeeze(-1)  # [B, hidden]
        return self.linear(x)  # [B, out_dim]


class PatchEmbed1D(Model):
    def __init__(self, in_channels: int, patch_size: int, embed_dim: int):
        """
        Args:
            in_channels: number of input channels (e.g., mel bins)
            patch_size: number of time-steps per patch
            embed_dim: dimension of the patch embedding
        """
        super().__init__()
        self.patch_size = patch_size
        self.proj = nn.Conv1d(
            in_channels, embed_dim, kernel_size=patch_size, stride=patch_size
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, C, T]
        x = self.proj(x)  # [B, embed_dim, T//patch_size]
        return x.transpose(1, 2)  # [B, T_patches, embed_dim]


class MultiScaleEncoder1D(Model):
    def __init__(
        self, in_channels: int, hidden: int, num_layers: int = 4, kernel_size: int = 3
    ):
        super().__init__()
        layers = []
        for i in range(num_layers):
            layers.append(
                nn.Conv1d(
                    in_channels if i == 0 else hidden,
                    hidden,
                    kernel_size=kernel_size,
                    dilation=2**i,
                    padding=(kernel_size - 1) * (2**i) // 2,
                )
            )
            layers.append(nn.GELU())
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, C, T]
        return self.net(x)  # [B, hidden, T]


class AudioClassifier(Model):
    def __init__(self, n_mels: int = 80, num_classes=5):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv1d(n_mels, 256, kernel_size=3, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(256, 256, kernel_size=3, padding=1, groups=4),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2),
            nn.Conv1d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2),
            nn.AdaptiveAvgPool1d(1),  # Output shape: [B, 64, 1]
            nn.Flatten(),  # -> [B, 64]
            nn.Linear(256, num_classes),
        )
        self.eval()

    def forward(self, x):
        return self.model(x)


class LoRALinearLayer(nn.Module):

    def __init__(
        self,
        in_features: int,
        out_features: int,
        rank: int = 4,
        alpha: float = 1.0,
    ):
        super().__init__()
        self.down = nn.Linear(in_features, rank, bias=False)
        self.up = nn.Linear(rank, out_features, bias=False)
        self.alpha = alpha
        self.rank = rank
        self.out_features = out_features
        self.in_features = in_features
        self.ah = self.alpha / self.rank
        self._down_dt = self.down.weight.dtype

        nn.init.normal_(self.down.weight, std=1 / rank)
        nn.init.zeros_(self.up.weight)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        orig_dtype = hidden_states.dtype
        down_hidden_states = self.down(hidden_states.to(self._down_dt))
        up_hidden_states = self.up(down_hidden_states) * self.ah
        return up_hidden_states.to(orig_dtype)


class LoRAConv1DLayer(Model):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        kernel_size: Union[int, Tuple[int, ...]] = 1,
        rank: int = 4,
        alpha: float = 1.0,
    ):
        super().__init__()
        self.down = nn.Conv1d(
            in_features, rank, kernel_size, padding=kernel_size // 2, bias=False
        )
        self.up = nn.Conv1d(
            rank, out_features, kernel_size, padding=kernel_size // 2, bias=False
        )
        self.ah = alpha / rank
        self._down_dt = self.down.weight.dtype
        nn.init.kaiming_uniform_(self.down.weight, a=math.sqrt(5))
        nn.init.zeros_(self.up.weight)

    def forward(self, inputs: Tensor) -> Tensor:
        orig_dtype = inputs.dtype
        down_hidden_states = self.down(inputs.to(self._down_dt))
        up_hidden_states = self.up(down_hidden_states) * self.ah
        return up_hidden_states.to(orig_dtype)


class LoRAConv2DLayer(Model):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        kernel_size: Union[int, Tuple[int, ...]] = (1, 1),
        rank: int = 4,
        alpha: float = 1.0,
    ):
        super().__init__()
        self.down = nn.Conv2d(
            in_features,
            rank,
            kernel_size,
            padding="same",
            bias=False,
        )
        self.up = nn.Conv2d(
            rank,
            out_features,
            kernel_size,
            padding="same",
            bias=False,
        )
        self.ah = alpha / rank

        nn.init.kaiming_normal_(self.down.weight, a=0.2)
        nn.init.zeros_(self.up.weight)

    def forward(self, inputs: Tensor) -> Tensor:
        orig_dtype = inputs.dtype
        down_hidden_states = self.down(inputs.to(self._down_dt))
        up_hidden_states = self.up(down_hidden_states) * self.ah
        return up_hidden_states.to(orig_dtype)


class SineGen(Model):
    def __init__(
        self,
        samp_rate,
        upsample_scale,
        harmonic_num=0,
        sine_amp=0.1,
        noise_std=0.003,
        voiced_threshold=0,
        flag_for_pulse=False,
    ):
        super().__init__()
        self.sampling_rate = samp_rate
        self.upsample_scale = upsample_scale
        self.harmonic_num = harmonic_num
        self.sine_amp = sine_amp
        self.noise_std = noise_std
        self.voiced_threshold = voiced_threshold
        self.flag_for_pulse = flag_for_pulse
        self.dim = self.harmonic_num + 1  # fundamental + harmonics

    def _f02uv_b(self, f0):
        return (f0 > self.voiced_threshold).float()  # [B, T]

    def _f02uv(self, f0):
        return (f0 > self.voiced_threshold).float().unsqueeze(-1)  # -> (B, T, 1)

    @torch.no_grad()
    def _f02sine(self, f0_values):
        """
        f0_values: (B, T, 1)
        Output: sine waves (B, T * upsample, dim)
        """
        B, T, _ = f0_values.size()
        f0_upsampled = repeat(
            f0_values, "b t d -> b (t r) d", r=self.upsample_scale
        )  # (B, T_up, 1)

        # Create harmonics
        harmonics = (
            torch.arange(1, self.dim + 1, device=f0_values.device)
            .float()
            .view(1, 1, -1)
        )
        f0_harm = f0_upsampled * harmonics  # (B, T_up, dim)

        # Convert Hz to radians (2πf/sr), then integrate to get phase
        rad_values = f0_harm / self.sampling_rate  # normalized freq
        rad_values = rad_values % 1.0  # remove multiples of 2π

        # Random initial phase for each harmonic (except 0th if pulse mode)
        if self.flag_for_pulse:
            rand_ini = torch.zeros((B, 1, self.dim), device=f0_values.device)
        else:
            rand_ini = torch.rand((B, 1, self.dim), device=f0_values.device)

        rand_ini = rand_ini * 2 * math.pi

        # Compute cumulative phase
        rad_values = rad_values * 2 * math.pi
        phase = torch.cumsum(rad_values, dim=1) + rand_ini  # (B, T_up, dim)

        sine_waves = torch.sin(phase)  # (B, T_up, dim)
        return sine_waves

    def _forward(self, f0):
        """
        f0: (B, T, 1)
        returns: sine signal with harmonics and noise added
        """
        sine_waves = self._f02sine(f0)  # (B, T_up, dim)
        uv = self._f02uv_b(f0)  # (B, T, 1)
        uv = repeat(uv, "b t d -> b (t r) d", r=self.upsample_scale)  # (B, T_up, 1)

        # voiced sine + unvoiced noise
        sine_signal = self.sine_amp * sine_waves * uv  # (B, T_up, dim)
        noise = torch.randn_like(sine_signal) * self.noise_std
        output = sine_signal + noise * (1.0 - uv)  # noise added only on unvoiced

        return output  # (B, T_up, dim)

    def forward(self, f0):
        """
        Args:
            f0: (B, T) in Hz (before upsampling)
        Returns:
            sine_waves: (B, T_up, dim)
            uv: (B, T_up, 1)
            noise: (B, T_up, 1)
        """
        B, T = f0.shape
        device = f0.device

        # Get uv mask (before upsampling)
        uv = self._f02uv(f0)  # (B, T, 1)

        # Expand f0 to include harmonics: (B, T, dim)
        f0 = f0.unsqueeze(-1)  # (B, T, 1)
        harmonics = (
            torch.arange(1, self.dim + 1, device=device).float().view(1, 1, -1)
        )  # (1, 1, dim)
        f0_harm = f0 * harmonics  # (B, T, dim)

        # Upsample
        f0_harm_up = repeat(
            f0_harm, "b t d -> b (t r) d", r=self.upsample_scale
        )  # (B, T_up, dim)
        uv_up = repeat(uv, "b t d -> b (t r) d", r=self.upsample_scale)  # (B, T_up, 1)

        # Convert to radians
        rad_per_sample = f0_harm_up / self.sampling_rate  # Hz → cycles/sample
        rad_per_sample = rad_per_sample * 2 * math.pi  # cycles → radians/sample

        # Random phase init for each sample
        B, T_up, D = rad_per_sample.shape
        rand_phase = torch.rand(B, D, device=device) * 2 * math.pi  # (B, D)

        # Compute cumulative phase
        phase = torch.cumsum(rad_per_sample, dim=1) + rand_phase.unsqueeze(
            1
        )  # (B, T_up, D)

        # Apply sine
        sine_waves = torch.sin(phase) * self.sine_amp  # (B, T_up, D)

        # Handle unvoiced: create noise only for fundamental
        noise = torch.randn(B, T_up, 1, device=device) * self.noise_std
        if self.flag_for_pulse:
            # If pulse mode is on, align phase at start of voiced segments
            # Optional and tricky to implement — may require segmenting uv
            pass

        # Replace sine by noise for unvoiced (only on fundamental)
        sine_waves[:, :, 0:1] = sine_waves[:, :, 0:1] * uv_up + noise * (1 - uv_up)

        return sine_waves, uv_up, noise
