"""
lisspyscope
===========

A tiny helper package for creating stereo tones that turn into
Lissajous figures on an oscilloscope.

Public API
----------
generate_lissajous
play_lissajous
plot_lissajous           
"""
from .core import (
    generate_lissajous,
    play_lissajous,
    plot_lissajous,
)

__all__ = [
    "generate_lissajous",
    "play_lissajous",
    "plot_lissajous",
]

__version__ = "0.1.1"

