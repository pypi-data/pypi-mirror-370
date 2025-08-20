__all__ = ["iSTFTNetGenerator", "iSTFTNetConfig"]
from lt_utils.common import *
import torch
from torch import nn, Tensor
from torch.nn.utils.parametrizations import weight_norm
from lt_tensor.model_zoo.convs import ConvNets
from lt_tensor.model_base import ModelConfig
from lt_utils.file_ops import is_file, load_json
from lt_tensor.model_zoo.audio_models.resblocks import ResBlock1, ResBlock2


class iSTFTNetConfig(ModelConfig):
    # Training params
    in_channels: int = 80
    upsample_rates: List[Union[int, List[int]]] = [8, 8]
    upsample_kernel_sizes: List[Union[int, List[int]]] = [16, 16]
    upsample_initial_channel: int = 512
    resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11]
    resblock_dilation_sizes: List[Union[int, List[int]]] = [
        [1, 3, 5],
        [1, 3, 5],
        [1, 3, 5],
    ]

    activation: Union[nn.Module, str] = "leakyrelu"
    resblock_activation: Union[nn.Module, str] = "leakyrelu"
    resblock: int = 0
    activation_kwargs: Dict[str, Any] = dict()
    resblock_activation_kwargs: Dict[str, Any] = dict()
    gen_istft_n_fft: int = 16
    sampling_rate: Number = 24000

    _activation: nn.Module = None
    _resblock_activation: nn.Module = None

    def __init__(
        self,
        in_channels: int = 80,
        upsample_rates: List[Union[int, List[int]]] = [8, 8],
        upsample_kernel_sizes: List[Union[int, List[int]]] = [16, 16],
        upsample_initial_channel: int = 512,
        resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11],
        resblock_dilation_sizes: List[Union[int, List[int]]] = [
            [1, 3, 5],
            [1, 3, 5],
            [1, 3, 5],
        ],
        activation: str = "leakyrelu",
        resblock_activation: str = "leakyrelu",
        activation_kwargs: Dict[str, Any] = dict(negative_slope=0.1),
        resblock_activation_kwargs: Dict[str, Any] = dict(negative_slope=0.1),
        resblock: Union[int, str] = 0,
        gen_istft_n_fft: int = 16,
        sampling_rate: Number = 24000,
        *args,
        **kwargs,
    ):
        settings = {
            "in_channels": in_channels,
            "upsample_rates": upsample_rates,
            "upsample_kernel_sizes": upsample_kernel_sizes,
            "upsample_initial_channel": upsample_initial_channel,
            "resblock_kernel_sizes": resblock_kernel_sizes,
            "resblock_dilation_sizes": resblock_dilation_sizes,
            "activation": activation,
            "resblock_activation": resblock_activation,
            "resblock": resblock,
            "gen_istft_n_fft": gen_istft_n_fft,
            "sampling_rate": sampling_rate,
            "resblock_activation_kwargs": resblock_activation_kwargs,
            "activation_kwargs": activation_kwargs,
        }
        super().__init__(**settings)
        self._forbidden_list.append("_activation")
        self._forbidden_list.append("_resblock_activation")
        

    def post_process(self):
        assert (isinstance(self.resblock, int) and self.resblock in [0, 1]) or (
            isinstance(self.resblock, str) and self.resblock in ["0", "1", "2"]
        )
        if isinstance(self.resblock, str):
            self.resblock = 0 if self.resblock in ["0", "1"] else 1

        self._activation = (
            self.get_activation(activation=self.activation)
            if isinstance(self.activation, str)
            else self.activation
        )
        self._resblock_activation = (
            self.get_activation(
                activation=self.resblock_activation, **self.resblock_activation_kwargs
            )
            if isinstance(self.resblock_activation, str)
            else self.resblock_activation
        )


class iSTFTNetGenerator(ConvNets):
    def __init__(
        self, cfg: Union[iSTFTNetConfig, Dict[str, object]] = iSTFTNetConfig()
    ):
        super().__init__()
        cfg = cfg if isinstance(cfg, iSTFTNetConfig) else iSTFTNetConfig(**cfg)
        self.cfg = cfg
        self.num_kernels = len(cfg.resblock_kernel_sizes)
        self.num_upsamples = len(cfg.upsample_rates)
        self.conv_pre = weight_norm(
            nn.Conv1d(cfg.in_channels, cfg.upsample_initial_channel, 7, 1, padding=3)
        )

        resblock = ResBlock1 if cfg.resblock == 0 else ResBlock2

        self.ups = nn.ModuleList()
        for i, (u, k) in enumerate(zip(cfg.upsample_rates, cfg.upsample_kernel_sizes)):
            if cfg.sampling_rate % 16000:
                self.ups.append(
                    weight_norm(
                        nn.ConvTranspose1d(
                            cfg.upsample_initial_channel // (2**i),
                            cfg.upsample_initial_channel // (2 ** (i + 1)),
                            k,
                            u,
                            padding=(k - u) // 2,
                        )
                    )
                )
            else:
                self.ups.append(
                    weight_norm(
                        nn.ConvTranspose1d(
                            cfg.upsample_initial_channel // (2**i),
                            cfg.upsample_initial_channel // (2 ** (i + 1)),
                            k,
                            u,
                            padding=(u // 2 + u % 2),
                            output_padding=u % 2,
                        )
                    )
                )

        self.resblocks = nn.ModuleList()
        for i in range(len(self.ups)):
            ch = cfg.upsample_initial_channel // (2 ** (i + 1))
            for j, (k, d) in enumerate(
                zip(cfg.resblock_kernel_sizes, cfg.resblock_dilation_sizes)
            ):
                self.resblocks.append(resblock(ch, k, d, cfg._resblock_activation))

        self.post_n_fft = cfg.gen_istft_n_fft
        self.conv_post = weight_norm(
            nn.Conv1d(ch, self.post_n_fft + 2, 7, 1, padding=3)
        )
        self.ups.apply(self.init_weights)
        self.conv_post.apply(self.init_weights)
        self.activation = cfg._activation
        self.reflection_pad = nn.ReflectionPad1d((1, 0))

    def forward(self, x: Tensor):
        x = self.conv_pre(x)
        for i in range(self.num_upsamples):
            x = self.activation(x)
            x = self.ups[i](x)
            xs = None
            for j in range(self.num_kernels):
                if xs is None:
                    xs = self.resblocks[i * self.num_kernels + j](x)
                else:
                    xs += self.resblocks[i * self.num_kernels + j](x)
            x = xs / self.num_kernels
        x = self.activation(x)
        x = self.reflection_pad(x)
        x = self.conv_post(x)
        spec = x[:, : self.post_n_fft // 2 + 1, :].exp()
        phase = x[:, self.post_n_fft // 2 + 1 :, :].sin()
        return spec, phase

    @classmethod
    def from_pretrained(
        cls,
        model_file: PathLike,
        model_config: Union[
            iSTFTNetConfig, Dict[str, Any], Dict[str, Any], PathLike
        ] = iSTFTNetConfig(),
        *,
        remove_norms: bool = False,
        strict: bool = False,
        map_location: Union[str, torch.device] = torch.device("cpu"),
        weights_only: bool = False,
        mmap: Optional[bool] = None,
        assign: bool = False,
        **kwargs,
    ):
        is_file(model_file, validate=True)
        if isinstance(map_location, str):
            map_location = torch.device(map_location)
        model_state_dict = torch.load(
            model_file,
            weights_only=weights_only,
            map_location=map_location,
            mmap=mmap,
        )

        if isinstance(model_config, (iSTFTNetConfig, dict)):
            h = model_config
        elif isinstance(model_config, (str, Path, bytes)):
            h = iSTFTNetConfig(**load_json(model_config, {}))
        model = cls(h)
        if remove_norms:
            model.remove_norms()
        try:
            model.load_state_dict(model_state_dict, strict=strict, assign=assign)
            return model
        except RuntimeError:
            print(
                f"[INFO] the pretrained checkpoint does not contain weight norm. Loading the checkpoint after removing weight norm!"
            )
            model.remove_norms()
            model.load_state_dict(model_state_dict, strict=strict, assign=assign)
        return model
