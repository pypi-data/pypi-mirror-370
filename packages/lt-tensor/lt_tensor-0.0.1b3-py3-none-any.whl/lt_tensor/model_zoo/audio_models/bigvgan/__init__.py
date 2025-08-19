from lt_utils.common import *
import torch
from torch.nn.utils.parametrizations import weight_norm
from torch import nn, Tensor
from lt_tensor.model_zoo.convs import ConvNets
from lt_tensor.model_base import ModelConfig
from lt_tensor.model_zoo.activations import alias_free
from lt_tensor.model_zoo.audio_models.resblocks import AMPBlock1, AMPBlock2, get_snake
from lt_utils.file_ops import load_json, is_file


class BigVGANConfig(ModelConfig):
    # Training params
    in_channels: int = 80
    upsample_rates: List[Union[int, List[int]]] = [4, 4, 2, 2, 2, 2]
    upsample_kernel_sizes: List[Union[int, List[int]]] = [8, 8, 4, 4, 4, 4]
    upsample_initial_channel: int = 1536
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
        upsample_rates: List[Union[int, List[int]]] = [4, 4, 2, 2, 2, 2],
        upsample_kernel_sizes: List[Union[int, List[int]]] = [8, 8, 4, 4, 4, 4],
        upsample_initial_channel: int = 1536,
        resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11],
        resblock_dilation_sizes: List[Union[int, List[int]]] = [
            [1, 3, 5],
            [1, 3, 5],
            [1, 3, 5],
        ],
        activation: Literal["snake", "snakebeta"] = "snakebeta",
        resblock_activation: Literal["snake", "snakebeta"] = "snakebeta",
        resblock: Union[int, str] = 0,
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


class BigVGAN(ConvNets):
    """Modified from 'https://github.com/NVIDIA/BigVGAN/blob/main/bigvgan.py' under mit license.

    BigVGAN is a neural vocoder model that applies anti-aliased periodic activation for residual blocks (resblocks).
    New in BigVGAN-v2: it can optionally use optimized CUDA kernels for AMP (anti-aliased multi-periodicity) blocks.

    Args:
        cfg (BigVGANConfig): Hyperparameters.

    """

    def __init__(self, cfg: Union[BigVGANConfig, Dict[str, object]] = BigVGANConfig()):
        super().__init__()
        cfg = cfg if isinstance(cfg, BigVGANConfig) else BigVGANConfig(**cfg)
        self.cfg = cfg
        actv = get_snake(self.cfg.activation)

        # Select which Activation1d, lazy-load cuda version to ensure backward compatibility

        self.num_kernels = len(cfg.resblock_kernel_sizes)
        self.num_upsamples = len(cfg.upsample_rates)

        # Pre-conv
        self.conv_pre = weight_norm(
            nn.Conv1d(cfg.in_channels, cfg.upsample_initial_channel, 7, 1, padding=3)
        )

        # Define which AMPBlock to use. BigVGAN uses AMPBlock1 as default
        resblock_class = AMPBlock1 if cfg.resblock == 0 else AMPBlock2

        # Transposed conv-based upsamplers. does not apply anti-aliasing
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

        # Residual blocks using anti-aliased multi-periodicity composition modules (AMP)
        self.resblocks = nn.ModuleList()
        for i in range(len(self.ups)):
            ch = cfg.upsample_initial_channel // (2 ** (i + 1))
            for k, d in zip(cfg.resblock_kernel_sizes, cfg.resblock_dilation_sizes):
                self.resblocks.append(
                    resblock_class(
                        ch,
                        k,
                        d,
                        snake_logscale=cfg.snake_logscale,
                        activation=cfg.resblock_activation,
                    )
                )

        # Post-conv
        activation_post = actv(ch, alpha_logscale=cfg.snake_logscale)

        self.activation_post = alias_free.Activation1d(activation=activation_post)

        # Whether to use bias for the final conv_post. Default to True for backward compatibility
        self.conv_post = weight_norm(
            nn.Conv1d(ch, 1, 7, 1, padding=3, bias=self.cfg.use_bias_at_final)
        )

        # Weight initialization
        for i in range(len(self.ups)):
            self.ups[i].apply(self.init_weights)
        self.conv_post.apply(self.init_weights)

        # Final tanh activation. Defaults to True for backward compatibility
        self.use_tanh_at_final = cfg.use_tanh_at_final

    def forward(self, x):
        # Pre-conv
        x = self.conv_pre(x)

        for i in range(self.num_upsamples):
            # Upsampling
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

        # Post-conv
        x = self.activation_post(x)
        x: Tensor = self.conv_post(x)
        # Final tanh activation
        if self.use_tanh_at_final:
            return x.tanh()
        return x.clamp(min=-1.0, max=1.0)

    @classmethod
    def from_pretrained(
        cls,
        model_file: PathLike,
        model_config: Union[
            BigVGANConfig, Dict[str, Any], Dict[str, Any], PathLike
        ] = BigVGANConfig(),
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
            model_file, weights_only=weights_only, map_location=map_location, mmap=mmap
        )

        if isinstance(model_config, (BigVGANConfig, dict)):
            h = model_config

        elif isinstance(model_config, (str, Path, bytes)):
            h = BigVGANConfig(**load_json(model_config, {}))

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
