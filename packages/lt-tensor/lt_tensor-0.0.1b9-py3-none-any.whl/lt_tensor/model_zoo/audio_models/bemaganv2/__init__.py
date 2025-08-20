import torch
from torch import nn, Tensor
from lt_utils.common import *
from lt_tensor.model_zoo.convs import ConvNets
from lt_utils.file_ops import is_file, load_json
from lt_tensor.model_base import ModelConfig
from torch.nn.utils.parametrizations import weight_norm
from lt_tensor.model_zoo.audio_models.resblocks import AMPBlock1, AMPBlock2, get_snake


class BemaGANv2Config(ModelConfig):
    # Training params
    in_channels: int = 80
    upsample_rates: List[Union[int, List[int]]] = [8, 8, 2, 2]
    upsample_kernel_sizes: List[Union[int, List[int]]] = [16, 16, 4, 4]
    upsample_initial_channel: int = 512
    resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11]
    resblock_dilation_sizes: List[Union[int, List[int]]] = [
        [1, 3, 5],
        [1, 3, 5],
        [1, 3, 5],
    ]

    activation: Literal["snake", "snakebeta"] = "snakebeta"
    resblock_activation: Literal["snake", "snakebeta"] = "snakebeta"
    resblock: int = 0
    use_bias_at_final: bool = True
    use_tanh_at_final: bool = True
    snake_logscale: bool = True

    def __init__(
        self,
        in_channels: int = 80,
        upsample_rates: List[Union[int, List[int]]] = [8, 8, 2, 2],
        upsample_kernel_sizes: List[Union[int, List[int]]] = [16, 16, 4, 4],
        upsample_initial_channel: int = 1536,
        resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11],
        resblock_dilation_sizes: List[Union[int, List[int]]] = [
            [1, 3, 5],
            [1, 3, 5],
            [1, 3, 5],
        ],
        activation: Literal["snake", "snakebeta"] = "snakebeta",
        resblock_activation: Literal["snake", "snakebeta"] = "snakebeta",
        resblock: Union[int, str] = "1",
        use_bias_at_final: bool = False,
        use_tanh_at_final: bool = False,
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
            "use_bias_at_final": use_bias_at_final,
            "use_tanh_at_final": use_tanh_at_final,
        }
        super().__init__(**settings)

    def post_process(self):
        if isinstance(self.resblock, str):
            self.resblock = 0 if self.resblock == "1" else 1


class BemaGANv2Generator(ConvNets):

    def __init__(
        self, cfg: Union[BemaGANv2Config, Dict[str, object]] = BemaGANv2Config()
    ):
        super().__init__()
        cfg = cfg if isinstance(cfg, BemaGANv2Config) else BemaGANv2Config(**cfg)
        self.cfg = cfg

        actv = get_snake(self.cfg.activation)

        self.num_kernels = len(cfg.resblock_kernel_sizes)
        self.num_upsamples = len(cfg.upsample_rates)

        self.conv_pre = weight_norm(
            nn.Conv1d(cfg.in_channels, cfg.upsample_initial_channel, 7, 1, padding=3)
        )

        # define which AMPBlock to use. BigVGAN uses AMPBlock1 as default
        resblock = AMPBlock1 if cfg.resblock == 0 else AMPBlock2

        # transposed conv-based upsamplers. does not apply anti-aliasing
        self.ups = nn.ModuleList()
        for i, (u, k) in enumerate(zip(cfg.upsample_rates, cfg.upsample_kernel_sizes)):
            self.ups.append(
                nn.ModuleList(
                    [
                        weight_norm(
                            nn.ConvTranspose1d(
                                cfg.upsample_initial_channel // (2**i),
                                cfg.upsample_initial_channel // (2 ** (i + 1)),
                                k,
                                u,
                                padding=(k - u) // 2,
                            )
                        )
                    ]
                )
            )
        # residual blocks using anti-aliased multi-periodicity composition modules (AMP)
        self.resblocks = nn.ModuleList()
        for i in range(len(self.ups)):
            ch = cfg.upsample_initial_channel // (2 ** (i + 1))
            for k, d in zip(cfg.resblock_kernel_sizes, cfg.resblock_dilation_sizes):
                self.resblocks.append(
                    resblock(
                        ch,
                        k,
                        d,
                        snake_logscale=cfg.snake_logscale,
                        activation=cfg.resblock_activation,
                    )
                )

        self.activation_post = actv(ch, alpha_logscale=cfg.snake_logscale)
        # post conv

        self.conv_post = weight_norm(
            nn.Conv1d(ch, 1, 7, 1, padding=3, bias=self.cfg.use_bias_at_final)
        )
        self._use_tanh = self.cfg.use_tanh_at_final

        # weight initialization
        for i in range(len(self.ups)):
            self.ups[i].apply(self.init_weights)
        self.conv_post.apply(self.init_weights)

    def forward(self, x: Tensor):
        # pre conv
        x = self.conv_pre(x)

        for i in range(self.num_upsamples):
            # upsampling
            for i_up in range(len(self.ups[i])):
                x = self.ups[i][i_up](x)
            # AMP blocks
            xs = None
            for j in range(self.num_kernels):
                if xs is None:
                    xs = self.resblocks[i * self.num_kernels + j](x)
                else:
                    xs += self.resblocks[i * self.num_kernels + j](x)
            x = xs / self.num_kernels

        # post conv
        x = self.activation_post(x)
        x = self.conv_post(x)
        if self._use_tanh:
            return x.tanh()
        return x

    @classmethod
    def from_pretrained(
        cls,
        model_file: PathLike,
        model_config: Union[
            BemaGANv2Config, Dict[str, Any], Dict[str, Any], PathLike
        ] = BemaGANv2Config(),
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

        if isinstance(model_config, (BemaGANv2Config, dict)):
            h = model_config
        elif isinstance(model_config, (str, Path, bytes)):
            h = BemaGANv2Config(**load_json(model_config, {}))

        model = cls(h)
        if remove_norms:
            model.remove_norms()
        try:
            model.load_state_dict(model_state_dict, strict=strict, assign=assign)
            return model
        except RuntimeError as e:
            if remove_norms:
                raise e
            print(
                f"[INFO] the pretrained checkpoint does not contain weight norm. Loading the checkpoint after removing weight norm!"
            )
            model.remove_norms()
            model.load_state_dict(model_state_dict, strict=strict, assign=assign)
        return model
