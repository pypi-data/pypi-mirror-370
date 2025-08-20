__all__ = [
    "spectral_norm_select",
    "get_weight_norm",
    "ResBlock1D",
    "AdaResBlock1D",
    "ResBlocks1D",
    "ResBlock1D_V2",
    "GatedResBlock",
    "DenseGatedResBlock",
]
from lt_utils.common import *
import torch
from torch.nn.utils.parametrizations import weight_norm
from torch import nn, Tensor
from typing import Union, List
from lt_tensor.model_zoo.fusion import AdaFusion1D
from lt_tensor.model_zoo.convs import ConvNets


def get_padding(ks, d):
    return int((ks * d - d) / 2)


class ResBlock1D(ConvNets):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()

        self.conv_nets = nn.ModuleList(
            [
                self._get_conv_layer(i, channels, kernel_size, 1, dilation, activation)
                for i in range(len(dilation))
            ]
        )
        self.conv_nets.apply(self.init_weights)
        self.last_index = len(self.conv_nets) - 1

    def _get_conv_layer(self, id, ch, k, stride, d, actv):
        return nn.Sequential(
            actv,  # 1
            weight_norm(
                nn.Conv1d(
                    ch, ch, k, stride, dilation=d[id], padding=get_padding(k, d[id])
                )
            ),  # 2
            actv,  # 3
            weight_norm(
                nn.Conv1d(ch, ch, k, stride, dilation=1, padding=get_padding(k, 1))
            ),  # 4
        )

    def forward(self, x: Tensor):
        for cnn in self.conv_nets:
            x = cnn(x) + x
        return x


class AdaResBlock1D(ConvNets):
    def __init__(
        self,
        res_block_channels: int,
        ada_channel_in: int,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()

        self.alpha1 = nn.ModuleList()
        self.alpha2 = nn.ModuleList()
        self.conv_nets = nn.ModuleList(
            [
                self._get_conv_layer(
                    d,
                    res_block_channels,
                    ada_channel_in,
                    kernel_size,
                )
                for d in dilation
            ]
        )
        self.conv_nets.apply(self.init_weights)
        self.last_index = len(self.conv_nets) - 1
        self.activation = activation

    def _get_conv_layer(self, d, ch, ada_ch, k):
        self.alpha1.append(nn.Parameter(torch.ones(1, ada_ch, 1)))
        self.alpha2.append(nn.Parameter(torch.ones(1, ada_ch, 1)))
        return nn.ModuleDict(
            dict(
                norm1=AdaFusion1D(ada_ch, ch),
                norm2=AdaFusion1D(ada_ch, ch),
                conv1=weight_norm(
                    nn.Conv1d(ch, ch, k, 1, dilation=d, padding=get_padding(k, d))
                ),  # 2
                conv2=weight_norm(
                    nn.Conv1d(ch, ch, k, 1, dilation=1, padding=get_padding(k, 1))
                ),  # 4
            )
        )

    def forward(self, x: torch.Tensor, y: torch.Tensor):
        for i, cnn in enumerate(self.conv_nets):
            xt = self.activation(cnn["norm1"](x, y, self.alpha1[i]))
            xt = cnn["conv1"](xt)
            xt = self.activation(cnn["norm2"](xt, y, self.alpha2[i]))
            x = cnn["conv2"](xt) + x
        return x


class ResBlock1D_V2(ConvNets):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()
        self.convs = nn.ModuleList(
            [
                weight_norm(
                    nn.Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        dilation=d,
                        padding=get_padding(kernel_size, d),
                    )
                )
                for d in range(dilation)
            ]
        )
        self.convs.apply(self.init_weights)
        self.activation = activation

    def forward(self, x):
        for c in self.convs:
            xt = c(self.activation(x))
            x = xt + x
        return x


class ResBlocks1D(ConvNets):
    def __init__(
        self,
        channels: int,
        resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11],
        resblock_dilation_sizes: List[Union[int, List[int]]] = [
            [1, 3, 5],
            [1, 3, 5],
            [1, 3, 5],
        ],
        activation: nn.Module = nn.LeakyReLU(0.1),
        block: Union[ResBlock1D, ResBlock1D_V2] = ResBlock1D,
    ):
        super().__init__()
        self.num_kernels = len(resblock_kernel_sizes)
        self.rb = nn.ModuleList()
        self.activation = activation

        for k, j in zip(resblock_kernel_sizes, resblock_dilation_sizes):
            self.rb.append(block(channels, k, j, activation))

        self.rb.apply(self.init_weights)

    def forward(self, x: Tensor):
        xs = torch.zeros_like(x)
        for i, block in enumerate(self.rb):
            xs += block(x)
        return xs / self.num_kernels


class GatedResBlock(ConvNets):
    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilations: Tuple[int, ...] = (1, 3, 9),
        activation: nn.Module = nn.LeakyReLU(0.1),
        residual_scale: float = 0.2,
        init_fn: Callable = ConvNets.init_weights,
    ):
        super().__init__()
        self.residual_scale = residual_scale
        self.activation = activation

        # Store dilation blocks (dilations=[1,3,9])
        self.dilation_blocks = nn.ModuleList()
        for d in dilations:
            self.dilation_blocks.append(
                nn.Sequential(
                    weight_norm(
                        nn.Conv1d(
                            channels,
                            channels * 2,
                            kernel_size,
                            padding=get_padding(kernel_size, d),
                            dilation=d,
                        )
                    ),
                    # Pointwise conv to reduce channel count after GLU
                    weight_norm(nn.Conv1d(channels, channels, 1)),
                )
            )
        self.dilation_blocks.apply(init_fn)

    def forward(self, x):
        residual = x
        for block in self.dilation_blocks:
            h = self.activation(x)
            y = block[0](h)  # [B, C*2, T]
            # Split into two halves (GLU): c and g
            c, g = torch.chunk(y, 2, dim=1)
            gated = c * torch.sigmoid(g)
            # pointwise convolution to reduce channels
            y = block[1](gated)  # [B, C, T]
            x = x + self.residual_scale * y
        return x + residual


class DenseGatedResBlock(ConvNets):
    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilations: Tuple[int, ...] = (1, 3, 9),
        activation: nn.Module = nn.LeakyReLU(0.1),
        residual_scale: float = 0.2,
        proj_after: bool = True,
        init_fn: Callable = ConvNets.init_weights,
    ):
        super().__init__()
        self.residual_scale = residual_scale
        self.activation = activation
        self.blocks = nn.ModuleList()
        self.dilations = list(dilations)
        for d in self.dilations:
            conv = weight_norm(
                nn.Conv1d(
                    channels,
                    channels * 2,
                    kernel_size,
                    padding=get_padding(kernel_size, d),
                    dilation=d,
                )
            )
            pw = weight_norm(nn.Conv1d(channels, channels, 1))
            self.blocks.append(nn.ModuleDict({"conv": conv, "pw": pw}))
        self.blocks.apply(init_fn)
        self.proj_after = proj_after
        if proj_after:
            self.proj = weight_norm(
                nn.Conv1d(channels * (len(self.dilations) + 1), channels, 1)
            )
            self.proj.apply(init_fn)

    def forward(self, x: Tensor):
        outputs = [x]
        cur = x
        for b in self.blocks:
            xt = self.activation(cur)
            xt = b["conv"](xt)
            a, g = xt.chunk(2, dim=1)
            xt = a * torch.sigmoid(g)
            xt = b["pw"](xt)
            cur = cur + self.residual_scale * xt
            outputs.append(cur)
        out = torch.cat(outputs, dim=1)
        if self.proj_after:
            out = self.proj(out)
        return out
