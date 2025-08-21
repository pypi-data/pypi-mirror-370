__all__ = ["ConvBase", "ConvPack"]
from lt_utils.common import *
from torch.nn.utils.parametrize import remove_parametrizations
from torch.nn.utils.parametrizations import weight_norm, spectral_norm
from torch import nn, Tensor
from lt_tensor.model_base import Model
from lt_utils.misc_utils import log_traceback

TP_SHAPE_1: TypeAlias = Union[int, Tuple[int]]
TP_SHAPE_2: TypeAlias = Union[TP_SHAPE_1, Tuple[int, int]]
TP_SHAPE_3: TypeAlias = Union[TP_SHAPE_2, Tuple[int, int, int]]


def spectral_norm_select(module: nn.Module, enabled: bool):
    if enabled:
        return spectral_norm(module)
    return module


def _dummy(module: Model, *args, **kwargs):
    return module


def get_weight_norm(
    norm_type: Optional[Literal["weight_norm", "spectral_norm"]] = None, **norm_kwargs
) -> Callable[[Union[nn.Module, Model]], Union[nn.Module, Model]]:
    if not norm_type:
        return _dummy
    if norm_type == "weight_norm":
        return lambda x: weight_norm(x, **norm_kwargs)
    return lambda x: spectral_norm(x, **norm_kwargs)


def remove_norm(module, name: str = "weight"):
    try:
        try:
            remove_parametrizations(module, name, leave_parametrized=False)
        except:
            # many times will fail with 'leave_parametrized'
            remove_parametrizations(module, name, leave_parametrized=True)
    except ValueError:
        pass  # not parametrized


class ConvBase(Model):

    @staticmethod
    def _get_1d(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: int = 1,
        stride: int = 1,
        padding: int = 0,
        output_padding: int = 0,
        dilation: int = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
    ):
        kwargs = dict(
            in_channels=in_channels,
            out_channels=out_channels if out_channels is not None else in_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
        )
        norm_fn = get_weight_norm(norm, **norm_kwargs)
        if transposed:
            return norm_fn(nn.ConvTranspose1d(**kwargs, output_padding=output_padding))
        return norm_fn(nn.Conv1d(**kwargs))

    @staticmethod
    def _get_2d(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: TP_SHAPE_2 = 1,
        stride: TP_SHAPE_2 = 1,
        padding: TP_SHAPE_2 = 0,
        output_padding: TP_SHAPE_2 = 0,
        dilation: TP_SHAPE_2 = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
    ):
        kwargs = dict(
            in_channels=in_channels,
            out_channels=out_channels if out_channels is not None else in_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
        )
        norm_fn = get_weight_norm(norm, **norm_kwargs)
        if transposed:
            return norm_fn(nn.ConvTranspose2d(**kwargs, output_padding=output_padding))
        return norm_fn(nn.Conv2d(**kwargs))

    @staticmethod
    def _get_3d(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: TP_SHAPE_3 = 1,
        stride: TP_SHAPE_3 = 1,
        padding: TP_SHAPE_3 = 0,
        output_padding: TP_SHAPE_3 = 0,
        dilation: TP_SHAPE_3 = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
    ):
        kwargs = dict(
            in_channels=in_channels,
            out_channels=out_channels if out_channels is not None else in_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
        )
        norm_fn = get_weight_norm(norm, **norm_kwargs)
        if transposed:
            return norm_fn(nn.ConvTranspose3d(**kwargs, output_padding=output_padding))
        return norm_fn(nn.Conv3d(**kwargs))

    def remove_norms(self, name: str = "weight"):
        for module in self.modules():
            try:
                if "Conv" in module.__class__.__name__:
                    remove_norm(module, name)
            except:
                pass

    @staticmethod
    def init_weights_a(m: nn.Module, mean=0.0, std=0.02):
        if "Conv" in m.__class__.__name__:
            m.weight.data.normal_(mean, std)

    def init_weights_b(
        self,
        negative_slope: float = 0.1,
        mean: float = 0.0,
        std: Optional[float] = 0.2,
        mode: Literal["fan_in", "fan_out"] = "fan_in",
    ):
        """
        mode: Literal['fan_in', 'fan_out']:
                    Choosing 'fan_in' preserves the magnitude of the variance of the weights in the forward pass.
                    Choosing 'fan_out' preserves the magnitudes in the backwards pass.
        """
        for param in self.parameters():
            if param.data.ndim < 2:  # biasses
                nn.init.normal_(param, mean=mean, std=std)
            else:
                nn.init.kaiming_normal_(param, a=negative_slope, mode=mode)


class ConvPack(ConvBase):
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
        transposed: bool = False,
        weight_init: Union[Callable[[nn.Module], None], Literal["a", "b"]] = "b",
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
                md = nn.Conv1d if not transposed else nn.ConvTranspose1d
            case "2d":
                md = nn.Conv2d if not transposed else nn.ConvTranspose2d
            case "3d":
                md = nn.Conv3d if not transposed else nn.ConvTranspose3d
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
            if callable(weight_init):
                try:
                    self.cnn.apply(weight_init)
                except Exception as e1:
                    try:
                        weight_init()
                    except Exception as e2:
                        log_traceback(
                            e1,
                            "While trying to execute the callable assigned to initialize the module",
                        )
                        log_traceback(e2, "While executing the function directly")
            else:
                if weight_init == "a":
                    self.cnn.apply(self.init_weights_a)
                else:
                    self.init_weights_b()

    def forward(self, input: Tensor):
        return self.actv_out(self.cnn(self.actv_in(input)))
