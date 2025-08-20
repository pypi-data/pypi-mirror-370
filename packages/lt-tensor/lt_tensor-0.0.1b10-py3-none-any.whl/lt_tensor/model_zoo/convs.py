__all__ = ["ConvNets", "ConvEXT"]
from lt_utils.common import *
from torch.nn.utils.parametrize import remove_parametrizations
from torch.nn.utils.parametrizations import weight_norm, spectral_norm
from torch import nn, Tensor
from lt_tensor.model_base import Model
from lt_utils.misc_utils import default


def spectral_norm_select(module: nn.Module, enabled: bool):
    if enabled:
        return spectral_norm(module)
    return module


def get_weight_norm(norm_type: Optional[Literal["weight", "spectral"]] = None):
    if not norm_type:
        return lambda x: x
    if norm_type == "weight":
        return lambda x: weight_norm(x)
    return lambda x: spectral_norm(x)


def remove_norm(module, name: str = "weight"):
    try:
        try:
            remove_parametrizations(module, name, leave_parametrized=False)
        except:
            # many times will fail with 'leave_parametrized'
            remove_parametrizations(module, name)
    except ValueError:
        pass  # not parametrized


class ConvNets(Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def remove_norms(self, name: str = "weight"):
        for module in self.modules():
            try:
                if "Conv" in module.__class__.__name__:
                    remove_norm(module, name)
            except:
                pass

    @staticmethod
    def init_weights(m: nn.Module, mean=0.0, std=0.02):
        if "Conv" in m.__class__.__name__:
            m.weight.data.normal_(mean, std)


class ConvEXT(ConvNets):
    def __init__(
        self,
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: Union[int, Tuple[int, ...]] = 1,
        stride: Union[int, Tuple[int, ...]] = 1,
        padding: Union[int, Tuple[int, ...]] = 0,
        dilation: Union[int, Tuple[int, ...]] = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        device: Optional[Any] = None,
        dtype: Optional[Any] = None,
        apply_norm: Optional[Literal["weight", "spectral"]] = None,
        activation_in: nn.Module = nn.Identity(),
        activation_out: nn.Module = nn.Identity(),
        module_type: Literal["1d", "2d", "3d"] = "1d",
        transpose: bool = False,
        weight_init: Optional[Callable[[nn.Module], None]] = None,
        init_weights: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if not out_channels:
            out_channels = in_channels
        cnn_kwargs = dict(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            groups=groups,
            bias=bias,
            padding_mode=padding_mode,
            device=device,
            dtype=dtype,
        )
        match module_type.lower():
            case "1d":
                md = nn.Conv1d if not transpose else nn.ConvTranspose1d
            case "2d":
                md = nn.Conv2d if not transpose else nn.ConvTranspose2d
            case "3d":
                md = nn.Conv3d if not transpose else nn.ConvTranspose3d
            case _:
                raise ValueError(
                    f"module_type {module_type} is not a valid module type! use '1d', '2d' or '3d'"
                )

        if apply_norm is None:
            self.cnn = md(**cnn_kwargs)
        else:
            if apply_norm == "spectral":
                self.cnn = spectral_norm(md(**cnn_kwargs))
            else:
                self.cnn = weight_norm(md(**cnn_kwargs))
        self.actv_in = activation_in
        self.actv_out = activation_out
        if init_weights:
            weight_init = default(weight_init, self.init_weights)
            self.cnn.apply(weight_init)

    def forward(self, input: Tensor):
        return self.actv_out(self.cnn(self.actv_in(input)))
