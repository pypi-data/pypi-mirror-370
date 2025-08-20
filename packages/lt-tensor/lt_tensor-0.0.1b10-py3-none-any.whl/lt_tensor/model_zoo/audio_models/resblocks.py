from lt_utils.common import *
from torch import nn, Tensor
from torch.nn import functional as F
from lt_tensor.model_zoo.convs import ConvNets
from torch.nn.utils.parametrizations import weight_norm


def get_padding(kernel_size, dilation=1):
    return int((kernel_size * dilation - dilation) / 2)


class ResBlockBase(ConvNets):
    st: int = 0

    def init_weights(
        self,
        negative_slope: float = 0.1,
        mean: float = 0.0,
        std: Optional[float] = None,
        mode: Literal["fan_in", "fan_out"] = "fan_out",
    ):
        """
        mode: Literal['fan_in', 'fan_out']: Choosing 'fan_in' preserves the magnitude of the variance of the weights in the forward pass.
                                            Choosing 'fan_out' preserves the magnitudes in the backwards pass.
        """
        if std is None:
            base = max(self.st, 2)
            std = (1.0 / (base**2)) * (base - 1)
        for param in self.parameters():
            if param.data.ndim < 2:  # biasses
                nn.init.normal_(param, mean=mean, std=std)
            else:
                nn.init.kaiming_normal_(param, a=negative_slope, mode=mode)


class ResBlock1(ResBlockBase):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: nn.Module = nn.LeakyReLU(0.1),
        *args,
        **kwargs,
    ):
        super().__init__()

        self.convs1 = nn.ModuleList(
            [
                weight_norm(
                    nn.Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=d,
                        padding=get_padding(kernel_size, d),
                    )
                )
                for d in dilation
            ]
        )

        self.convs2 = nn.ModuleList(
            [
                weight_norm(
                    nn.Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=1,
                        padding=get_padding(kernel_size, 1),
                    )
                )
                for _ in dilation
            ]
        )

        negative_slope = (
            activation.negative_slope if isinstance(activation, nn.LeakyReLU) else 0.1
        )
        self.st = int(len(dilation) * 2)
        self.init_weights(negative_slope=negative_slope)
        # self.convs1.apply(self.init_weights)
        # self.convs2.apply(lambda m: self.init_weights())
        self.activation = activation

    def forward(self, x: Tensor):
        for c1, c2 in zip(self.convs1, self.convs2):
            xt = c1(self.activation(x))
            x = c2(self.activation(xt)) + x
        return x


class ResBlock2(ResBlockBase):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3),
        activation: nn.Module = nn.LeakyReLU(0.1),
        *args,
        **kwargs,
    ):
        super().__init__()
        self.convs = nn.ModuleList(
            [
                weight_norm(
                    nn.Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=d,
                        padding=get_padding(kernel_size, d),
                    )
                )
                for d in dilation
            ]
        )
        self.st = int(len(dilation) * 2)
        # self.convs.apply(self.init_weights)
        negative_slope = (
            activation.negative_slope if isinstance(activation, nn.LeakyReLU) else 0.1
        )
        self.init_weights(negative_slope=negative_slope)
        self.activation = activation

    def forward(self, x):
        for c in self.convs:
            xt = c(self.activation(x))
            x = xt + x
        return x


def get_snake(name: Literal["snake", "snakebeta"] = "snake"):
    assert name.lower() in [
        "snake",
        "snakebeta",
    ], f"'{name}' is not a valid snake activation! use 'snake' or 'snakebeta'"
    from lt_tensor.model_zoo.activations import snake

    if name.lower() == "snake":
        return snake.Snake
    return snake.SnakeBeta


class AMPBlock1(ResBlockBase):
    """Modified from 'https://github.com/NVIDIA/BigVGAN/blob/main/bigvgan.py' under MIT license, found in 'bigvgan/LICENSE'
    AMPBlock applies Snake / SnakeBeta activation functions with trainable parameters that control periodicity, defined for each layer.
    AMPBlock1 has additional self.convs2 that contains additional Conv1d layers with a fixed dilation=1 followed by each layer in self.convs1

    Args:
        channels (int): Number of convolution channels.
        kernel_size (int): Size of the convolution kernel. Default is 3.
        dilation (tuple): Dilation rates for the convolutions. Each dilation layer has two convolutions. Default is (1, 3, 5).
        snake_logscale: (bool): to use logscale with snake activation. Default to True.
        activation (str): Activation function type. Should be either 'snake' or 'snakebeta'. Defaults to 'snakebeta'.
    """

    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilation: tuple = (1, 3, 5),
        snake_logscale: bool = True,
        activation: Literal["snake", "snakebeta"] = "snakebeta",
        *args,
        **kwargs,
    ):
        super().__init__()
        from lt_tensor.model_zoo.activations import alias_free

        actv = get_snake(activation)

        self.convs1 = nn.ModuleList(
            [
                weight_norm(
                    nn.Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        stride=1,
                        dilation=d,
                        padding=get_padding(kernel_size, d),
                    )
                )
                for d in dilation
            ]
        )
        # self.convs1.apply(self.init_weights)

        self.convs2 = nn.ModuleList(
            [
                weight_norm(
                    nn.Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        stride=1,
                        dilation=1,
                        padding=get_padding(kernel_size, 1),
                    )
                )
                for _ in range(len(dilation))
            ]
        )
        # self.convs2.apply(self.init_weights)

        self.num_layers = len(self.convs1) + len(
            self.convs2
        )  # Total number of conv layers

        # Activation functions
        self.activations = nn.ModuleList(
            [
                alias_free.Activation1d(
                    activation=actv(channels, alpha_logscale=snake_logscale)
                )
                for _ in range(self.num_layers)
            ]
        )
        self.init_weights()
        

    def forward(self, x):
        acts1, acts2 = self.activations[::2], self.activations[1::2]
        for c1, c2, a1, a2 in zip(self.convs1, self.convs2, acts1, acts2):
            xt = a1(x)
            xt = c1(xt)
            xt = a2(xt)
            xt = c2(xt)
            x = xt + x
        return x


class AMPBlock2(ResBlockBase):
    """Modified from 'https://github.com/NVIDIA/BigVGAN/blob/main/bigvgan.py' under MIT license, found in 'bigvgan/LICENSE'
    AMPBlock applies Snake / SnakeBeta activation functions with trainable parameters that control periodicity, defined for each layer.
    Unlike AMPBlock1, AMPBlock2 does not contain extra Conv1d layers with fixed dilation=1

    Args:
        channels (int): Number of convolution channels.
        kernel_size (int): Size of the convolution kernel. Default is 3.
        dilation (tuple): Dilation rates for the convolutions. Each dilation layer has two convolutions. Default is (1, 3, 5).
        snake_logscale: (bool): to use logscale with snake activation. Default to True.
        activation (str): Activation function type. Should be either 'snake' or 'snakebeta'. Defaults to 'snakebeta'.
    """

    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilation: tuple = (1, 3, 5),
        snake_logscale: bool = True,
        activation: Literal["snake", "snakebeta"] = "snakebeta",
        *args,
        **kwargs,
    ):
        super().__init__()
        from lt_tensor.model_zoo.activations import alias_free

        actv = get_snake(activation)
        self.convs = nn.ModuleList(
            [
                weight_norm(
                    nn.Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        stride=1,
                        dilation=d,
                        padding=get_padding(kernel_size, d),
                    )
                )
                for d in dilation
            ]
        )
        # self.convs.apply(self.init_weights)

        self.num_layers = len(self.convs)  # Total number of conv layers

        # Activation functions
        self.activations = nn.ModuleList(
            [
                alias_free.Activation1d(
                    activation=actv(channels, alpha_logscale=snake_logscale)
                )
                for _ in range(self.num_layers)
            ]
        )
        self.init_weights()

    def forward(self, x):
        for c, a in zip(self.convs, self.activations):
            xt = a(x)
            xt = c(xt)
            x = xt + x
        return x


class ResAttn(nn.Module):
    """Its almost un-usable due to the memory consumption"""

    def __init__(self, channels, heads=2, downsample=16):
        super().__init__()
        self.norm = nn.LayerNorm(channels)
        self.qkv = nn.Conv1d(channels, channels * 3, kernel_size=1)
        self.out_proj = nn.Conv1d(channels, channels, kernel_size=1)
        self.downsample = downsample
        self.heads = heads

    def forward(self, x):
        b, c, t = x.shape

        # Downsample time axis to reduce memory
        x_ds = F.avg_pool1d(x, kernel_size=self.downsample, stride=self.downsample)
        td = x_ds.shape[-1]

        qkv = self.qkv(x_ds)  # (B, 3C, T')
        q, k, v = qkv.chunk(3, dim=1)

        # Convert to (B, T', H, C//H) -> (B*H, T', C//H)
        def reshape_heads(t):
            return (
                t.view(b, self.heads, c // self.heads, td)
                .transpose(1, 2)
                .reshape(b * self.heads, td, c // self.heads)
            )

        q = reshape_heads(q)
        k = reshape_heads(k)
        v = reshape_heads(v)

        attn_out = F.scaled_dot_product_attention(q, k, v)

        # Back to (B, C, T')
        attn_out = attn_out.view(b, c, td)
        attn_out = self.out_proj(attn_out)
        attn_out = F.interpolate(attn_out, size=t, mode="linear")
        return x + attn_out
