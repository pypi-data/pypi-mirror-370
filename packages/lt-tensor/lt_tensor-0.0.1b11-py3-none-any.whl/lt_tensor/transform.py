__all__ = [
    "to_mel_spectrogram",
    "stft",
    "istft",
    "fft",
    "ifft",
    "to_log_mel_spectrogram",
    "normalize",
    "min_max_scale",
    "mel_to_linear",
    "stretch_tensor",
    "pad_tensor",
    "get_sinusoidal_embedding",
    "pad_center",
    "normalize",
    "window_sumsquare",
    "inverse_transform",
    "InverseTransformConfig",
    "InverseTransform",
    "stft_istft_rebuild",
]

import torch
from torch import nn, Tensor
import torchaudio
import math
from lt_utils.common import *
import torch.nn.functional as F
from lt_tensor.model_base import Model

DeviceType: TypeAlias = Union[torch.device, str]


def to_mel_spectrogram(
    waveform: torch.Tensor,
    sample_rate: int = 24000,
    n_fft: int = 1024,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    n_mels: int = 80,
    f_min: float = 0.0,
    f_max: Optional[float] = None,
) -> torch.Tensor:
    """Converts waveform to mel spectrogram."""
    return (
        torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            win_length=win_length,
            n_mels=n_mels,
            f_min=f_min,
            f_max=f_max,
        )
        .to(device=waveform.device)
        .forward(waveform)
    )


def stft(
    waveform: Tensor,
    n_fft: int = 512,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    window_fn: str = "hann",
    center: bool = True,
    return_complex: bool = True,
) -> Tensor:
    """Performs short-time Fourier transform using PyTorch."""
    window = (
        torch.hann_window(win_length or n_fft).to(waveform.device)
        if window_fn == "hann"
        else None
    )
    return torch.stft(
        input=waveform,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        window=window,
        center=center,
        return_complex=return_complex,
    )


def istft(
    stft_matrix: Tensor,
    n_fft: int = 512,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    window_fn: str = "hann",
    center: bool = True,
    length: Optional[int] = None,
) -> Tensor:
    """Performs inverse short-time Fourier transform using PyTorch."""
    window = (
        torch.hann_window(win_length or n_fft).to(stft_matrix.device)
        if window_fn == "hann"
        else None
    )
    return torch.istft(
        input=stft_matrix,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        window=window,
        center=center,
        length=length,
    )


def fft(x: Tensor, norm: Optional[str] = "backward") -> Tensor:
    """Returns the FFT of a real tensor."""
    return torch.fft.fft(x, norm=norm)


def ifft(x: Tensor, norm: Optional[str] = "backward") -> Tensor:
    """Returns the inverse FFT of a complex tensor."""
    return torch.fft.ifft(x, norm=norm)


def to_log_mel_spectrogram(
    waveform: torch.Tensor, sample_rate: int = 22050, eps: float = 1e-9, **kwargs
) -> torch.Tensor:
    """Converts waveform to log-mel spectrogram."""
    mel = to_mel_spectrogram(waveform, sample_rate, **kwargs)
    return torch.log(mel + eps)


def normalize(
    x: torch.Tensor,
    mean: Optional[float] = None,
    std: Optional[float] = None,
    eps: float = 1e-9,
) -> torch.Tensor:
    """Normalizes tensor by mean and std."""
    if mean is None:
        mean = x.mean()
    if std is None:
        std = x.std()
    return (x - mean) / (std + eps)


def min_max_scale(
    x: torch.Tensor, min_val: float = 0.0, max_val: float = 1.0
) -> torch.Tensor:
    """Scales tensor to [min_val, max_val] range."""
    x_min, x_max = x.min(), x.max()
    return (x - x_min) / (x_max - x_min + 1e-8) * (max_val - min_val) + min_val


def mel_to_linear(
    mel_spec: torch.Tensor, mel_fb: torch.Tensor, eps: float = 1e-8
) -> torch.Tensor:
    """Approximate inversion of mel to linear spectrogram using pseudo-inverse."""
    mel_fb_inv = torch.pinverse(mel_fb)
    return torch.matmul(mel_fb_inv, mel_spec + eps)


def stretch_tensor(x: torch.Tensor, rate: float, mode: str = "linear") -> torch.Tensor:
    """Time-stretch tensor using interpolation."""
    B, C, T = x.shape if x.ndim == 3 else (1, 1, x.shape[0])
    new_T = int(T * rate)
    x_reshaped = x.view(B * C, T).unsqueeze(1)
    stretched = torch.nn.functional.interpolate(x_reshaped, size=new_T, mode=mode)
    return (
        stretched.squeeze(1).view(B, C, new_T) if x.ndim == 3 else stretched.squeeze()
    )


def pad_tensor(
    x: torch.Tensor, target_len: int, pad_value: float = 0.0
) -> torch.Tensor:
    """Pads tensor to target length along last dimension."""
    current_len = x.shape[-1]
    if current_len >= target_len:
        return x[..., :target_len]
    padding = [0] * (2 * (x.ndim - 1)) + [0, target_len - current_len]
    return F.pad(x, padding, value=pad_value)


def get_sinusoidal_embedding(timesteps: torch.Tensor, dim: int) -> torch.Tensor:
    # Expect shape [B] or [B, 1]
    if timesteps.dim() > 1:
        timesteps = timesteps.view(-1)  # flatten to [B]

    device = timesteps.device
    half_dim = dim // 2
    emb = torch.exp(
        torch.arange(half_dim, device=device) * -(math.log(10000.0) / half_dim)
    )
    emb = timesteps[:, None].float() * emb[None, :]  # [B, half_dim]
    emb = torch.cat((emb.sin(), emb.cos()), dim=-1)  # [B, dim]
    return emb


def generate_window(
    M: int, alpha: float = 0.5, device: Optional[DeviceType] = None
) -> Tensor:
    if M < 1:
        raise ValueError("Window length M must be >= 1.")
    if M == 1:
        return torch.ones(1, device=device)

    n = torch.arange(M, dtype=torch.float32, device=device)
    return alpha - (1.0 - alpha) * torch.cos(2.0 * math.pi * n / (M - 1))


def pad_center(tensor: torch.Tensor, size: int, axis: int = -1) -> torch.Tensor:
    n = tensor.shape[axis]
    if size < n:
        raise ValueError(f"Target size ({size}) must be at least input size ({n})")

    lpad = (size - n) // 2
    rpad = size - n - lpad

    pad = [0] * (2 * tensor.ndim)
    pad[2 * axis + 1] = rpad
    pad[2 * axis] = lpad

    return F.pad(tensor, pad, mode="constant", value=0)


def normalize(
    S: torch.Tensor,
    norm: float = float("inf"),
    axis: int = 0,
    threshold: float = 1e-10,
    fill: bool = False,
) -> torch.Tensor:
    mag = S.abs().float()

    if norm is None:
        return S

    elif norm == float("inf"):
        length = mag.max(dim=axis, keepdim=True).values

    elif norm == float("-inf"):
        length = mag.min(dim=axis, keepdim=True).values

    elif norm == 0:
        length = (mag > 0).sum(dim=axis, keepdim=True).float()

    elif norm > 0:
        length = (mag**norm).sum(dim=axis, keepdim=True) ** (1.0 / norm)

    else:
        raise ValueError(f"Unsupported norm: {norm}")

    small_idx = length < threshold
    length = length.clone()
    if fill:
        length[small_idx] = float("nan")
        Snorm = S / length
        Snorm[Snorm != Snorm] = 1.0  # replace nan with fill_norm (default 1.0)
    else:
        length[small_idx] = float("inf")
        Snorm = S / length

    return Snorm


def window_sumsquare(
    window_spec: Union[str, int, float, Callable, List[Any], Tuple[Any, ...]],
    n_frames: int,
    hop_length: int = 256,
    win_length: int = 1024,
    n_fft: int = 2048,
    dtype: torch.dtype = torch.float32,
    norm: Optional[Union[int, float]] = None,
    device: Optional[torch.device] = None,
):
    if win_length is None:
        win_length = n_fft

    total_length = n_fft + hop_length * (n_frames - 1)
    x = torch.zeros(total_length, dtype=dtype, device=device)

    # Get the window (from scipy for now)
    win = generate_window(window_spec, win_length, fftbins=True)
    win = torch.tensor(win, dtype=dtype, device=device)

    # Normalize and square
    win_sq = normalize(win, norm=norm, axis=0) ** 2
    win_sq = pad_center(win_sq, size=n_fft, axis=0)

    # Accumulate squared windows
    for i in range(n_frames):
        sample = i * hop_length
        end = min(total_length, sample + n_fft)
        length = end - sample
        x[sample:end] += win_sq[:length]

    return x


def inverse_transform(
    spec: Tensor,
    phase: Tensor,
    n_fft: int = 1024,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    length: Optional[Any] = None,
    window: Optional[Tensor] = None,
):
    if window is None:
        window = torch.hann_window(win_length or n_fft).to(spec.device)
    return torch.istft(
        spec * torch.exp(phase * 1j),
        n_fft,
        hop_length,
        win_length,
        window=window,
        length=length,
    )


class InverseTransformConfig:
    def __init__(
        self,
        n_fft: int = 1024,
        win_length: Optional[int] = None,
        hop_length: Optional[int] = None,
        length: Optional[int] = None,
        window: Optional[Tensor] = None,
        onesided: Optional[bool] = None,
        return_complex: bool = False,
        normalized: bool = False,
        center: bool = True,
    ):
        self.n_fft = n_fft
        self.win_length = win_length
        self.hop_length = hop_length
        self.length = length
        self.onesided = onesided
        self.return_complex = return_complex
        self.normalized = normalized
        self.center = center
        self.window = window

    def to_dict(self):
        return self.__dict__.copy()


class InverseTransform(Model):
    def __init__(
        self,
        n_fft: int = 1024,
        win_length: Optional[int] = None,
        hop_length: Optional[int] = None,
        length: Optional[int] = None,
        window: Optional[Tensor] = None,
        onesided: Optional[bool] = None,
        return_complex: bool = False,
        normalized: bool = False,
        center: bool = True,
    ):
        """
        Module for inverting a magnitude + phase spectrogram to a waveform using ISTFT.

        This class encapsulates common ISTFT parameters at initialization and applies
        the inverse transformation in the `forward()` method with minimal per-call overhead.

        Parameters
        ----------
        n_fft : int, optional
            Size of FFT to use during inversion. Default is 1024.
        win_length : int, optional
            Size of the window function. Defaults to `n_fft // 4`.
        hop_length : int, optional
            Number of audio samples between STFT columns. Defaults to `n_fft`.
        length : int, optional
            Output waveform length. If not provided, length will be inferred.
        window : Tensor, optional
            Custom window tensor. If None, a Hann window is used.
        onesided : bool, optional
            Whether the input STFT was onesided. Required only for consistency checks.
        return_complex : bool, default=False
            Must be False if `onesided` is True. Not used internally.
        normalized : bool, default=False
            Whether the STFT was normalized.
        center : bool, default=True
            Whether the signal was padded during STFT.

        Methods
        -------
        forward(spec, phase)
            Applies ISTFT using stored settings on the given magnitude and phase tensors.
        update_settings(...)
            Updates ISTFT parameters dynamically (used internally during forward).
        """
        super().__init__()
        assert window is None or isinstance(window, (Tensor, nn.Module))
        assert not bool(return_complex and onesided)
        self.n_fft = n_fft
        self.length = length
        self.win_length = win_length or n_fft // 4
        self.hop_length = hop_length or n_fft
        self.center = center
        self.return_complex = return_complex
        self.onesided = onesided
        self.normalized = normalized
        self.register_buffer(
            "window", torch.hann_window(self.win_length) if window is None else window
        )

    def forward(self, spec: Tensor, phase: Tensor, *, _recall: bool = False):
        """
        Perform the inverse short-time Fourier transform.

        Parameters
        ----------
        spec : Tensor
            Magnitude spectrogram of shape (batch, freq, time).
        phase : Tensor
            Phase angles tensor, same shape as `spec`, in radians.

        Returns
        -------
        Tensor
            Time-domain waveform reconstructed from `spec` and `phase`.
        """
        try:
            return torch.istft(
                spec * torch.exp(phase * 1j),
                n_fft=self.n_fft,
                hop_length=self.hop_length,
                win_length=self.win_length,
                window=self.window,
                center=self.center,
                normalized=self.normalized,
                onesided=self.onesided,
                length=self.length,
                return_complex=self.return_complex,
            )
        except RuntimeError as e:
            if not _recall and spec.device != self.window.device:
                self.window = self.window.to(spec.device)
                return self.forward(spec, phase, _recall=True)
            raise e
