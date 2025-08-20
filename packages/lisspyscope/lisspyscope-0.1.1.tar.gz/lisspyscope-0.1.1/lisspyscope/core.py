"""
core.py
=======

Generate, play, plot, and save stereo tones whose x-y trace on an
oscilloscope forms a Lissajous figure.  The default parameters produce
a perfect circle (1 : 1 frequency ratio, 90° phase).

Only NumPy is imported at module load; heavier libraries are imported
lazily inside the specific helper that needs them.
"""


from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np

# ---------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------
DEFAULT_BASE_FREQ = 1000.0       # Hz  (Base frequency)
DEFAULT_R_FACT = 1               # right = r_fact × base
DEFAULT_L_FACT = 1               # left  = l_fact x base   
DEFAULT_PHASE_DEG = 90.0         # degrees   (circle)
DEFAULT_SR = 48_000              # samples/s


# ---------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------
def _lcm(a: int, b: int) -> int:
    """Least common multiple via Euclid’s algorithm."""
    from math import gcd
    return abs(a * b) // gcd(a, b)


def _auto_duration(base_freq: float, l_fact: int, r_fact: int) -> float:
    """Shortest time that closes the figure (in seconds)."""
    return _lcm(l_fact, r_fact) / base_freq


def _validate(base_freq: float, l_fact: int, r_fact: int, sr: int) -> None:
    if base_freq <= 0:
        raise ValueError("base_freq must be positive.")
    if l_fact <= 0 or not isinstance(l_fact, int):
        raise ValueError("l_fact must be a positive integer.")
    if r_fact <= 0 or not isinstance(r_fact, int):
        raise ValueError("r_fact must be a positive integer.")
    if sr <= 0:
        raise ValueError("sample rate must be positive.")


# ---------------------------------------------------------------------
# Core generator
# ---------------------------------------------------------------------
def generate_lissajous(
    base_freq: float = DEFAULT_BASE_FREQ,
    l_fact: int = DEFAULT_L_FACT,
    r_fact: int = DEFAULT_L_FACT,
    phase_deg: float = DEFAULT_PHASE_DEG,
    sr: int = DEFAULT_SR,
) -> Tuple[np.ndarray, int]:
    """
    Return a float32 stereo buffer whose oscilloscope trace is a
    closed Lissajous figure.

    Parameters
    ----------
    base_freq : float  (Hz)
    l_fact    : int   (left = l_fact × base_freq)
    r_fact    : int   (right = r_fact × base_freq) 
    phase_deg : float  (degrees)
    sr        : int    (sample rate in samples/s)

    The duration is computed automatically; users cannot override it.
    """
    _validate(base_freq, l_fact, r_fact, sr)

    f_left = base_freq * l_fact
    f_right = base_freq * r_fact
    phase = np.deg2rad(phase_deg)
    duration = _auto_duration(base_freq, l_fact, r_fact)

    t = np.linspace(0.0, duration, int(sr * duration), endpoint=False, dtype=np.float32)

    left = np.sin(2.0 * np.pi * f_left * t, dtype=np.float32)
    right = np.sin(2.0 * np.pi * f_right * t + phase, dtype=np.float32)

    buffer = np.column_stack((left, right))
    np.clip(buffer, -1.0, 1.0, out=buffer)   # hard safety limit
    return buffer, sr


# ---------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------
def play_lissajous(
    base_freq: float = DEFAULT_BASE_FREQ,
    l_fact: int = DEFAULT_L_FACT,
    r_fact: int = DEFAULT_R_FACT,
    phase_deg: float = DEFAULT_PHASE_DEG,
    sr: int = DEFAULT_SR,
) -> None:
    """Generate the buffer and play it (blocking)."""
    buffer, sr = generate_lissajous(base_freq, l_fact, r_fact, phase_deg, sr)
    from .audio import play_buffer
    play_buffer(buffer, sr)


def plot_lissajous(
    base_freq: float = DEFAULT_BASE_FREQ,
    l_fact: int = DEFAULT_L_FACT,
    r_fact: int = DEFAULT_R_FACT,
    phase_deg: float = DEFAULT_PHASE_DEG,
    sr: int = DEFAULT_SR,
) -> None:
    """Plot the figure. Requires matplotlib."""
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:
        raise ImportError(
            "Plotting requires matplotlib → pip install lisspyscope[plot]"
        ) from exc

    buffer, _ = generate_lissajous(base_freq, l_fact, r_fact, phase_deg, sr)
    double_buf = np.vstack([buffer, buffer])
    x, y = double_buf.T
    plt.plot(x, y, lw=0.8)
    plt.title(
    rf"Lissajous: $f_L={base_freq*l_fact:.0f}\,\text{{Hz}}$, "
    rf"$f_R={base_freq*r_fact:.0f}\,\text{{Hz}}$, "
    rf"$\varphi={phase_deg:.1f}^\circ$"
)
    plt.axis("equal")
    plt.xlabel("Left channel")
    plt.ylabel("Right channel")
    plt.grid(ls=":")
    plt.show()


