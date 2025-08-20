__all__ = [
    "sin_tensor",
    "cos_tensor",
    "sin_plus_cos",
    "sin_times_cos",
    "apply_window",
    "shift_ring",
    "dot_product",
    "log_magnitude",
    "shift_time",
    "phase",
    "normalize_unit_norm",
    "normalize_minmax",
    "normalize_zscore",
]

import torch
from torch import Tensor


def sin_tensor(x: Tensor, freq: float = 1.0) -> Tensor:
    """Applies sine function element-wise."""
    return torch.sin(x * freq)


def cos_tensor(x: Tensor, freq: float = 1.0) -> Tensor:
    """Applies cosine function element-wise."""
    return torch.cos(x * freq)


def sin_plus_cos(x: Tensor, freq: float = 1.0) -> Tensor:
    """Returns sin(x) + cos(x)."""
    return torch.sin(x * freq) + torch.cos(x * freq)


def sin_times_cos(x: Tensor, freq: float = 1.0) -> Tensor:
    """Returns sin(x) * cos(x)."""
    return torch.sin(x * freq) * torch.cos(x * freq)


def apply_window(x: Tensor, window_type: str = "hann") -> Tensor:
    """Applies a window function to a 1D tensor."""
    if window_type == "hann":
        window = torch.hann_window(x.shape[-1], device=x.device)
    elif window_type == "hamming":
        window = torch.hamming_window(x.shape[-1], device=x.device)
    else:
        raise ValueError(f"Unsupported window type: {window_type}")
    return x * window


def shift_ring(x: Tensor, dim: int = -1) -> Tensor:
    """Circularly shifts tensor values: last becomes first (along given dim)."""
    return torch.roll(x, shifts=1, dims=dim)


def shift_time(x: torch.Tensor, shift: int) -> torch.Tensor:
    """Shifts tensor along time axis (last dim)."""
    return torch.roll(x, shifts=shift, dims=-1)


def dot_product(x: Tensor, y: Tensor, dim: int = -1) -> Tensor:
    """Computes dot product along the specified dimension."""
    return torch.sum(x * y, dim=dim)


def log_magnitude(stft_complex: Tensor, eps: float = 1e-5) -> Tensor:
    """Returns log magnitude from complex STFT."""
    magnitude = torch.abs(stft_complex)
    return torch.log(magnitude + eps)


def phase(stft_complex: Tensor) -> Tensor:
    """Returns phase from complex STFT."""
    return torch.angle(stft_complex)


def normalize_unit_norm(x: torch.Tensor, eps: float = 1e-6):
    norm = torch.norm(x, dim=-1, keepdim=True)
    return x / (norm + eps)


def normalize_minmax(x: torch.Tensor, eps: float = 1e-6):
    min_val = x.amin(dim=-1, keepdim=True)
    max_val = x.amax(dim=-1, keepdim=True)
    return (x - min_val) / (max_val - min_val + eps)


def normalize_zscore(x: torch.Tensor, eps: float = 1e-6):
    mean = x.mean(dim=-1, keepdim=True)
    std = x.std(dim=-1, keepdim=True)
    return (x - mean) / (std + eps)
