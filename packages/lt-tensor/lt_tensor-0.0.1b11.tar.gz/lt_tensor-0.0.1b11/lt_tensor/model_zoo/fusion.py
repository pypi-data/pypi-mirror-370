__all__ = [
    "ConcatFusion",
    "FiLMFusion",
    "BilinearFusion",
    "CrossAttentionFusion",
    "GatedFusion",
]
from lt_utils.common import *
import torch
from torch import nn, Tensor
from lt_tensor.model_base import Model
import torch.nn.functional as F


class ConcatFusion(Model):
    def __init__(self, in_dim_a: int, in_dim_b: int, out_dim: int):
        super().__init__()
        self.proj = nn.Linear(in_dim_a + in_dim_b, out_dim)

    def forward(self, a: Tensor, b: Tensor) -> Tensor:
        x = torch.cat([a, b], dim=-1)
        return self.proj(x)


class FiLMFusion(Model):
    def __init__(self, cond_dim: int, feature_dim: int):
        super().__init__()
        self.modulator = nn.Linear(cond_dim, 2 * feature_dim)

    def forward(self, x: Tensor, cond: Tensor) -> Tensor:
        scale, shift = self.modulator(cond).chunk(2, dim=-1)
        return x * scale + shift


class BilinearFusion(Model):
    def __init__(self, in_dim_a: int, in_dim_b: int, out_dim: int):
        super().__init__()
        self.bilinear = nn.Bilinear(in_dim_a, in_dim_b, out_dim)

    def forward(self, a: Tensor, b: Tensor) -> Tensor:
        return self.bilinear(a, b)


class CrossAttentionFusion(Model):
    def __init__(self, q_dim: int, kv_dim: int, n_heads: int = 4, d_model: int = 256):
        super().__init__()
        self.q_proj = nn.Linear(q_dim, d_model)
        self.k_proj = nn.Linear(kv_dim, d_model)
        self.v_proj = nn.Linear(kv_dim, d_model)
        self.attn = nn.MultiheadAttention(
            embed_dim=d_model, num_heads=n_heads, batch_first=True
        )

    def forward(self, query: Tensor, context: Tensor, mask: Tensor = None) -> Tensor:
        Q = self.q_proj(query)
        K = self.k_proj(context)
        V = self.v_proj(context)
        output, _ = self.attn(Q, K, V, key_padding_mask=mask)
        return output


class GatedFusion(Model):
    def __init__(self, in_dim: int):
        super().__init__()
        self.gate = nn.Sequential(nn.Linear(in_dim * 2, in_dim), nn.Sigmoid())

    def forward(self, a: Tensor, b: Tensor) -> Tensor:
        gate = self.gate(torch.cat([a, b], dim=-1))
        return gate * a + (1 - gate) * b


class AdaFusion1D(Model):
    def __init__(self, channels: int, num_features: int):
        super().__init__()
        self.fc = nn.Linear(channels, num_features * 2)
        self.norm = nn.InstanceNorm1d(num_features, affine=False)

    def forward(self, x: torch.Tensor, y: torch.Tensor, alpha: torch.Tensor):
        h = self.fc(y)
        h = h.view(h.size(0), h.size(1), 1)
        gamma, beta = torch.chunk(h, chunks=2, dim=1)
        t = (1.0 + gamma) * self.norm(x) + beta
        return t + (1 / alpha) * (torch.sin(alpha * t) ** 2)


class AdaIN1D(Model):
    def __init__(self, channels: int, num_features: int):
        super().__init__()
        self.norm = nn.InstanceNorm1d(num_features, affine=False)
        self.fc = nn.Linear(channels, num_features * 2)

    def forward(self, x, y):
        h = self.fc(y)
        h = h.view(h.size(0), h.size(1), 1)
        gamma, beta = torch.chunk(h, chunks=2, dim=1)
        return (1 + gamma) * self.norm(x) + beta

class AdaIN(Model):
    def __init__(self, cond_dim, num_features, eps=1e-5):
        """
        cond_dim: size of the conditioning input
        num_features: number of channels in the input feature map
        """
        super().__init__()
        self.linear = nn.Linear(cond_dim, num_features * 2)
        self.eps = eps

    def forward(self, x, cond):
        """
        x: [B, C, T] - input features
        cond: [B, cond_dim] - global conditioning vector (e.g., speaker/style)
        """
        B, C, T = x.size()
        # Instance normalization
        mean = x.mean(dim=2, keepdim=True)     # [B, C, 1]
        std = x.std(dim=2, keepdim=True) + self.eps  # [B, C, 1]
        x_norm = (x - mean) / std              # [B, C, T]

        # Conditioning
        gamma_beta = self.linear(cond)         # [B, 2*C]
        gamma, beta = gamma_beta.chunk(2, dim=1)  # [B, C], [B, C]
        gamma = gamma.unsqueeze(-1)            # [B, C, 1]
        beta = beta.unsqueeze(-1)              # [B, C, 1]

        return gamma * x_norm + beta
    
class FiLMBlock(Model):
    def __init__(self, activation: nn.Module = nn.Identity()):
        super().__init__()
        self.activation = activation

    def forward(self, x: Tensor, gamma: Tensor, beta: Tensor):
        beta = beta.view(x.size(0), x.size(1), 1, 1)
        gamma = gamma.view(x.size(0), x.size(1), 1, 1)
        return self.activation(gamma * x + beta)


class InterpolatedFusion(Model):
    def __init__(
        self,
        in_dim_a: int,
        in_dim_b: int,
        out_dim: int,
        mode: Literal[
            "nearest",
            "linear",
            "bilinear",
            "bicubic",
            "trilinear",
            "area",
            "nearest-exact",
        ] = "nearest",
    ):
        super().__init__()
        self.fuse = nn.Linear(in_dim_a + in_dim_b, out_dim)
        self.mode = mode

    def forward(self, a: Tensor, b: Tensor) -> Tensor:
        # a: [B, T1, D1], b: [B, T2, D2] → T1 != T2
        B, T1, _ = a.shape
        b_interp = F.interpolate(
            b.transpose(1, 2), size=T1, mode=self.mode, align_corners=False
        )
        b_interp = b_interp.transpose(1, 2)  # [B, T1, D2]
        return self.fuse(torch.cat([a, b_interp], dim=-1))
