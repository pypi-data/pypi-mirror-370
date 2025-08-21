__all__ = [
    "log_tensor",
    "set_seed",
    "count_parameters",
    "freeze_all_except",
    "freeze_selected_weights",
    "unfreeze_all_except",
    "unfreeze_selected_weights",
    "clip_gradients",
    "detach_hidden",
    "one_hot",
    "safe_divide",
    "batch_pad",
    "sample_tensor",
    "TorchCacheUtils",
    "clear_cache",
    "default_device",
    "soft_restore",
    "Packing",
    "Padding",
    "Masking",
    "get_losses",
    "plot_view",
    "get_activated_conv",
    "update_lr",
    "is_tensor",
    "to_tensor",
    "to_numpy",
    "ROOT_DEVICE",
    "time_weighted_ema",
    "is_fused_available",
    "TrainTracker",
    "has_same_dim",
    "has_same_shape",
]

import gc
import sys
import copy
import torch
import random
import inspect
import warnings
import numpy as np
from lt_utils.common import *
from torch import nn, optim, Tensor
from lt_utils.type_utils import is_str
from lt_utils.misc_utils import cache_wrapper
import torch.nn.functional as F
from typing import TypeGuard
from lt_utils.misc_utils import get_current_time
from lt_utils.file_ops import load_json, save_json

CONV_MAP = {
    "conv1d": nn.Conv1d,
    "conv2d": nn.Conv2d,
    "conv3d": nn.Conv3d,
    "convtranspose1d": nn.ConvTranspose1d,
    "convtranspose2d": nn.ConvTranspose2d,
    "convtranspose3d": nn.ConvTranspose3d,
}


ROOT_DEVICE = torch.device(
    "cpu"
    if torch.cpu.is_available()
    else (
        "cuda"
        if torch.cuda.is_available()
        else "mps" if torch.mps.is_available() else torch.zeros(1).device
    )
)


def has_same_dim(tensor1: Tensor, tensor2: Tensor):
    return tensor1.ndim == tensor2.ndim


def has_same_shape(tensor1: Tensor, tensor2: Tensor, dim: Optional[int] = None):
    return tensor1.size(dim) == tensor2.size(dim)


def is_fused_available():

    return "fused" in inspect.signature(optim.AdamW).parameters


def time_weighted_ema(data, alpha):
    """
    Compute the time-weighted Exponential Moving Average (EMA) for a given data array.

    Parameters:
    - data: array-like, the input data to smooth.
    - alpha: float, the smoothing factor (0 < alpha ≤ 1). Higher alpha discounts older observations faster.

    Returns:
    - ema: numpy array, the smoothed data.
    """
    import numpy as np

    if isinstance(data, Tensor):
        data = data.detach().clone().to(ROOT_DEVICE).numpy()
    elif isinstance(data, (list, tuple)):
        data = np.array([float(x) for x in data])
    ema = np.zeros_like(data)
    alpha = min(max(float(alpha), 0.00001), 0.99999)
    ema[0] = data[0]  # Initialize with the first data point
    for t in range(1, len(data)):
        ema[t] = alpha * data[t] + alpha * ema[t - 1]
    return ema


def get_activated_conv(
    in_channels: int,
    out_channels: int,
    kernel_size: int = 1,
    stride: int = 1,
    padding: Union[int, str] = 0,
    groups: int = 1,
    conv_type: Literal[
        "Conv1d",
        "Conv2d",
        "Conv3d",
        "ConvTranspose1d",
        "ConvTranspose2d",
        "ConvTranspose3d",
    ] = "Conv1d",
    activation: nn.Module = nn.LeakyReLU(0.2),
    norm_fn: Callable[[nn.Module], nn.Module] = lambda x: x,
):
    assert conv_type.lower() in CONV_MAP, f"Invalid conv type: {conv_type}."
    return nn.Sequential(
        activation,
        norm_fn(
            nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, groups)
        ),
    )


def is_tensor(item: Any) -> TypeGuard[Tensor]:
    return isinstance(item, Tensor)


def to_tensor(inp: Union[Tensor, np.ndarray, List[Number], Number]):
    if is_tensor(inp):
        return inp.detach().clone()
    elif isinstance(inp, (int, float)):
        if isinstance(inp, int):
            return torch.tensor(inp, dtype=torch.long)
        return torch.tensor(inp)
    elif isinstance(inp, (list, tuple)):
        return torch.tensor([float(x) for x in inp if isinstance(x, (int, float))])
    elif isinstance(inp, np.ndarray):
        return torch.from_numpy(inp)
    raise ValueError(f"'{inp}' cannot be converted to tensor! (type: {type(inp)})")


def to_numpy(inp: Union[Tensor, np.ndarray, List[Number], Number]):
    if isinstance(inp, np.ndarray):
        return inp.copy()
    elif isinstance(inp, Tensor):
        return inp.detach().clone().to(device=ROOT_DEVICE).numpy(force=True)
    elif isinstance(inp, (list, tuple)):
        return np.array([float(x) for x in inp if isinstance(x, (int, float))])
    elif isinstance(inp, (int, float)):
        return np.array([float(inp)])
    raise ValueError(f"'{inp}' cannot be converted to numpy array! (type: {type(inp)})")


def get_loss_average(losses: List[float]):
    """A little helper for training, for example:
    ```python
    losses = []
    for epoch in range(100):
        for inp, label in dataloader:
            optimizer.zero_grad()
            out = model(inp)
            loss = loss_fn(out, label)
            optimizer.step()
            losses.append(loss.item())
        print(f"Epoch {epoch+1} | Loss: {get_loss_average(losses):.4f}")
    """
    if not losses:
        return float("nan")
    return sum(losses) / len(losses)


def update_lr(optimizer: optim.Optimizer, new_value: Union[float, Tensor] = 1e-4):
    if isinstance(new_value, (int, float)):
        new_value = float(new_value)

    elif isinstance(new_value, Tensor):
        if new_value.ndim in [0, 1]:
            try:
                new_value = float(new_value.item())
            except:
                pass

    new_value_float = isinstance(new_value, float)
    for param_group in optimizer.param_groups:
        if isinstance(param_group["lr"], Tensor) and new_value_float:
            param_group["lr"].fill_(new_value)
        else:
            param_group["lr"] = new_value
    return optimizer


def plot_view(
    data: Dict[str, List[Any]],
    title: str = "Loss",
    xaxis_title="Step/Epoch",
    yaxis_title="Loss",
    template="plotly_dark",
    smoothing: bool = False,
    smoothing_alpha: float = 0.6673,
):
    try:
        import plotly.graph_objs as go
    except ModuleNotFoundError:
        warnings.warn(
            "No installation of plotly was found. To use it use 'pip install plotly' and restart this application!"
        )
        return
    fig = go.Figure()
    for mode, values in data.items():
        if values:
            items = (
                values if not smoothing else time_weighted_ema(values, smoothing_alpha)
            )
            fig.add_trace(go.Scatter(y=items, name=mode.capitalize()))
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        template=template,
    )
    return fig


def updateDict(self, dct: dict[str, Any]):
    for k, v in dct.items():
        setattr(self, k, v)


def soft_restore(tensor, epsilon=1e-6):
    return torch.where(tensor == 0, torch.full_like(tensor, epsilon), tensor)


def try_torch(fn: str, *args, **kwargs):
    tried_torch = False
    not_present_message = (
        f"Both `torch` and `torch.nn.functional` does not contain the module `{fn}`"
    )
    try:
        if hasattr(F, fn):
            return getattr(F, fn)(*args, **kwargs)
        elif hasattr(torch, fn):
            tried_torch = True
            return getattr(torch, fn)(*args, **kwargs)
        return not_present_message
    except Exception as a:
        try:
            if not tried_torch and hasattr(torch, fn):
                return getattr(torch, fn)(*args, **kwargs)
            return str(a)
        except Exception as e:
            return str(e) + " | " + str(a)


def log_tensor(
    item: Union[Tensor, np.ndarray],
    title: Optional[str] = None,
    print_details: bool = True,
    print_tensor: bool = False,
    dim: Optional[int] = None,
):
    assert isinstance(item, (Tensor, np.ndarray))
    has_title = is_str(title)

    if has_title:
        print("========[" + title.title() + "]========")
        _b = 20 + len(title.strip())
    print(f"shape: {item.shape}")
    print(f"dtype: {item.dtype}")
    if print_details:
        print(f"ndim: {item.ndim}")
        if isinstance(item, Tensor):
            print(f"device: {item.device}")
            print(f"min: {item.min():.4f}")
            print(f"max: {item.max():.4f}")
            try:
                print(f"std: {item.std(dim=dim):.4f}")
            except:
                pass
            try:

                print(f"mean: {item.mean(dim=dim):.4f}")
            except:
                pass
    if print_tensor:
        print(item)
    if has_title:
        print("".join(["-"] * _b), "\n")
    else:
        print("\n")
    sys.stdout.flush()


def get_losses(base: Tensor, target: Tensor, return_valid_only: bool = False):
    losses = {}
    losses["mse_loss"] = try_torch("mse_loss", base, target)
    losses["l1_loss"] = try_torch("l1_loss", base, target)
    losses["huber_loss"] = try_torch("huber_loss", base, target)
    losses["poisson_nll_loss"] = try_torch("poisson_nll_loss", base, target)
    losses["smooth_l1_loss"] = try_torch("smooth_l1_loss", base, target)
    losses["cross_entropy"] = try_torch("cross_entropy", base, target)
    losses["soft_margin_loss"] = try_torch("soft_margin_loss", base, target)
    losses["nll_loss"] = try_torch("nll_loss", base, target)
    losses["gaussian_nll_loss"] = try_torch("gaussian_nll_loss", base, target, var=1.0)
    losses["gaussian_nll_loss-var_0.25"] = try_torch(
        "gaussian_nll_loss", base, target, var=0.25
    )
    losses["gaussian_nll_loss-var_4.0"] = try_torch(
        "gaussian_nll_loss", base, target, var=4.0
    )
    if not return_valid_only:
        return losses
    valid = {}
    for name, loss in losses.items():
        if isinstance(loss, str):
            continue
        valid[name] = loss
    return valid


def set_seed(seed: int):
    """Set random seed for reproducibility."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if torch.mps.is_available():
        torch.mps.manual_seed(seed)
    if torch.xpu.is_available():
        torch.xpu.manual_seed_all(seed)


def count_parameters(model: nn.Module) -> int:
    """Returns total number of trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def freeze_all_except(model: nn.Module, except_layers: Optional[list[str]] = None):
    """Freezes all model parameters except specified layers."""
    no_exceptions = not except_layers
    for name, param in model.named_parameters():
        if no_exceptions:
            param.requires_grad_(False)
        elif any(layer in name for layer in except_layers):
            param.requires_grad_(False)


def freeze_selected_weights(model: nn.Module, target_layers: list[str]):
    """Freezes only parameters on specified layers."""
    for name, param in model.named_parameters():
        if any(layer in name for layer in target_layers):
            param.requires_grad_(False)


def unfreeze_all_except(model: nn.Module, except_layers: Optional[list[str]] = None):
    """Unfreezes all model parameters except specified layers."""
    no_exceptions = not except_layers
    for name, param in model.named_parameters():
        if no_exceptions:
            param.requires_grad_(True)
        elif not any(layer in name for layer in except_layers):
            param.requires_grad_(True)


def unfreeze_selected_weights(model: nn.Module, target_layers: list[str]):
    """Unfreezes only parameters on specified layers."""
    for name, param in model.named_parameters():
        if not any(layer in name for layer in target_layers):
            param.requires_grad_(True)


def clip_gradients(model: nn.Module, max_norm: float = 1.0):
    """Applies gradient clipping."""
    return nn.utils.clip_grad_norm_(model.parameters(), max_norm)


def detach_hidden(hidden):
    """Detaches hidden states (for RNNs)."""
    if isinstance(hidden, torch.Tensor):
        return hidden.detach()
    else:
        return tuple(detach_hidden(h) for h in hidden)


def one_hot(labels: torch.Tensor, num_classes: int) -> torch.Tensor:
    """One-hot encodes a tensor of labels."""
    return F.one_hot(labels, num_classes).float()


def safe_divide(a: torch.Tensor, b: torch.Tensor, eps: float = 1e-8):
    """Safe division for tensors (prevents divide-by-zero)."""
    return a / (b + eps)


def batch_pad(tensors: list[torch.Tensor], padding_value: float = 0.0) -> torch.Tensor:
    """Pads a list of tensors to the same shape (assumes 2D+ tensors)."""
    max_shape = [
        max(s[i] for s in [t.shape for t in tensors]) for i in range(tensors[0].dim())
    ]
    padded = []
    for t in tensors:
        pad_dims = [(0, m - s) for s, m in zip(t.shape, max_shape)]
        pad_flat = [p for pair in reversed(pad_dims) for p in pair]  # reverse for F.pad
        padded.append(F.pad(t, pad_flat, value=padding_value))
    return torch.stack(padded)


def sample_tensor(tensor: torch.Tensor, num_samples: int = 5):
    """Randomly samples values from tensor for preview."""
    flat = tensor.flatten()
    idx = torch.randperm(len(flat))[:num_samples]
    return flat[idx]


def clear_cache():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    if torch.mps.is_available():
        torch.mps.empty_cache()
    if torch.xpu.is_available():
        torch.xpu.empty_cache()
    gc.collect()


@cache_wrapper
def default_device(idx: Optional[int] = None):
    try:
        if torch.cuda.is_available():
            return torch.device("cuda", idx)
        if torch.xpu.is_available():
            return torch.device("xpu", idx)
        if torch.mps.is_available():
            return torch.device("mps", idx)
        if hasattr(torch, "is_vulkan_available"):
            if getattr(torch, "is_vulkan_available")():
                return torch.device("vulkan", idx)
    except:
        pass
    finally:
        return torch.device(torch.zeros(1).device)


class Packing:
    """
    example:

    ```
    x_lengths = torch.tensor([5, 3, 6])
    x_padded = torch.randn(3, 6, 256)  # padded input [B, T, C]

    # 1. RNN expects packed input
    x_packed = Padding.pack_sequence(x_padded, x_lengths)
    output_packed, _ = rnn(x_packed)

    # 2. Recover padded for loss
    output = Padding.unpack_sequence(output_packed, total_length=x_padded.size(1))

    # 3. Mask for loss
    mask = torch.arange(x_padded.size(1))[None, :] < x_lengths[:, None]
    loss = (F.mse_loss(output, target, reduction="none") * mask.unsqueeze(-1)).sum() / mask.sum()
    ```
    """

    @staticmethod
    def pack_sequence(x: Tensor, lengths: Tensor):
        """
        Pack padded sequence for RNN/LSTM.
        Args:
            x (Tensor): Padded input [B, T, C]
            lengths (Tensor): Actual lengths [B]
        Returns:
            PackedSequence

        """
        return nn.utils.rnn.pack_padded_sequence(
            x,
            lengths.cpu().numpy(),
            batch_first=True,
            enforce_sorted=False,
        )

    @staticmethod
    def unpack_sequence(packed, total_length: int) -> Tensor:
        """Unpacks RNN PackedSequence to padded [B, T, C]."""
        output, _ = nn.utils.rnn.pad_packed_sequence(
            packed,
            batch_first=True,
            total_length=total_length,
        )
        return output


class Padding:

    @staticmethod
    def pad_to(x: Tensor, target_length: int, pad_value: float = 0.0) -> Tensor:
        """
        Pad input tensor along time axis (dim=1) to target length.
        Args:
            x (Tensor): Input tensor [B, T, C]
            target_length (int): Target time length
            pad_value (float): Fill value
        Returns:
            Padded tensor [B, target_length, C]
        """
        B, T, C = x.size()
        if T >= target_length:
            return x
        pad = x.new_full((B, target_length - T, C), pad_value)
        return torch.cat([x, pad], dim=1)

    @staticmethod
    def pad_sequence(
        inputs: Tensor,
        size: int,
        direction: Literal["left", "right"] = "left",
        pad_id: Union[int, float] = 0,
    ) -> Tensor:
        """
        Pads a single tensor to the specified size in 1D.
        Args:
            inputs (Tensor): Tensor of shape [T] or [B, T]
            size (int): Desired size along the last dimension
            direction (str): 'left' or 'right'
            pad_id (int): Value to pad with
        Returns:
            Padded tensor
        """
        total = size - inputs.shape[-1]
        if total < 1:
            return inputs
        pad_config = (total, 0) if direction == "left" else (0, total)
        return F.pad(inputs, pad_config, value=pad_id)

    @staticmethod
    def pad_batch_1d(
        batch: List[Tensor],
        pad_value: float = 0.0,
        pad_to_multiple: Optional[int] = None,
        direction: Literal["left", "right"] = "right",
    ) -> Tuple[Tensor, Tensor]:
        """
        Pad list of 1D tensors to same length with optional multiple alignment.
        Returns:
            Padded tensor [B, T], Lengths [B]
        """
        lengths = torch.tensor([t.size(0) for t in batch])
        max_len = lengths.max().item()

        if pad_to_multiple:
            max_len = (
                (max_len + pad_to_multiple - 1) // pad_to_multiple
            ) * pad_to_multiple

        padded = []
        for t in batch:
            padded.append(Padding.pad_sequence(t, max_len, direction, pad_value))
        return torch.stack(padded), lengths

    @staticmethod
    def pad_batch_2d(
        batch: List[Tensor],
        pad_value: float = 0.0,
        pad_to_multiple: Optional[int] = None,
        direction: Literal["left", "right"] = "right",
    ) -> Tuple[Tensor, Tensor]:
        """
        Pad list of 2D tensors (e.g. [T, D]) to same T.
        Returns:
            Padded tensor [B, T, D], Lengths [B]
        """
        lengths = torch.tensor([t.size(0) for t in batch])
        feat_dim = batch[0].size(1)
        max_len = lengths.max().item()

        if pad_to_multiple:
            max_len = (
                (max_len + pad_to_multiple - 1) // pad_to_multiple
            ) * pad_to_multiple

        padded = []
        for t in batch:
            pad_len = max_len - t.size(0)
            if direction == "left":
                pad_tensor = t.new_full((pad_len, feat_dim), pad_value)
                padded.append(torch.cat([pad_tensor, t], dim=0))
            else:
                pad_tensor = t.new_full((pad_len, feat_dim), pad_value)
                padded.append(torch.cat([t, pad_tensor], dim=0))
        return torch.stack(padded), lengths

    # --- Batching ---

    @staticmethod
    def pad_batch_1d(
        batch: List[Tensor],
        pad_value: float = 0.0,
        pad_to_multiple: Optional[int] = None,
        direction: Literal["left", "right"] = "right",
    ) -> Tuple[Tensor, Tensor]:
        """Pads list of 1D tensors → [B, T]"""
        lengths = torch.tensor([t.size(0) for t in batch])
        max_len = lengths.max().item()
        if pad_to_multiple:
            max_len = (
                (max_len + pad_to_multiple - 1) // pad_to_multiple
            ) * pad_to_multiple

        padded = [Padding.pad_sequence(t, max_len, direction, pad_value) for t in batch]
        return torch.stack(padded), lengths

    @staticmethod
    def pad_batch_2d(
        batch: List[Tensor],
        pad_value: float = 0.0,
        pad_to_multiple: Optional[int] = None,
        direction: Literal["left", "right"] = "right",
    ) -> Tuple[Tensor, Tensor]:
        """Pads list of 2D tensors [T, D] → [B, T, D]"""
        lengths = torch.tensor([t.size(0) for t in batch])
        feat_dim = batch[0].size(1)
        max_len = lengths.max().item()
        if pad_to_multiple:
            max_len = (
                (max_len + pad_to_multiple - 1) // pad_to_multiple
            ) * pad_to_multiple

        padded = []
        for t in batch:
            pad_len = max_len - t.size(0)
            pad_tensor = t.new_full((pad_len, feat_dim), pad_value)
            padded_tensor = (
                torch.cat([pad_tensor, t], dim=0)
                if direction == "left"
                else torch.cat([t, pad_tensor], dim=0)
            )
            padded.append(padded_tensor)
        return torch.stack(padded), lengths

    @staticmethod
    def pad_batch_nd(
        batch: List[Tensor],
        pad_value: float = 0.0,
        dim: int = 0,
        pad_to_multiple: Optional[int] = None,
    ) -> Tuple[Tensor, Tensor]:
        """
        General N-D padding along time axis (dim=0, usually).
        Handles shapes like:
            [T, C] → [B, T, C]
            [T, H, W] → [B, T, H, W]
        """
        lengths = torch.tensor([t.size(dim) for t in batch])
        max_len = lengths.max().item()
        if pad_to_multiple:
            max_len = (
                (max_len + pad_to_multiple - 1) // pad_to_multiple
            ) * pad_to_multiple

        padded = []
        for t in batch:
            pad_len = max_len - t.size(dim)
            pad_shape = list(t.shape)
            pad_shape[dim] = pad_len
            pad_tensor = t.new_full(pad_shape, pad_value)
            padded_tensor = torch.cat([t, pad_tensor], dim=dim)
            padded.append(padded_tensor)

        return torch.stack(padded), lengths


class Masking:

    @staticmethod
    def apply_mask(x: Tensor, mask: Tensor, fill_value: Number = 0) -> Tensor:
        """
        Apply a mask to a tensor, setting masked positions to `fill_value`.
        Args:
            x (Tensor): Input tensor of shape [..., T, D].
            mask (Tensor): Mask of shape [..., T] where True = masked.
            fill_value (Number): Value to fill masked positions with.
        Returns:
            Tensor: Masked tensor.
        """
        return x.masked_fill(mask.unsqueeze(-1), fill_value)

    @staticmethod
    def get_padding_mask(
        lengths: Optional[Tensor] = None,
        tokens: Optional[Tensor] = None,
        padding_id: int = 0,
    ) -> Tensor:
        """
        Generate a padding mask: 1 for real tokens, 0 for padding.
        Args:
            lengths (Tensor): Tensor of shape [B] with sequence lengths.
            tokens (Tensor): Tensor of shape [B, T] with token ids.
            padding_id (int): Padding token id (default=0).
        Returns:
            Tensor: Boolean mask of shape [B, T].
        """
        assert (
            tokens is not None or lengths is not None
        ), "Either tokens or lengths must be provided."

        if tokens is not None:
            return tokens != padding_id

        B = lengths.size(0)
        max_len = lengths.max().item()
        arange = torch.arange(max_len, device=lengths.device).unsqueeze(0).expand(B, -1)
        return arange < lengths.unsqueeze(1)

    @staticmethod
    def get_padding_mask_fps(lengths: Tensor) -> Tensor:
        """
        Legacy-style padding mask using 1-based comparison.
        """
        mask = (
            torch.arange(lengths.max(), device=lengths.device)
            .unsqueeze(0)
            .expand(lengths.shape[0], -1)
        )
        return (mask + 1) > lengths.unsqueeze(1)

    @staticmethod
    def get_causal_mask(
        size: Union[int, tuple[int, ...]],
        device: Optional[Union[str, torch.device]] = None,
    ) -> Tensor:
        """
        Generate a causal mask for self-attention.
        Args:
            size (int or tuple): Size (T) or (1, T, T)
        Returns:
            Tensor: [1, T, T] boolean causal mask
        """
        if isinstance(size, int):
            size = (1, size, size)
        return torch.tril(torch.ones(size, dtype=torch.bool, device=device))

    @staticmethod
    def combine_masks(pad_mask: Tensor, causal_mask: Tensor) -> Tensor:
        """
        Combine padding and causal masks.
        Args:
            pad_mask (Tensor): [B, T] padding mask
            causal_mask (Tensor): [1, T, T] causal mask
        Returns:
            Tensor: [B, T, T] combined mask
        """
        return (
            causal_mask & pad_mask.unsqueeze(1).expand(-1, pad_mask.size(1), -1).bool()
        )


class TrainTracker:
    last_file = f"logs/history_{get_current_time()}.json"
    loss_history: Dict[str, List[Number]] = {}
    lr_history: Dict[str, List[Number]] = {}

    def __init__(self, max_len: int = 100_000, max_len_percent_removal: float = 0.1):
        self.set_max_history(max_len, max_len_percent_removal)

    def set_max_history(
        self, max_len: int = 100_000, max_len_percent_removal: float = 0.1
    ):
        self.max_len = max(int(max_len), 10)
        self.percentage_removal = min(max(float(max_len_percent_removal), 0.1), 0.95)
        self.removal_length = max(int(self.max_len * self.percentage_removal), 4)

    def add_lr(
        self,
        lr: Union[float, Tensor],
        key: str = "main",
    ):
        if key not in self.lr_history:
            self.lr_history[key] = []

        if isinstance(lr, Tensor):
            lr = lr.item()

        self.lr_history[key].append(lr)
        if len(self.lr_history[key]) > self.max_len:
            nc = copy.deepcopy(self.lr_history[key][self.removal_length :])
            self.lr_history[key].clear()
            self.lr_history[key] = nc.copy()

    def add_loss(
        self,
        loss: Union[float, Tensor],
        key: str = "main",
    ):
        if key not in self.loss_history:
            self.loss_history[key] = []
        if isinstance(loss, Tensor):
            loss = loss.item()
        self.loss_history[key].append(float(loss))
        if len(self.loss_history[key]) > self.max_len:
            nc = copy.deepcopy(self.loss_history[key][self.removal_length :])
            self.loss_history[key].clear()
            self.loss_history[key] = nc.copy()

    @staticmethod
    def _sum_and_avg(values: List[Number]):
        if not values:
            return float("nan")
        return sum(values) / len(values)

    def get_lr_average(self, key: str = "main", total: int = 0):
        lr = self.get_learning_rates(key, total)
        return self._sum_and_avg(lr)

    def get_loss_average(self, key: str = "main", total: int = 0):
        losses = self.get_losses(key, total)
        return self._sum_and_avg(losses)

    def get_learning_rates(self, key: str = "train", total: int = 0):
        total = max(int(total), 0)
        results = self.lr_history.get(key, [])
        if total:
            return results[-total:]
        return results

    def get_losses(self, key: str = "main", total: int = 0):
        total = max(int(total), 0)
        results = self.loss_history.get(key, [])
        if total:
            return results[-total:]
        return results

    def save(self, path: Optional[PathLike] = None):
        if path is None:
            path = f"logs/history_{get_current_time()}.json"
        save_json(path, self.loss_history, indent=2)
        self.last_file = str(path)

    def load(self, path: Optional[PathLike] = None):
        if path is None:
            path = self.last_file
        self.loss_history = load_json(path, {})
        self.last_file = str(path)

    def plot_loss(
        self,
        keys: Union[str, List[str]] = ["main"],
        max_amount: int = 0,
        smoothing: bool = False,
        smoothing_alpha: float = 0.5,
        title: str = "Loss(es)",
    ):
        if isinstance(keys, str):
            keys = [keys]
        max_amount = min(self.max_len, max(int(max_amount), 0))
        if not max_amount:
            max_amount = self.max_len
        return plot_view(
            {k: v[-max_amount:] for k, v in self.loss_history.items() if k in keys},
            title,
            smoothing=smoothing,
            smoothing_alpha=smoothing_alpha,
        )

    def plot_lr(
        self,
        keys: Union[str, List[str]] = ["main"],
        max_amount: int = 0,
        smoothing: bool = False,
        smoothing_alpha: float = 0.5,
        title: str = "Learning Rate(s)",
    ):
        if isinstance(keys, str):
            keys = [keys]
        max_amount = min(self.max_len, max(int(max_amount), 0))
        if not max_amount:
            max_amount = self.max_len
        return plot_view(
            {k: v[-max_amount:] for k, v in self.lr_history.items() if k in keys},
            title,
            smoothing=smoothing,
            smoothing_alpha=smoothing_alpha,
        )
