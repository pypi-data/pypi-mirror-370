"""
audio.py
========
Minimal wrapper around the `sounddevice` library to play a
float32 stereo NumPy buffer (−1 … +1).

The import is kept local to avoid adding latency to users who
only need signal generation or plotting.
"""


from __future__ import annotations

import contextlib
from typing import Optional

import numpy as np
import sounddevice as sd

__all__ = ["play_buffer"]

# ---------------------------------------------------------------------
# Module-level cache for the output stream
# ---------------------------------------------------------------------
_stream: Optional[sd.OutputStream] = None


def _get_stream(samplerate: int) -> sd.OutputStream:
    """Return a persistent OutputStream at the requested samplerate."""
    global _stream

    # Re-create the stream if none exists or sr has changed
    if _stream is None or _stream.samplerate != samplerate:
        with contextlib.suppress(Exception):
            if _stream is not None:
                _stream.close()

        _stream = sd.OutputStream(
            samplerate=samplerate,
            channels=2,
            dtype="float32",
            blocksize=0,            # let PortAudio choose the buffer size
            finished_callback=lambda: None,
        )
        _stream.start()

    return _stream


def play_buffer(buffer: np.ndarray, sr: int) -> None:
    """
    Play *buffer* on a loop until KeyboardInterrupt.

    Parameters
    ----------
    buffer : np.ndarray, shape (n_samples, 2), dtype float32
        Stereo audio data in the range −1…+1.
    sr : int
        Sample rate in samples/s.
    """
    if buffer.ndim != 2 or buffer.shape[1] != 2:
        raise ValueError("Audio buffer must have shape (n_samples, 2).")
    if buffer.dtype != np.float32:
        raise ValueError("Audio buffer must be float32.")

    stream = _get_stream(sr)

    try:
        while True:                # loop indefinitely
            stream.write(buffer)
    except KeyboardInterrupt:
        # Stop current playback but keep the stream open for the next call
        stream.abort(ignore_errors=True)
