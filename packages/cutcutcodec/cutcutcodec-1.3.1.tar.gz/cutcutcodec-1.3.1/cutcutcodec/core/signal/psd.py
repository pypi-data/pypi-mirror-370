#!/usr/bin/env python3

"""Tools for the Power Spectral Density (PSD) estimation."""

import numbers
import typing
import math

import torch

from .window import alpha_to_band, att_to_alpha, band_to_alpha, dpss


def _compute_psd(
    signal: torch.Tensor, win: torch.Tensor, shift: int, return_std: bool
) -> torch.Tensor:
    """Help welch."""
    assert signal.ndim >= 1, signal.shape
    assert signal.shape[-1] >= len(win), "signal to short or window to tall"
    assert win.ndim == 1, win.shape
    signal = signal.contiguous()
    psd = signal.as_strided(  # shape (..., o, m)
        (
            *signal.shape[:-1],
            (signal.shape[-1] - len(win)) // shift + 1,  # number of slices
            len(win),
        ),
        (*signal.stride()[:-1], shift, 1),
    )
    psd = psd * win  # not inplace because blocs was not contiguous
    psd = torch.fft.rfft(psd, norm="ortho", dim=-1)  # norm ortho for perceval theorem
    psd = psd.real**2 + psd.imag**2
    inv_win_mass = len(win) / torch.sum(win)
    if return_std:
        std, psd = torch.std_mean(psd, dim=-2)  # shape (..., m)
        std *= inv_win_mass
        psd *= inv_win_mass
        return std, psd
    psd = torch.mean(psd, dim=-2)  # shape (..., m)
    psd *= inv_win_mass
    return psd


def _find_len(s_x: float, sigma_max: float, psd_max: float, freq_res: float) -> float:
    s_w_min, s_w_max = 3.0, 65536.0
    for _ in range(16):  # dichotomy, resol = 2**-n
        s_w = 0.5*(s_w_min + s_w_max)
        gamma = sigma_max * math.sqrt(s_w/s_x) / psd_max
        att = max(20.0, -20.0*math.log10(gamma))  # 20 is a minimal acceptable attenuation
        value = s_w*freq_res - 2.0 * alpha_to_band(att_to_alpha(att)) - 1.0
        if value <= 0:
            s_w_min = s_w
        else:
            s_w_max = s_w
    return s_w


def welch(signal: torch.Tensor, freq_res: typing.Optional[numbers.Real] = None) -> torch.Tensor:
    r"""Estimate the power spectral density (PSD) with the Welch method.

    Terminology
    -----------
    * :math:`s_x` is the number of samples in the signal.
    * :math:`s_w` is the number of samples in the dpss window.
    * :math:`r` is the frequency resolution in Hz, for a sample rate of 1.
    * :math:`\sigma(f)` is an estimation of the std of the psd.
    * :math:`psd(f)` is the power spectral density.
    * :math:`n_{psd}(f)` is the psd noise, ignoring gibbs effects.
    * :math:`n_{win}` is the additive noise created by the gibbs effect of the window.
    * :math:`\gamma` is the maximum amplitude of the largest of the window's secondary lobs.
    * :math:`\alpha` is the window theorical standardized half bandwidth.
    * :math:`\beta` is the window experimental standardized half bandwidth.

    Equations
    ---------
    There, the equation to find the optimal windows size:

    .. math::

        \begin{cases}
            n_{psd}(f) = \sigma(f) . \sqrt{\frac{s_w}{s_x}} & \text{std of mean estimator} \\
            n_{win} = \max\left(psd(f)\right) . \gamma & \text{because convolution}\\
            \gamma = g(\alpha) \\
            \beta = \alpha + \epsilon = h(\alpha) \\
            r = \frac{1}{s_w} + 2 . \frac{\beta}{s_w} & \text{convolution main lob} \\
        \end{cases}

    To avoid having a too big gibbs noise, we want :math:`n_{win} < n_{psd}(f)`.

    .. math::

        \Leftrightarrow \begin{cases}
            psd_{max} . \gamma  < \sigma_{max} . \sqrt{\frac{s_w}{s_x}} \\
            r . s_w = 1 + 2.h(g^{-1}(\gamma)) \\
        \end{cases} \Leftrightarrow
            s_w . r - 2 . h\left(
                g^{-1}\left(\frac{\sigma_{max} . \sqrt{\frac{s_w}{s_x}}}{psd_{max}}\right)
            \right) - 1 > 0


    Parameters
    ----------
    signal : torch.Tensor
        The stationary signal on witch we evaluate the PSD.
        The tensor can be batched, so the shape is (..., n).
    freq_res : float
        The normlised frequency resolution in Hz (:math:`r \in \left]0, \frac{1}{2}\right[`),
        for a sample rate of 1.
        Higher it is, better is the frequency resolution but noiser it is.

    Returns
    -------
    psd : torch.Tensor
        An estimation of the power spectral density, of shape (..., m).

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.signal.psd import welch
    >>> signal = torch.randn((16, 2, 768000))  # 16 stereos signals
    >>> psd = welch(signal, 1/4800)
    >>>
    >>> # freq = torch.fft.rfftfreq(2*psd.shape[-1]-1, 1/48000)
    >>> # import matplotlib.pyplot as plt
    >>> # _ = plt.plot(freq, psd[0].T)
    >>> # plt.show()
    >>>
    """
    assert isinstance(signal, torch.Tensor), signal.__class__.__name__
    assert signal.shape[-1] >= 32, "the signal is to short, please provide more samples"

    # The first step consists in having a fast and inaccurate estimation of the psd.
    win_len = min(4096, signal.shape[-1]//3)
    win = torch.hann_window(win_len, periodic=False, dtype=signal.dtype, device=signal.device)
    std, psd = _compute_psd(signal, win, win_len//2, return_std=True)

    # Get a frequency resolution.
    if freq_res is None:
        freq_res = max(1.0 / win_len, 10.0 / 48000)
    else:
        assert isinstance(freq_res, numbers.Real), freq_res.__class__.__name__
        assert 0 < freq_res < 0.5, freq_res
        freq_res = float(freq_res)

    # The second step constists in finding the best windows size.
    # According to the inequality specified in the docstring.
    win_len = math.ceil(_find_len(signal.shape[-1], float(std.max()), float(psd.max()), freq_res))
    win_len = min(win_len, signal.shape[-1])

    # The fird step consists in deducing alpha
    # according the frequency accuracy expression in the doctring.
    alpha = band_to_alpha(0.5 * (freq_res * win_len - 1))

    # compute the psd
    win = dpss(win_len, alpha, dtype=signal.dtype)
    psd = _compute_psd(signal, win, win_len//4, return_std=False)  # //4 is arbitrary overlapp

    return psd
