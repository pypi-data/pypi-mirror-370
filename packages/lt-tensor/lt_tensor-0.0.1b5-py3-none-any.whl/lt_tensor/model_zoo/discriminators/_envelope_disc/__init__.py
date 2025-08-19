"""Modified from: https://github.com/dinhoitt/BemaGANv2/blob/9560ae9df153c956f259c261c57c4f84f89e3d72/envelope.py
MIT License

Copyright (c) 2025 Taseoo Park

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import torch
from torch import Tensor
from lt_utils.common import *
from lt_tensor.model_base import Model


class Envelope(Model):
    def __init__(self, max_freq: int, sample_rate: Number = 24000, cut_off: int = 0):
        super().__init__()
        self.sr = sample_rate
        self.max_freq = max_freq
        self.setup_low_pass_fn(max_freq, cut_off)

    def forward(self, x: torch.Tensor):
        if not self.max_freq:
            return x
        return self.lp_fn(x)

    def _ft_signal(self, signal: torch.Tensor):
        filtered_signal = self.butterwort_lowpass_filter(signal)
        return torch.abs(self.hilbert(filtered_signal))

    def setup_low_pass_fn(self, max_freq: int, cutoff: int = 0):
        self.max_freq = int(max_freq)
        cutoff = self.max_freq if cutoff == 0 else cutoff
        self.lp_fn = self.hilbert if self.max_freq in [-1, 1] else self._ft_signal
        self.setup_butterwort_lowpass_coefficients(cutoff)

    def hilbert(self, signal: Tensor) -> Tensor:
        """Implementing the Hilbert transform manually"""
        N = signal.shape[2]  # Signal length
        FFT_signal = torch.fft.fft(signal, axis=2)
        h = torch.zeros_like(
            signal
        )  # Generate an array with the same shape as the signal

        if N % 2 == 0:
            h[:, 0, 0] = 1
            h[:, 0, N // 2] = 1
            h[:, 0, 1 : N // 2] = 2
        else:
            h[:, 0, 0] = 1
            h[:, 0, 1 : (N + 1) // 2] = 2

        out: Tensor = torch.fft.ifft(FFT_signal * h, axis=2)
        if self.max_freq == -1:
            return -out.abs()
        return -out.abs()

    def butterwort_lowpass_filter(self, signal):
        filtered_signal = torch.zeros_like(signal)
        # Applying the filter to the signal
        for n in range(len(signal)):
            if n < 2:
                filtered_signal[n] = self.lp_coef_a[0] * signal[n]
            else:
                filtered_signal[n] = (
                    self.lp_coef_b[0] * signal[n]
                    + self.lp_coef_b[1] * signal[n - 1]
                    + self.lp_coef_b[2] * signal[n - 2]
                    - self.lp_coef_a[1] * filtered_signal[n - 1]
                    - self.lp_coef_a[2] * filtered_signal[n - 2]
                )

        return filtered_signal

    def setup_butterwort_lowpass_coefficients(self, cutoff: int):
        cutoff = torch.tensor([cutoff], dtype=torch.float64)
        fs = torch.tensor([self.sr], dtype=torch.float64)

        omega = torch.tan(torch.pi * cutoff / fs)
        # Convert float 2 to tensor
        sqrt2 = torch.tensor(2.0, dtype=torch.float64).sqrt()

        sq_omega = sqrt2 * omega + omega**2
        # Transfer function coefficients using the bilinear transform
        a = 2 * (omega**2 - 1) / (1 + sq_omega)
        self.register_buffer(
            "lp_coef_a",
            torch.tensor(
                [1.0, a.item(), ((1 - sq_omega) / (1 + sq_omega)).item()],
                dtype=torch.float64,
                device=self.device,
            ),
        )
        b = omega**2 / (1 + sq_omega)
        self.register_buffer(
            "lp_coef_b",
            torch.tensor(
                [b.item(), (2 * b).item(), b.item()],
                dtype=torch.float64,
                device=self.device,
            ),
        )
